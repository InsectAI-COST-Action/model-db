"""Inspect linked PyTorch artifacts without importing author model code."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import tempfile
import tomllib
import urllib.parse
import urllib.request
import uuid
import zipfile

from .runner import digest, execute
from .weight_guide import Cancelled, choose, confirm, require_terminal

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
EXTENSIONS = {".pt", ".pth", ".bin", ".ckpt"}
SCOPE = ("Logical tensor elements in model data; optimizer and EMA branches are excluded. "
         "Serialized modules use registered parameters, excluding buffers. Plain state dictionaries "
         "may include buffers. Repeated references to a tensor count once per candidate; distinct views count separately. "
         "Runtime-created parameters may be absent; "
         "these are not verified runtime or trainable parameter counts.")


def asset_signature(asset):
    identity = {k: asset.get(k) for k in ("url", "filename", "revision", "sha256", "size_bytes")}
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def select_assets(repo, models=None, asset_key=None):
    cards = {p.parent.name: p for p in (repo / "content/models").glob("*/index.md")}
    if models and set(models) - cards.keys():
        raise ValueError("Unknown model(s): " + ", ".join(sorted(set(models) - cards.keys())))
    selected = []
    for model in sorted(set(models) if models else cards):
        card = tomllib.loads(cards[model].read_text().split("+++", 2)[1])
        assets = card.get("assets", [])
        if asset_key:
            assets = [a for a in assets if a.get("key") == asset_key]
            if not assets:
                raise ValueError(f"{model}: unknown asset {asset_key!r}")
        if not assets:
            selected.append({"model": model, "asset": {"key": None, "url": ""}})
        selected.extend({"model": model, "asset": a} for a in assets)
    return selected


def unsupported_reason(asset):
    url = urllib.parse.urlsplit(asset.get("url", ""))
    if url.scheme not in ("http", "https") or not url.netloc:
        return "No direct HTTP(S) weight URL"
    name = Path(asset.get("filename") or url.path).name
    if Path(name).suffix.lower() not in EXTENSIONS:
        return "Not a supported PyTorch weight file"
    if re.search(r"-\d+-of-\d+\.", name):
        return "Sharded checkpoints are not supported"
    if url.hostname == "huggingface.co" and "/resolve/" not in url.path:
        return "Hugging Face asset needs a direct resolve URL"
    if url.hostname in ("drive.google.com", "www.dropbox.com") or "/blob/" in url.path:
        return "Landing-page resolution is not supported"
    if url.path.lower().endswith((".zip", ".tar", ".gz", ".xz")):
        return "Archive extraction is not supported"
    return None


def download(asset, cache, max_bytes, network_timeout):
    """Bounded download; reuse only checksum-pinned or immutable Hub assets."""
    url = asset["url"]
    expected = asset.get("sha256")
    if expected and not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise ValueError("Invalid SHA-256 in asset metadata")
    expected = expected.lower() if expected else None
    if asset.get("size_bytes", 0) > max_bytes:
        raise ValueError("Declared file size exceeds byte limit")
    parsed = urllib.parse.urlsplit(url)
    immutable = expected or (parsed.hostname == "huggingface.co" and
                             re.search(r"/resolve/[0-9a-f]{40}/", parsed.path))
    key = hashlib.sha256(url.encode()).hexdigest()
    directory = cache / key
    directory.mkdir(parents=True, exist_ok=True)
    target, metadata = directory / "checkpoint", directory / "download.json"
    if immutable and target.is_file() and metadata.is_file():
        try:
            info = json.loads(metadata.read_text())
            if target.stat().st_size <= max_bytes and digest(target) == info["sha256"]:
                if not expected or info["sha256"] == expected:
                    return target, info
        except (ValueError, KeyError, OSError):
            pass
    fd, temporary = tempfile.mkstemp(dir=directory, suffix=".partial")
    try:
        with os.fdopen(fd, "wb") as output:
            request = urllib.request.Request(url, headers={"User-Agent": "model-db-weight-inspection/1"})
            with urllib.request.urlopen(request, timeout=network_timeout) as response:
                length = response.headers.get("Content-Length")
                if length and int(length) > max_bytes:
                    raise ValueError("Content-Length exceeds byte limit")
                size = 0
                sha = hashlib.sha256()
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > max_bytes:
                        raise ValueError("Download exceeds byte limit")
                    output.write(chunk)
                    sha.update(chunk)
                if length and size != int(length):
                    raise ValueError("Incomplete download")
                if expected and sha.hexdigest() != expected:
                    raise ValueError("SHA-256 mismatch")
                info = {"sha256": sha.hexdigest(), "size_bytes": size,
                        "resolved_url": response.geturl()}
        os.replace(temporary, target)
        meta_temp = directory / (uuid.uuid4().hex + ".json")
        meta_temp.write_text(json.dumps(info))
        os.replace(meta_temp, metadata)
        return target, info
    finally:
        Path(temporary).unlink(missing_ok=True)


def inspect_asset(selected, args, run):
    asset = selected["asset"]
    result = {"model": selected["model"], "asset": asset.get("key"),
              "asset_signature": asset_signature(asset),
              "source_url": asset.get("url"), "revision": asset.get("revision"),
              "runtime_parameter_count": None, "candidates": []}
    reason = unsupported_reason(asset)
    if reason:
        return dict(result, status="unsupported", reason=reason, eligible=False)
    result["eligible"] = True
    try:
        path, info = download(asset, args.cache, args.max_bytes, args.network_timeout)
        result.update(info)
        output = run / "result.json"
        worker = ROOT / "probe/weight_worker.py"
        command = ([sys.executable] if zipfile.is_zipfile(path) else
                   ["uv", "run", "--locked", "--project", str(ROOT / "environments/weights"), "python"])
        code = execute(
            command + [str(worker), str(path), str(output)],
            ROOT, os.environ.copy(), run / "worker.log", args.timeout,
        )
        if code != 0 or not output.is_file():
            raise RuntimeError(f"Inspection worker failed (exit {code}); see {run / 'worker.log'}")
        result.update(json.loads(output.read_text()))
    except Exception as error:
        result.update(status="failed", reason=f"{type(error).__name__}: {error}")
    return result


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def guide_selection(args):
    require_terminal()
    from .weight_review import audit, catalogue, coverage_state, read_reports

    assets = select_assets(args.repo)
    eligible = [s for s in assets if not unsupported_reason(s["asset"])]
    rows = audit(catalogue(args.repo, None), read_reports(list(args.run_root.glob("*/report.json"))))
    states = {(r['model'], r['asset']): coverage_state(r) for r in rows}
    if not args.show_all:
        eligible = [s for s in eligible if states[(s['model'], s['asset']['key'])] in {'Inspect', 'Refresh', 'Blocked'}]
    models = sorted({s["model"] for s in eligible})
    if not models:
        print("No PyTorch assets need inspection in this view. Use --show-all to include saved counts and pending reviews.")
        return []
    print("Inspection saves local results only; it does not update model cards.")
    print("Only models with direct PyTorch file links are listed.")
    print("Showing all eligible assets." if args.show_all else
          "Showing Inspect, Refresh and Blocked assets only; use --show-all to include Review and Saved.")
    model = models[choose("1. Choose a model", [
        f"{m} ({sum(s['model'] == m for s in eligible)} PyTorch assets)" for m in models])]
    candidates = [s for s in eligible if s["model"] == model]
    labels = [f"{s['asset']['key']} [{states[(s['model'], s['asset']['key'])]}] — {s['asset']['url']}" for s in candidates]
    if len(candidates) > 1:
        labels.append(f"All {len(candidates)} listed PyTorch assets for {model}")
    selected = choose("2. Choose weights to inspect", labels)
    chosen = candidates if selected == len(candidates) else [candidates[selected]]
    print("\n3. Confirm inspection")
    for item in chosen:
        print(f"  {item['model']}/{item['asset']['key']}: {item['asset']['url']}")
    print(f"Downloads may be required. Limit: {args.max_bytes:,} bytes per artifact; "
          f"network timeout: {args.network_timeout}s; inspection timeout: {args.timeout}s.")
    if not confirm("Inspect these assets?"):
        raise Cancelled()
    return chosen


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--model", action="append", help="Model id; repeat to select several")
    selection.add_argument("--all", action="store_true", help="Select all catalogue assets")
    selection.add_argument("--guide", action="store_true", help="Choose a model and weights interactively")
    parser.add_argument("--asset", help="Asset key within one selected model")
    parser.add_argument("--show-all", action="store_true", help="With --guide, include assets already reviewed or awaiting review")
    parser.add_argument("--list", action="store_true", help="List eligibility without downloading")
    parser.add_argument("--output", type=Path, help="Write JSON report to this path")
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache/weights")
    parser.add_argument("--run-root", type=Path, default=ROOT / "runs/weights")
    parser.add_argument("--max-bytes", type=positive, default=2 * 1024**3)
    parser.add_argument("--network-timeout", type=positive, default=60)
    parser.add_argument("--timeout", type=positive, default=300, help="Worker timeout, including environment setup")
    args = parser.parse_args(argv)
    if args.show_all and not args.guide:
        parser.error("--show-all requires --guide")
    if args.guide and args.list:
        parser.error("--guide performs selected inspections; use --all --list for a read-only list")
    if args.asset and (not args.model or len(args.model) != 1):
        parser.error("--asset requires exactly one --model")
    try:
        assets = guide_selection(args) if args.guide else select_assets(args.repo, args.model, args.asset)
        if args.guide and not assets:
            return 0
    except (Cancelled, EOFError, KeyboardInterrupt):
        print("\nCancelled; no inspection started.")
        return 0
    except (ValueError, OSError, IndexError) as error:
        parser.error(str(error))
    if args.list:
        results = [dict(model=s["model"], asset=s["asset"].get("key"),
                        source_url=s["asset"].get("url"),
                        status="unsupported" if unsupported_reason(s["asset"]) else "eligible",
                        reason=unsupported_reason(s["asset"])) for s in assets]
    else:
        run = args.run_root / uuid.uuid4().hex
        run.mkdir(parents=True)
        results = []
        for i, selected in enumerate(assets):
            job = run / str(i)
            job.mkdir()
            results.append(inspect_asset(selected, args, job))
    report = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
              "scope": SCOPE, "results": results}
    for r in results:
        counts = ", ".join(f"{c['container']}={c['tensor_elements']:,}" for c in r.get("candidates", []))
        print(f"{r['model']}/{r['asset']}\t{r['status']}\t{counts or r.get('reason') or '-'}")
    if not args.list:
        print(SCOPE)
        (run / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(f"Report: {run / 'report.json'}")
        if args.guide:
            print("Review these local results next:\n  " + shlex.join([
                "uv", "run", "--locked", "--project", "src/probe", "review-pending-weights",
                "--guide", "--repo", str(args.repo), "--report", str(run / "report.json")]))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    return int(any(r.get("eligible") and r["status"] != "ok" for r in results))


if __name__ == "__main__":
    sys.exit(main())
