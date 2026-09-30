"""Dependency-free coordinator. Model packages run only in child environments."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import time
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(resource, cache):
    """Content-addressed downloads; a failed download never becomes a cache hit."""
    expected = resource["sha256"]
    target = cache / expected / resource["filename"]
    if target.exists() and digest(target) == expected:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".partial")
    try:
        request = urllib.request.Request(
            resource["url"], headers={"User-Agent": "model-db-probe/0.1"}
        )
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            partial.open("wb") as f,
        ):
            size = 0
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > resource.get("max_bytes", 600_000_000):
                    raise ValueError("Download exceeds resource byte limit")
                f.write(chunk)
        if digest(partial) != expected:
            raise ValueError("Resource SHA-256 mismatch: " + resource["url"])
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)
    return target


def unpack(archive, target):
    """Extract source ZIPs with no traversal or symlink entries."""
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            destination = (target / item.filename).resolve()
            if not destination.is_relative_to(target.resolve()):
                raise ValueError("Unsafe archive path")
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Archive symlink is not supported")
        z.extractall(target)
    roots = list(target.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError("Expected a single source directory")
    return roots[0]


def execute(command, cwd, env, log, timeout):
    with log.open("w") as output:
        proc = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            return proc.wait(timeout=timeout)
        except BaseException as exc:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            if isinstance(exc, subprocess.TimeoutExpired):
                raise TimeoutError(
                    f"Probe exceeded {timeout}s; child process group terminated"
                ) from exc
            raise


def run_job(job, resources, run_root, cache, timeout):
    folder = run_root / job["id"]
    folder.mkdir(parents=True, exist_ok=False)
    report = {
        "schema_version": 1,
        "probe": job["id"],
        "model": job["model"],
        "variant": job.get("variant"),
        "capability": "output_format",
        "author_sources": job["author_sources"],
        "status": "blocked",
        "scope": job["scope"],
        "job": job,
        "probe_code": {
            name: digest(ROOT / "probe" / name) for name in ["runner.py", "worker.py"]
        },
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        if job.get("blocked"):
            report["reason"] = job["blocked"]
            return report
        paths = {}
        report["resources"] = {}
        for role, key in job["resources"].items():
            asset = resources[key]
            local = fetch(asset, cache)
            report["resources"][role] = {"url": asset["url"], "sha256": digest(local)}
            paths[role] = str(
                unpack(local, folder / role) if asset.get("archive") else local
            )
        profile = ROOT / "environments" / job["environment"]
        report["environment_lock_sha256"] = digest(profile / "uv.lock")
        request = {**job, "paths": paths, "output": str(folder / "artifacts")}
        (folder / "request.json").write_text(json.dumps(request, indent=2) + "\n")
        command = [
            "uv",
            "run",
            "--locked",
            "--project",
            str(profile),
            "python",
            str(ROOT / "probe" / "worker.py"),
            str(folder / "request.json"),
        ]
        report["command"] = command
        for role, path in paths.items():
            if role.startswith("torch-cache:"):
                name = role.removeprefix("torch-cache:")
                if Path(name).name != name:
                    raise ValueError("Invalid Torch cache filename")
                target = folder / "torch" / "hub" / "checkpoints" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        for directory in ["config", "torch", "matplotlib"]:
            (folder / directory).mkdir(exist_ok=True)
        env = dict(os.environ)
        env.pop("VIRTUAL_ENV", None)
        env.pop("PYTHONPATH", None)
        env.update(
            {
                "OMP_NUM_THREADS": "2",
                "MKL_NUM_THREADS": "2",
                "OPENBLAS_NUM_THREADS": "2",
                "CUDA_VISIBLE_DEVICES": "",
                "YOLO_AUTOINSTALL": "false",
                "YOLO_OFFLINE": "true",
                "YOLO_CONFIG_DIR": str(folder / "config"),
                "TORCH_HOME": str(folder / "torch"),
                "MPLCONFIGDIR": str(folder / "matplotlib"),
                "PYTHONNOUSERSITE": "1",
            }
        )
        code = execute(command, folder, env, folder / "run.log", timeout)
        report["exit_code"] = code
        observed = folder / "artifacts" / "observed.json"
        if code != 0 or not observed.exists():
            report["status"] = "failed"
            report["reason"] = (
                "Worker failed; see run.log. No format assignment is justified."
            )
        else:
            report["observation"] = json.loads(observed.read_text())
            report["status"] = report["observation"].pop("status")
        report["artifacts"] = [
            {
                "path": str(p.relative_to(folder)),
                "sha256": digest(p),
                "bytes": p.stat().st_size,
            }
            for p in sorted((folder / "artifacts").rglob("*"))
            if p.is_file()
        ]
    except Exception as exc:
        report["status"] = "failed"
        report["reason"] = f"{type(exc).__name__}: {exc}"
    finally:
        report["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["list", "run"])
    parser.add_argument("ids", nargs="*", help="Probe IDs; run requires IDs or --all")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--run-root", type=Path, default=ROOT / "runs")
    args = parser.parse_args()
    jobs = json.loads((ROOT / "models.json").read_text())
    if args.action == "list":
        for job in jobs:
            print(f"{job['id']:32} {job.get('blocked', job['scope'])}")
        return
    if not args.all and not args.ids:
        parser.error("Choose IDs or --all; listing does not install model packages")
    unknown = set(args.ids) - {j["id"] for j in jobs}
    if unknown:
        parser.error("Unknown probe IDs: " + ", ".join(sorted(unknown)))
    resources = json.loads((ROOT / "resources.json").read_text())
    run_root = args.run_root.resolve() / (
        time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    )
    run_root.mkdir(parents=True)
    print(f"Reports: {run_root}", flush=True)
    reports = []
    for job in jobs:
        if args.all or job["id"] in args.ids:
            print("Running " + job["id"], flush=True)
            report = run_job(job, resources, run_root, ROOT / ".cache", args.timeout)
            reports.append(report)
            print(job["id"] + ": " + report["status"], flush=True)
    (run_root / "summary.json").write_text(json.dumps(reports, indent=2) + "\n")
    raise SystemExit(0 if all(r["status"] == "observed" for r in reports) else 1)
