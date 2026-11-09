"""Audit local weight-count evidence and explicitly review model-card updates."""
import argparse
from datetime import datetime
import difflib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import tempfile

from .weights import REPO, ROOT, asset_signature, select_assets, unsupported_reason
from .weight_worker import VERSION
from .weight_guide import Cancelled, choose, confirm, require_terminal

KINDS = {"stored_parameters", "tensor_elements"}


def read_reports(paths):
    """Use report timestamps, never filesystem mtimes or aggregate summaries."""
    latest = {}
    for path in sorted(set(paths)):
        report = json.loads(path.read_text())
        if report.get("schema_version") != 1:
            continue
        when = datetime.fromisoformat(report["created_at"])
        if when.tzinfo is None:
            raise ValueError(f"{path}: report timestamp needs a timezone")
        for result in report["results"]:
            key = (result["model"], result["asset"])
            if key not in latest or when > latest[key][0]:
                latest[key] = (when, result, path)
            elif when == latest[key][0] and result != latest[key][1]:
                raise ValueError(f"Conflicting simultaneous reports for {key}; select --report explicitly")
    return latest


def evidence_problem(asset, result):
    if result.get("status") != "ok":
        return result.get("reason") or result.get("status", "Missing status")
    if result.get("inspection_version") != VERSION:
        return "Inspector version changed; inspect again"
    if result.get("asset_signature") != asset_signature(asset) or result.get("source_url") != asset.get("url"):
        return "Asset identity changed or was not recorded; inspect again"
    sha = result.get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        return "Missing checkpoint SHA-256; inspect again"
    if asset.get("sha256") and asset["sha256"].lower() != sha:
        return "Checkpoint checksum differs from model card; inspect again"
    if result.get("method") not in {"pickle_tensor_metadata", "legacy_restricted_loader"}:
        return "Unknown inspection method; inspect again"
    if not result.get("candidates"):
        return "No candidate counts; inspect again"
    return None


def proposed_count(asset, evidence, container):
    when, result, _ = evidence
    if problem := evidence_problem(asset, result):
        raise ValueError(problem)
    candidates = [c for c in result["candidates"] if c.get("container") == container]
    if len(candidates) != 1:
        raise ValueError(f"Choose one unique candidate container: {container!r}")
    candidate = candidates[0]
    value, kind = candidate.get("tensor_elements"), candidate.get("kind")
    if type(value) is not int or value < 0 or kind not in KINDS:
        raise ValueError("Invalid count or count scope; inspect again")
    return {"value": value, "kind": kind, "sha256": result["sha256"],
            "asset_signature": result["asset_signature"], "container": container,
            "method": result["method"], "inspection_version": VERSION,
            "observed_at": when.isoformat()}


def catalogue(repo, models):
    selected = select_assets(repo, models)
    index = {}
    for item in selected:
        key = (item["model"], item["asset"].get("key"))
        if key in index:
            raise ValueError(f"Duplicate asset key: {key}")
        index[key] = item["asset"]
    return index


def audit(assets, evidence):
    rows = []
    for key, asset in assets.items():
        saved = asset.get("weight_count")
        saved_current = bool(isinstance(saved, dict) and saved.get("asset_signature") == asset_signature(asset)
                             and saved.get("inspection_version") == VERSION)
        row = {"model": key[0], "asset": key[1], "stored_count": saved,
               "stored_status": "current" if saved_current else "stale" if saved else "missing",
               "eligible": unsupported_reason(asset) is None, "proposals": []}
        found = evidence.get(key)
        if found:
            row["report"] = str(found[2])
            row["reason"] = evidence_problem(asset, found[1])
            row["status"] = "pending" if row["reason"] is None else found[1].get("status", "unresolved")
            if row["reason"] and row["status"] == "ok":
                row["status"] = "stale"
            if row["reason"] is None:
                try:
                    for candidate in found[1]["candidates"]:
                        count = proposed_count(asset, found, candidate["container"])
                        # A new inspection date alone need not churn tracked evidence.
                        same = saved and all(saved.get(k) == v for k, v in count.items() if k != "observed_at")
                        row["proposals"].append({"selector": "/".join((*key, candidate["container"])),
                                                 "action": "UNCHANGED" if same else "REPLACE" if saved else "ADD",
                                                 "weight_count": count})
                except (KeyError, ValueError) as error:
                    row.update(status="unresolved", reason=str(error), proposals=[])
        else:
            row.update(status="unsupported" if unsupported_reason(asset) else "uninspected",
                       reason=unsupported_reason(asset) or "No local inspection report")
        if row["proposals"]:
            row["next_step"] = "Review a candidate, then apply its explicit selector"
        elif row["eligible"]:
            row["next_step"] = "inspect-weights --model " + shlex.quote(key[0]) + " --asset " + shlex.quote(key[1])
        else:
            row["next_step"] = "Provide a direct unsharded PyTorch file asset, or inspect manually"
        rows.append(row)
    return rows


