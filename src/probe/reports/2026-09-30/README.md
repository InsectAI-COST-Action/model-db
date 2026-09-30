# Author output probe results

Fourteen probe invocations produced inspected outputs with real checkpoints on
CPU. These are the retained receipts from the initial probe pass; they are not
a complete inventory of the current detection catalogue. See the
[coverage expansion](../2026-09-30-format-expansion/README.md) for the current audit.

Inventory correction: the original card reader split on every `+++`, including
that text inside TOML comments. It therefore missed some cards and incorrectly
reported InsectDCT as unpublished. The parser now recognizes delimiter lines.
The inference observations below are unchanged.

These are format checks, not accuracy measurements. Each linked report records
its exact checkpoint, source, environment and input scope. Some workflows were
first tested with fixtures that yielded no detections; the receipts below are
the final selected runs, not an aggregate claim about all attempted fixtures.

| Model | Observed author output | Evidence and limits |
| --- | --- | --- |
| Stark 2023 | Six-column YOLO TXT, including confidence | [nano](stark-yolov5_n/report.json), [small](stark-yolov5_s/report.json), [tiny](stark-yolov7_tiny/report.json); author CLI settings, populated outputs and blank control |
| Smartphone study | Same six-column TXT at the detector stage | [nano](smartphone-yolov5_n/report.json), [small](smartphone-yolov5_s/report.json), [tiny](smartphone-yolov7_tiny/report.json); downstream COCO evaluation conversion was not run |
| ArthroNat | Ultralytics Python Results, pixel boxes | [report](arthronat/report.json); YOLO11n mosaic33 only; no JSON exporter requested |
| POLLINATOR | JPEG frames in presence/absence directories | [report](pollinator/report.json); only without_object was exercised; the annotated branch is source-supported, not runtime-verified |
| Flatbug | Custom per-image JSON and compiled COCO, plus visual/crop artifacts | [N](flatbug-N/report.json), [M v2](flatbug-M_v2/report.json); 12 and 11 specimen detections respectively, empty blank control; contours observed as 2 × N arrays |
| Bjerge 2023 | Custom headerless CSV plus YOLO TXT | [report](bjerge/report.json); 1280s6 Zenodo checkpoint with user-supplied insectsFlowers exporter; historical pairing unconfirmed, so no format assigned to the card |
| BeetleFlow | Palette mask image and overlay | [report](beetleflow/report.json); 5-class model only, original 301 × 154 resolution, six observed colors; 9-class export not tested |
| InsectMorphoAI | Rapid Scan and Detailed Analysis measurement CSVs | [report](insectmorphoai/report.json); both modes on three author fixtures, three rows per CSV, default calibration/configuration |
| InsectDCT | Final classification and hierarchical-detail CSVs | [report](insectdct/report.json); 35 consecutive author frames, full YOLO11s motion detector and ConvNextBase V6 classifier, 40 rows in each CSV |
| Bjerge 2025 moths | Not verified | [failed run](moths/report.json), [log](moths/run.log); author-required AMI label-map URL returned HTTP 403 before full inference |
| Insect Detect platform | Not verified | [blocked report](insect-detect-platform/report.json); USB enumeration found only Linux root hubs, no Luxonis OAK device |

## Important observed differences

The insectsFlowers CSV uses pixel corners, one-based class indices, integer
percentage confidence, and file-modification timestamps. It is not directly
interchangeable with normalized YOLO text or COCO JSON. The supplied repository
describes a later publication; running the earlier weights in it establishes
compatibility with this invocation, not what the 2023 study historically used.

POLLINATOR keeps its YOLO Detections object internally and saves frames. Its
script's confidence threshold is an additional filter after the model's own
filtering. The two tested frames produced no detections; the actual saved JPEGs
and their directory placement were inspected. A positive in-domain fixture is
still needed to exercise the annotated-frame branch.

BeetleFlow saves palette colors, not raw class IDs. It inherits the input file
extension, so JPEG inputs yield lossy masks. Source inspection also shows the
output counter advancing once per folder: same-extension images in a folder
overwrite earlier outputs. The probe used one specimen in its folder.

InsectMorphoAI's default biomass configuration differs from equations quoted
in its paper. The probe records the application's actual columns and values;
no claim is made that the default camera/lens is calibrated for other imagery.

InsectDCT's CL table contains a classifier score in percent and a one-based
selected taxon index. Its HI table contains per-level classifier details and
probabilities. Neither is the native Ultralytics detection result. The published InsectDCT card now references this verified CSV profile.

## Reproduction

See [the probe README](../../README.md) for commands. The manifest includes runnable and explicitly blocked entries; the linked
coverage audit distinguishes their evidence.
Raw run directories stay under the ignored `src/probe/runs/` directory. These
committed receipts retain small original CSV/TXT/JSON samples, execution logs,
package versions and artifact hashes; binary fixtures and checkpoints are not
copied here.

The first successful InsectDCT run downloaded the torchvision ConvNext backbone
that the author constructor loads before replacing its state. That exact file
has now been added to `resources.json` and is staged into the per-run Torch cache
for subsequent runs. The final recorded run verified this cache and produced the
same 40-row outputs without downloading the backbone. This pins initialization
without modifying author code.

The moth script specifically failed fetching
`01-moths-ukdenmark_v2_category_map_species_names.json` from its author-configured
Compute Canada object-store URL. It has not been replaced with another label
list or with a generic YOLO-only result. Its runnable adapter and failure
receipt remain available for a retry when the source is restored.
