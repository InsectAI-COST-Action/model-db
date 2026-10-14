# Model probes and weight counts

Run commands from the repository root with [uv](https://docs.astral.sh/uv/)
installed. `uv` manages Python and the locked environments.

## Get and review weight counts

```bash
# 1. See what is saved, awaiting review, or still missing.
uv run --locked --project src/probe review-weights coverage

# 2. Choose models/weights to inspect and confirm any downloads.
uv run --locked --project src/probe inspect-weights --guide

# 3. Choose local results, review the diff, and confirm card edits.
uv run --locked --project src/probe review-pending-weights --guide

# 4. Check your changes before committing them yourself.
git diff -- content/models
```

Guides show only assets needing that step; add `--show-all` to revisit others.
Enter or `q` cancels a selection; confirmation defaults to **no**. Inspections
save local reports, not model-card edits. Only confirmed reviews edit cards;
nothing stages, commits, or pushes changes. Earlier confirmed edits remain if
you cancel later.

Counts describe saved tensors, not verified runtime/trainable parameters.
State-dictionary totals may include buffers; serialized-module counts exclude
them. Reports and downloads stay in ignored `src/probe/runs/` and
`src/probe/.cache/` directories.

## Check a model's output format

```bash
uv run --locked --project src/probe probe-models list
uv run --locked --project src/probe probe-models run arthronat
```

Read the report at the printed path before updating an output-format claim.
These probes run reviewed author code with real weights; their environments
isolate dependencies, not filesystem/network access. They check output formats,
not accuracy or speed. See the [detection coverage audit](reports/2026-09-30-format-expansion/README.md).

## Documentation

Prefix every command below with `uv run --locked --project src/probe`.
All commands accept `-h` / `--help`. Paths supplied as flags are relative to your
working directory; defaults refer to this checkout. Guides require a terminal.

### `inspect-weights`

| Command | What it does |
| --- | --- |
| `inspect-weights` | Inspects selected direct HTTP(S) `.pt`, `.pth`, `.bin`, or `.ckpt` assets without importing author code. ZIP checkpoints use inert tensor metadata; legacy files use restricted PyTorch loading in a locked CPU environment. Records counts, containers, hashes and failures locally. Continues after failures; exits nonzero when an eligible inspection fails or is unresolved. `--list` only lists eligibility. |

| Flag | Function and options | Default |
| --- | --- | --- |
| `--guide` | Choose model → asset(s) → confirm inspection. Shows Inspect, Refresh and Blocked assets. | Off; exactly one of `--guide`, `--model`, `--all` is required. |
| `--show-all` | Include Review/Saved assets in the guide; requires `--guide`. | Off. |
| `--model ID` | Select a model-card directory name; repeat for several models. | No selection. |
| `--all` | Select every catalogue asset; unsupported links remain visible in reports. | Off. |
| `--asset KEY` | Restrict to one asset; requires exactly one `--model`. | All assets in selected models. |
| `--list` | List eligibility without downloads; incompatible with `--guide`. | Off. |
| `--repo PATH` | Catalogue checkout to read. | This repository. |
| `--cache PATH` | Download cache; checksums are verified. Only checksum-pinned or immutable Hub URLs reuse cached files. | `src/probe/.cache/weights`. |
| `--run-root PATH` | Store reports/logs here; the guide also reads its existing reports to filter choices. | `src/probe/runs/weights`. |
| `--output PATH` | Write an additional JSON report (also works with `--list`). | No additional copy. |
| `--max-bytes N` | Positive per-artifact download limit in bytes. | `2147483648` (2 GiB). |
| `--network-timeout N` | Positive network socket timeout in seconds. | `60`. |
| `--timeout N` | Positive inspection-worker timeout in seconds, including environment setup. | `300`. |

Optimizer, EMA, scheduler and scaler branches are excluded. Repeated references
to one tensor count once per candidate; distinct views count separately.
Multiple containers are reported separately, never summed. Runtime-created
parameters may be absent. Archives, shards, TorchScript, landing pages and
unknown tensor encodings are unsupported; loading never retries unrestricted.

### `review-weights`

| Command | What it does |
| --- | --- |
| `review-weights coverage` | Read-only summary of saved counts and local evidence. Saved = no pending update; Review = pending count; Refresh = stale evidence/identity; Inspect = no evidence; Blocked = unsuccessful inspection. Counts refer to directly inspectable PyTorch assets; other assets are summarized separately. |
| `review-weights pending` | Show local count proposals, or preview selected additions/replacements/deletions without editing cards. `--guide` also offers confirmed application. |
| `review-weights apply` | Validate explicit selections, show the exact diff and ask for interactive confirmation before editing cards. Requires `--accept` and/or `--remove`. Failed/missing evidence never deletes a count automatically. |

| Flag | Function and options | Default |
| --- | --- | --- |
| `--model ID` | Limit to a model; repeat for several. | All models. |
| `--repo PATH` | Catalogue checkout to read/edit. | This repository. |
| `--run-root PATH` | Search immediate run subdirectories for `report.json`. | `src/probe/runs/weights`. |
| `--report PATH` | Use explicit reports instead of discovery; repeat for several. | Discover local reports; use the newest timestamp per asset. |
| `--output PATH` | Write the full audit/proposals as JSON; unavailable in guide mode. | Terminal output only. |
| `--details` | Expand coverage to individual assets and reasons; unavailable in guide mode. | Compact coverage summary. |
| `--guide` | With `pending`, choose model → asset → container, then review evidence/diff and confirm edits. | Off. |
| `--show-all` | With `--guide`, include usable results already matching saved counts; viewing these does not rewrite them. | Pending changes only. |
| `--accept MODEL/ASSET/CONTAINER` | Select a specific count; repeat for distinct assets. `pending` previews, `apply` asks to save. | None; unavailable with coverage or the guide. |
| `--remove MODEL/ASSET` | Explicitly select a saved count for deletion; repeat for distinct assets. `pending` previews, `apply` asks to delete. | None; unavailable with coverage or the guide. |

Only usable reports matching the asset identity and inspector version can be
applied. Count evidence is stored per asset as `weight_count` and displayed on
the model page. To preview one explicit selection:

```bash
uv run --locked --project src/probe review-weights pending --accept nemo/pytorch/root
```

### `review-pending-weights`

| Command | What it does |
| --- | --- |
| `review-pending-weights` | Alias for `review-weights pending`. Without `--guide`, lists proposals; with it, walks through selection and confirmed application. |

| Flags | Function and default |
| --- | --- |
| `--guide`, `--show-all` | Interactive review; both off by default. `--show-all` requires `--guide`. |
| `--model`, `--repo`, `--run-root`, `--report` | Same filters, options and defaults as `review-weights` above. |
| `--accept`, `--remove` | Preview explicit changes without editing; none by default. Cannot combine with `--guide`. |
| `--output` | Optional JSON audit file; none by default. Cannot combine with `--guide`. |
| `--details` | Accepted but has no effect on the pending listing; cannot combine with `--guide`. |

### `probe-models`

| Command | What it does |
| --- | --- |
| `probe-models list` | List configured probe IDs/scopes without installing model packages or downloading weights. |
| `probe-models run ID [ID ...]` | Run selected author prediction workflows in their locked CPU environments. Writes reports, logs and artifacts under a unique run directory. Exit zero requires every result to be `observed`; `inconclusive`, `blocked` and `failed` exit nonzero. An observed result establishes only the tested checkpoint/workflow. |

| Argument/flag | Function and options | Default |
| --- | --- | --- |
| `ID [ID ...]` | Probe IDs from `list` (not necessarily model-card names). | `run` requires IDs or `--all`. |
| `--all` | Run every configured probe. | Off. |
| `--timeout N` | Worker timeout in seconds, including setup and child processes. | `600`. |
| `--run-root PATH` | Parent directory for generated run reports. | `src/probe/runs`. |

`python -m probe` is an equivalent entry point. To add a probe, register its
workflow in `models.json`, pin resources/checksums in `resources.json`, add a
locked environment if needed, and implement its adapter in `probe/worker.py`.

### Developer checks

```bash
uv run --locked --project src/probe python -m unittest discover -s src/probe/tests -v
PYTHONPATH=src/probe uv run --locked --project src/probe/environments/weights \
  python -m unittest discover -s src/probe/tests -p test_weights.py -v
```
