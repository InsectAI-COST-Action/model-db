# Model output probes

This project tests the output of an author's prediction workflow with real
published weights. It distinguishes exported files from internal model objects.
The coordinator uses only the standard library; each incompatible model stack
runs in its own locked `uv` environment and fresh subprocess.

## Running probes

Run these commands from the repository root:

```bash
uv run --locked --project src/probe python -m probe list
uv run --locked --project src/probe python -m probe run arthronat
uv run --locked --project src/probe python -m probe run stark-yolov5_n pollinator
uv run --locked --project src/probe python -m probe run --all
uv run --locked --project src/probe python -m unittest discover -s src/probe/tests -v
```

Listing and unit tests do not install model packages or download weights.
A selected inference probe synchronizes its own environment from `uv.lock`.
The supplied runtime projects were tested on Linux x86_64 and target Python 3.11 and use the explicit PyTorch
CPU wheel index. The coordinator supports Python 3.11–3.12. `uv` can obtain
these interpreters when they are missing.

Runs are CPU-only and use two compute threads. `--timeout 600` bounds each
worker, including its child processes; downloads have separate socket and byte
limits. Some author pipelines require several hundred MB of weights; a complete
first run downloads multiple GB. `--run-root /path` changes the run destination.
A run exits nonzero if any selected probe is failed, blocked, or inconclusive.

## Isolation and evidence

- `models.json` specifies model cards, entry points, source citations, settings,
  and adapters. A card can have multiple probes for distinct checkpoints.
- `resources.json` pins every prepared resource by SHA-256, including source
  archives, released checkpoints, and author-provided test images. Downloads
  are verified before use; partial files are never accepted as cache hits.
- `environments/<name>/pyproject.toml` and `uv.lock` isolate dependency stacks.
  Model libraries are never imported into the coordinator.
- `.cache/` holds verified downloads. `runs/<run>/<probe>/` holds a unique
  request, log, report and artifacts. These directories and environments are
  gitignored; weights are never committed or published by Hugo.
- Reports identify source/weight hashes, the environment lock, commands,
  installed packages and output artifacts. New runs also fingerprint the
  coordinator and worker source. Author-generated auxiliary downloads are
  confined to the run's Torch cache or extracted source tree; they must be
  inspected and pinned before treating a workflow as fully reproducible.
- `reports/` holds curated small evidence and the review results. It does not
  contain checkpoints or copied author code.

Environment isolation prevents dependency conflicts. It is not a security
sandbox: running an author script or loading a pickle checkpoint executes that
code with the invoking user's permissions. Only run reviewed model sources.

## Interpreting results

`observed` means the configured author path completed and its expected artifact
was inspected. It is evidence for that checkpoint, input and invocation—not
proof about every version, option, or checkpoint in the model family.
`inconclusive` means inference completed but produced no populated instance
output. `failed` retains the runtime error and log. `blocked` records a known
missing prerequisite, such as an OAK device, without substituting generic YOLO
inference for the intended workflow.

Fixture adapters may prepare input directories, generate a blank control or a
short video from a real image, select CPU, and redirect downloads to pinned
local sources. Those changes are recorded in the scope and command. They do
not replace predictions with synthetic boxes. InsectDCT uses consecutive author
frames because motion enhancement depends on frame history. These are format
probes, not accuracy or speed benchmarks.

The files `observed.json` and `python-results.json` are probe evidence. They are
not advertised as JSON outputs from authors who return Python objects or save
images. A missing detection TXT on a blank image is distinct from an empty file.

No probe automatically rewrites model cards. Review actual artifacts, the
selected workflow, and the source before assigning an `output_format`. In
particular, later code from the same author does not establish which exporter
was used in an earlier publication.

## Adding a probe

Add the author entry point and one representative variant to `models.json`,
then pin its resources in `resources.json`. Create a separate locked runtime
when dependencies conflict. Implement a small adapter in `probe/worker.py`
that invokes the real author API/CLI and inspects its output. The coordinator
owns downloads, time limits, process isolation, and evidence recording.

Each report has a schema version and a `capability` field, currently only
`output_format`. This leaves room for later metadata probes without mixing
parameter counting or architecture inference into the current output tests.