def coverage_state(row):
    # One action per eligible asset; newer evidence takes precedence over a
    # saved count, so replacements are not hidden behind existing coverage.
    if any(p["action"] != "UNCHANGED" for p in row["proposals"]):
        return "Review"
    if row["stored_status"] == "current":
        return "Saved"
    if row["status"] == "stale" or row["stored_status"] == "stale":
        return "Refresh"
    if row["status"] in {"failed", "unresolved", "unsupported"}:
        return "Blocked"
    return "Inspect"


def print_coverage(rows, args):
    eligible = [r for r in rows if r["eligible"]]
    models = {r["model"] for r in rows}
    supported_models = {r["model"] for r in eligible}
    saved = sum(r["stored_status"] == "current" for r in eligible)
    ready = sum(bool(r["proposals"]) for r in eligible)
    print(f"Weight-count coverage: {len(models)} models, {len(eligible)} directly inspectable PyTorch assets")
    print(f"  In model cards: {saved}/{len(eligible)} assets have current saved counts")
    print(f"  Local evidence: {ready}/{len(eligible)} assets have usable inspection results")
    print("  Local results are pending review; coverage does not download or edit anything.")
    if eligible:
        columns = ("Saved", "Review", "Refresh", "Inspect", "Blocked")
        width = max(len("Model"), *(len(m) for m in supported_models))
        print("\n" + f"{'Model':<{width}}  " + "  ".join(f"{c:>7}" for c in columns))
        for model in sorted(supported_models):
            states = [coverage_state(r) for r in eligible if r["model"] == model]
            print(f"{model:<{width}}  " + "  ".join(f"{states.count(c):>7}" for c in columns))
        print("\nAssets by next action (each asset appears once):")
        print("  Saved: no update pending; Review: new local count awaiting approval.")
        print("  Refresh: evidence/card identity or inspector version changed; inspect again.")
        print("  Inspect: no local evidence; Blocked: last inspection could not produce a usable count.")
    outside = sum(r["asset"] is not None and not r["eligible"] for r in rows)
    print(f"\nOutside direct inspection: {outside} other assets; "
          f"{len(models - supported_models)} models have no directly inspectable asset.")
    print("  Includes other formats, repository/download pages and missing weight links.")
    print("  Use --details for asset names and reasons, or --model MODEL to narrow the view.")

    # Preserve the selected checkout/evidence when suggesting runnable commands.
    options = []
    if args.repo != REPO:
        options += ["--repo", str(args.repo)]
    review_options = options.copy()
    for model in args.model or []:
        review_options += ["--model", model]
    if args.report:
        for path in args.report:
            review_options += ["--report", str(path)]
    elif args.run_root != ROOT / "runs/weights":
        review_options += ["--run-root", str(args.run_root)]
    print("\nNext steps (run from the repository root):")
    prefix = ["uv", "run", "--locked", "--project", "src/probe"]
    pending = next((r for r in eligible if coverage_state(r) == "Review"), None)
    if pending:
        print("  Review local results interactively: " + shlex.join(prefix + ["review-pending-weights", "--guide"] + review_options))
    target = next((r for r in eligible if coverage_state(r) in {"Refresh", "Inspect", "Blocked"}), None)
    if target:
        print("  Choose weights to inspect (may download): " + shlex.join(prefix + ["inspect-weights", "--guide"] + options))
    if not pending and not target:
        print("  No eligible assets need action." if eligible else "  Add a direct PyTorch weight link to inspect a model.")


