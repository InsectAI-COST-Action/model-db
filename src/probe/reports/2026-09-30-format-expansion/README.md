# Detection output coverage expansion

The line-delimited TOML inventory contains **14 detection cards**, including the
one deprecated smartphone-study card. **13 now reference specific format
profiles** (12 of 13 non-deprecated cards). The remaining Bjerge 2023 assignment
is intentionally unresolved because the historical exporter/checkpoint pairing
has not been established. This is documentation coverage, not 13 successful
full-pipeline tests.

Seven author-specific profiles were added and the existing observed InsectDCT
profile was attached to its published card. All sources are pinned in each
profile's `notes.sources`. Source-inspected profiles are clearly marked in both
the descriptor and model card.

| Detection card | Documented output | Evidence and limits |
| --- | --- | --- |
| AMI insect detector | `ami-detector-boxes` | Source-inspected postprocessor for both 2023 architectures; drops scores/classes; full inference not run |
| ArthroNat | `ultralytics-detect-results` | [Prior real-checkpoint probe](../2026-09-30/arthronat/report.json), one variant |
| BioMoth | `biomoth-csv` | [New probe](biomoth/report.json): original notebook functions and TorchScript checkpoint; 32 specimen rows, no blank rows |
| Bjerge 2023 | Unassigned | [Prior probe](../2026-09-30/bjerge/report.json) used a later author CSV exporter; historical pairing unresolved |
| Bjerge 2025 moths | `mcc24-csv` | Source-inspected combined pipeline; [prior full run failed](../2026-09-30/moths/report.json) on classifier label-map HTTP 403 |
| Flatbug | `flatbug` | [N](../2026-09-30/flatbug-N/report.json) and [M v2](../2026-09-30/flatbug-M_v2/report.json), author CLI |
| Grounding DINO | `grounding-dino-hf-results` | Source-inspected Transformers 4.40.2 author-example interface; no checkpoint run; newer versions excluded |
| Insect Detect platform | `insect-detect-csv` | Source-inspected v2.0.0 capture CSV; OAK-dependent runtime remains blocked |
| InsectDCT | `insectdct-csv` | [Prior full pipeline probe](../2026-09-30/insectdct/report.json): 35 frames, 40 rows in each table |
| Marin POLLINATOR | `pollinator-frame-folders` | [Prior probe](../2026-09-30/pollinator/report.json): absence branch only; positive annotations remain source-supported |
| Mothbot | `mothbot-detection-json` | [New probe](mothbot/report.json): MBD-1-1 and original writer; 15 specimen shapes, empty blank JSON; later stages excluded |
| Smartphone study (deprecated) | YOLOv5/v7 detection TXT | [Prior receipts](../2026-09-30/README.md), three variants |
| Stark 2023 | YOLOv5/v7 detection TXT | [Prior receipts](../2026-09-30/README.md), three variants |
| Ultra-lightweight Ecto-Trigger | `ecto-trigger-tflite-score` | Source-inspected quantized image-level output; no released-artifact or hardware inference run |

## New runtime evidence

Reproduce from the repository root:

```bash
uv run --locked --project src/probe python -m probe run biomoth mothbot --timeout 600
```

BioMoth runs the original function definitions extracted from the pinned author
notebook, including `batch_process`, without executing visualization cells or
local notebook paths. The original thresholds, calibration and hard-coded year
are preserved. The probe supplies fixture paths and CPU execution.

Mothbot runs real OBB inference through the author's selected library and then
the unchanged `_save_result` and `current_timestamp` function bodies. It uses
the pinned detection script's image size and maximum detection count. It does
not execute the GUI, thumbnail writer, blur enrichment, classification or
tracking. The JSON records thumbnail filenames, but this probe does not create
those thumbnails. Optional blur fields are source-inspected only.

Both probes use the existing pinned Flatbug specimen image plus a generated
white blank control. These are format checks, not in-domain accuracy or
measurement-calibration tests. Original small output artifacts, logs and reports
are retained here; input images and checkpoints remain in the ignored cache.
The report artifact lists include omitted binary inputs and their hashes.

## Remaining work

Resolve the Bjerge 2023 historical exporter, run the source-only AMI and Grounding
DINO interfaces with real checkpoints, inspect the released Ecto-Trigger tensor,
restore the moth classifier label map, and run Insect Detect on OAK hardware.
Mothbot's later enrichment/export stages and POLLINATOR's positive branch also
need their own observations before claiming complete workflow coverage.