def print_details(rows, proposals=False):
    for row in rows:
        name = f"{row['model']}/{row['asset']}" if row["asset"] is not None else row["model"] + " (no assets)"
        print(f"{name}\tstored={row['stored_status']}\t{row['status']}\t{row.get('reason') or ''}")
        print("  " + row["next_step"])
        if proposals:
            for proposal in row["proposals"]:
                count = proposal["weight_count"]
                print(f"  {proposal['action']} {proposal['selector']}: {count['value']:,} {count['kind']}")


def prepare_changes(repo, assets, evidence, accepts, removes):
    import tomlkit

    edits = {}
    for selector in accepts:
        parts = selector.split("/", 2)
        if len(parts) != 3:
            raise ValueError("--accept requires MODEL/ASSET/CONTAINER")
        key = tuple(parts[:2])
        if key not in assets or key not in evidence:
            raise ValueError(f"No local evidence for {selector}")
        if key in edits:
            raise ValueError(f"Asset selected more than once: {selector}")
        edits[key] = proposed_count(assets[key], evidence[key], parts[2])
    for selector in removes:
        key = tuple(selector.split("/"))
        if key not in assets or not assets[key].get("weight_count"):
            raise ValueError(f"No stored count to remove: {selector}")
        if key in edits:
            raise ValueError(f"Asset selected more than once: {selector}")
        edits[key] = None
    changes, actions = {}, []
    for model in sorted({key[0] for key in edits}):
        path = repo / "content/models" / model / "index.md"
        if path.is_symlink() or not path.resolve().is_relative_to(repo.resolve()):
            raise ValueError(f"Refusing model-card path outside checkout or symlink: {path}")
        before = path.read_bytes()
        parts = before.decode().split("+++", 2)
        document = tomlkit.parse(parts[1])
        for asset in document["assets"]:
            key = (model, asset["key"])
            if key not in edits:
                continue
            value = edits[key]
            old = asset.get("weight_count")
            if dict(asset) != assets[key]:
                raise ValueError(f"Card changed while preparing {model}; retry")
            if value is None:
                del asset["weight_count"]
                action = "DELETE"
            else:
                if old and all(old.get(k) == v for k, v in value.items() if k != "observed_at"):
                    continue
                table = tomlkit.inline_table()
                table.update(value)
                asset["weight_count"] = table
                action = "REPLACE" if old is not None else "ADD"
            previous = f"{old['value']:,} {old['kind']}" if old else "no saved count"
            following = f"{value['value']:,} {value['kind']}" if value is not None else "no saved count"
            actions.append(f"{action} {'/'.join(key)}: {previous} -> {following}")
        after = (parts[0] + "+++" + tomlkit.dumps(document) + "+++" + parts[2]).encode()
        if before != after:
            changes[path] = (before, after)
    return changes, actions


def write_changes(changes):
    """Check all preimages first; atomically replace each card, roll back on error."""
    for path, (before, _) in changes.items():
        if path.is_symlink() or path.read_bytes() != before:
            raise ValueError(f"{path} changed during review; nothing written, retry")
    staged, written = {}, []
    try:
        for path, (_, after) in changes.items():
            fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".weight-count-")
            staged[path] = Path(temporary)
            with os.fdopen(fd, "wb") as out:
                out.write(after)
            os.chmod(temporary, path.stat().st_mode)
        for path, temporary in staged.items():
            os.replace(temporary, path)
            written.append(path)
    except Exception:
        for path in written:
            path.write_bytes(changes[path][0])
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def guide_review(args):
    require_terminal()
    print("Review local evidence, choose one count, then preview the exact card edit.")
    print("No downloads. Nothing is staged, committed or pushed. Enter or q cancels any selection.")
    while True:
        assets = catalogue(args.repo, args.model)
        paths = args.report if args.report is not None else list(args.run_root.glob("*/report.json"))
        evidence = read_reports(paths)
        rows = audit(assets, evidence)
        pending = [r for r in rows if any(args.show_all or p['action'] != 'UNCHANGED' for p in r['proposals'])]
        if not pending:
            print("No usable pending count changes in the selected local reports.")
            print("Use review-weights coverage to find missing/stale evidence, then inspect-weights --guide.")
            print("Use --show-all to include usable results that already match saved counts.")
            return 0
        models = sorted({r['model'] for r in pending})
        model = models[choose("1. Choose a model to review", [
            f"{m} ({sum(r['model'] == m for r in pending)} selectable assets)" for m in models])]
        candidates = [r for r in pending if r['model'] == model]
        row = candidates[choose("2. Choose an asset", [r['asset'] for r in candidates])]
        proposals = [p for p in row['proposals'] if args.show_all or p['action'] != 'UNCHANGED']
        proposal = proposals[choose("3. Choose one count (containers are never added together)", [
            f"{p['action']} {p['weight_count']['container']}: {p['weight_count']['value']:,} "
            f"{p['weight_count']['kind']}" for p in proposals])]
        count = proposal['weight_count']
        result = evidence[(model, row['asset'])][1]
        print(f"\nSource: {result['source_url']}\nReport: {row['report']}\nCheckpoint SHA-256: {count['sha256']}")
        print(f"Observed: {count['observed_at']}; method: {count['method']} (v{count['inspection_version']})")
        print("Tensor totals may include buffers. Stored parameters exclude module buffers.")
        print("Runtime-created parameters may be absent; runtime/trainable counts are unverified.")
        # The normal apply path performs validation, prints the complete diff,
        # and asks for confirmation. Use the exact report selected above.
        if proposal['action'] == 'UNCHANGED':
            print("This count already matches the model card; no edit is needed.")
            code = 0
        else:
            code = main(["apply", "--repo", str(args.repo), "--report", row['report'],
                         "--accept", proposal['selector']])
        if code:
            return code
        if not confirm("Review another asset?"):
            return 0


def pending_main():
    return main(["pending", *sys.argv[1:]])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("coverage", "pending", "apply"))
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--model", action="append")
    parser.add_argument("--run-root", type=Path, default=ROOT / "runs/weights")
    parser.add_argument("--report", type=Path, action="append", help="Use these reports instead of automatic local discovery")
    parser.add_argument("--output", type=Path, help="Write local coverage/proposal JSON")
    parser.add_argument("--details", action="store_true", help="Show every asset and reason in coverage")
    parser.add_argument("--guide", action="store_true", help="Guide pending review through selections, diff and confirmation")
    parser.add_argument("--show-all", action="store_true", help="With --guide, include usable results already saved in model cards")
    parser.add_argument("--accept", action="append", default=[], metavar="MODEL/ASSET/CONTAINER")
    parser.add_argument("--remove", action="append", default=[], metavar="MODEL/ASSET")
    args = parser.parse_args(argv)
    if args.show_all and not args.guide:
        parser.error("--show-all requires --guide")
    if args.guide and (args.command != "pending" or args.accept or args.remove or args.output or args.details):
        parser.error("--guide is for pending review; do not combine with --accept, --remove, --output or --details")
    if args.command == "coverage" and (args.accept or args.remove):
        parser.error("Use pending or apply for selected changes")
    if args.command == "apply" and not (args.accept or args.remove):
        parser.error("apply requires explicit --accept and/or --remove selectors")
    try:
        if args.guide:
            return guide_review(args)
        assets = catalogue(args.repo, args.model)
        paths = args.report if args.report is not None else list(args.run_root.glob("*/report.json"))
        evidence = read_reports(paths)
        rows = audit(assets, evidence)
        if args.command == "coverage":
            print_coverage(rows, args)
            if args.details:
                print("\nAsset details:")
                print_details(rows)
        elif not (args.accept or args.remove):
            print_details(rows, proposals=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps({"results": rows}, indent=2) + "\n")
        if args.accept or args.remove:
            changes, actions = prepare_changes(args.repo, assets, evidence, args.accept, args.remove)
            for action in actions:
                print(action)
            for path, (before, after) in changes.items():
                print("".join(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True),
                                                 fromfile=str(path), tofile=str(path))), end="")
            if args.command == "apply" and changes:
                if not sys.stdin.isatty():
                    raise ValueError("Confirmation requires an interactive terminal. Use pending to preview/manual edit.")
                if input("Apply these model-card edits locally? [y/N] ").strip().lower() != "y":
                    print("Cancelled; model cards unchanged.")
                    return 0
                write_changes(changes)
                print(f"Updated {len(changes)} model card(s). Review with git diff; nothing staged, committed or pushed.")
    except (Cancelled, EOFError, KeyboardInterrupt):
        print("\nReview stopped. Only previously confirmed edits, if any, were applied.")
        return 0
    except (ValueError, OSError, KeyError, IndexError, TypeError) as error:
        print(f"review-weights: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
