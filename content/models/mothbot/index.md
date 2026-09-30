+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Mothbot Detect (MBD)"
description        = "Single-class YOLO26 oriented-box detector that finds every insect on a light-trap sheet photographed by a Mothbox, as the first step of the Mothbot processing pipeline."
foundation         = false

# ── Catalogue ───────────────────────────────────────────────────────
purpose            = ["Insect detection"]
task               = ["Object Detection"]
architecture       = ["YOLO26-OBB"]
base_model         = ""
year               = 2026
license            = "AGPL-3.0-only"
status             = "published"
training_data      = ["unpublished"]
date               = 2026-09-30

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Global (training insects from Panama, Mexico, Croatia, Germany, Poland, Hawaii, North Carolina, Netherlands, Indonesia, Canada, Seattle)"
output_format      = ["mothbot-detection-json"]
produces           = ["bbox"]
target_taxonomic_rank = ["NA"]
image_input_size   = "1600x1600"
taxonomic_coverage = "Class-agnostic: one class, 'creature' (any arthropod on the sheet)"
developer          = "Digital Naturalism Laboratories"
paper_url          = "https://mothbox.org/docs/processing/process/hacker/detect/"
code_url           = "https://github.com/Digital-Naturalism-Laboratories/Mothbot_Process"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "MBD-1-1"
provider     = "github"
filename     = "MBD-1-1.pt"
size_bytes   = 21692897
url          = "https://raw.githubusercontent.com/Digital-Naturalism-Laboratories/Mothbot_Process/7514bee8ace5c9cb859f3566ed3088a7824b692c/trained_models/MBD-1-1.pt"
released     = 2026-09-22
note         = "Newest checkpoint, and the one the Mothbot UI selects by default. Its YAML names it yolo26s_Sept212026 (display name MDB-1-1-OBB); the commit that added it calls it an M model. Pinned to commit 7514bee."

[[assets]]
key          = "MBD-1-0"
provider     = "github"
filename     = "MBD-1-0.pt"
size_bytes   = 22027036
url          = "https://raw.githubusercontent.com/Digital-Naturalism-Laboratories/Mothbot_Process/7514bee8ace5c9cb859f3566ed3088a7824b692c/trained_models/MBD-1-0.pt"
released     = 2026-07-12
note         = "Previous checkpoint, YAML name yolo26m_obb_custom15 (display name Yolo26m15kbugs-OBB). Pinned to commit 7514bee."

[[assets]]
key          = "desktop-app"
provider     = "github"
url          = "https://github.com/Digital-Naturalism-Laboratories/Mothbot_Process/releases"
note         = "Desktop app bundles (Windows, Windows CUDA 11.8, macOS arm64, Linux) with the weights and the full pipeline included, plus SHA256SUMS.txt."
+++

> Finds every insect on a Mothbox light-trap photo and returns one oriented box per individual.

**Intended use.** The detection step of **Mothbot**, the processing software for the
open-hardware [Mothbox](https://mothbox.org) light trap. It is meant for whole-night series of
high-resolution photos of an illuminated sheet, which can carry thousands of insects per frame. The
detector does not name anything. Mothbot passes each crop to BioCLIP 2 (zero-shot, see the
[BioCLIP 2 entry](../bioclip-2/)) and filters the result to a GBIF species list for the region.

## Architecture and training

- **Architecture:** Ultralytics YOLO26 with oriented bounding boxes (OBB), one class (`creature`).
- **Checkpoints:** `MBD-1-1` (September 2026, default) and `MBD-1-0` (July 2026). An older
  `MBD-0-2.pt` without a config file is also in the repository.
- **Training data:** the README describes the interim v0.1 model as trained on 7,000 insects at
  imgsz 1600, from Mothbox deployments in Panama, Mexico, Croatia, Germany, Poland, Hawaii, North
  Carolina, the Netherlands, Indonesia, Canada and Seattle. The original 2025 YOLO11-OBB model was
  trained on 4,500 insects, mostly from Panama. The training data for MBD-1-0 and MBD-1-1 is not
  documented. The display name "15kbugs" hints at about 15,000 insects, but this is not stated.
  The training set is not published.

The rest of the Mothbot pipeline uses off-the-shelf models, which are not part of this entry:
- BioCLIP 2 (`imageomics/bioclip-2` via `pybioclip`), with order rank as the default.
- DINOv2 ViT-S/14 embeddings, clustered with HDBSCAN.
- BiRefNet (via `rembg`), which segments crops for a pixel-mass size estimate.

## Inputs and outputs

- **Input:** RGB light-trap photos, run at `imgsz = 1600`.
- **Shipped YAML settings:** the YAMLs set `conf = 0.1` and `max_det = 5000` (MBD-1-1) or `500` (MBD-1-0).
- **Output:** one JSON per image in X-AnyLabeling/LabelMe style. Each detection is a `shape` with
  `label: "creature"`, `shape_type: "rotation"` and four corner points. Cropped patches are saved
  next to it.
- **Later pipeline steps** add the taxon, the ID confidence and the cluster ID to the same JSON, and
  finally write a Darwin-Core-like CSV.
- **Models:** `.pt` files run through `ultralytics.YOLO`. ONNX export is referenced in the YAMLs,
  but the ONNX files are not in the repository and ONNX selection is disabled in the UI.

The documented [Mothbot detection JSON profile](/formats/detection/mothbot-detection-json.json) follows the PyTorch OBB writer at revision `7514bee`. A CPU probe of MBD-1-1 and the original `_save_result` produced 15 shapes on a specimen fixture and an empty shape list on a blank control. The source invocation uses `imgsz=1600` and `max_det=10000`, leaving confidence/IoU to the model library; YAML training settings are not explicitly forwarded here. The probe covers inference and JSON serialization, excluding thumbnail generation, optional blur enrichment and later identification/tracking stages.

## Performance

Not reported in the source publication. There is no mAP, precision or recall, and no evaluation
set, in the repository or on the documentation site.

## Limitations

- **Class-agnostic.** Everything on the sheet is a `creature`: moths, beetles, flies, spiders,
  debris that looks like an insect. Any taxonomy comes from the downstream BioCLIP 2 step. Its docs
  say that step is reliable mainly at order or family level.
- **Domain.** Trained on Mothbox sheet photos at about 1600 px. Expect worse results on other
  backgrounds, other trap geometries, or much lower resolution.
- **Undocumented checkpoints.** The README still describes the 2025 YOLO11 model and the v0.1
  interim model. It says nothing about the MBD-1-x checkpoints in this entry. For MBD-1-1, the
  model size is ambiguous: the YAML says `s`, the commit says `M`.
- **Performance.** No evaluation has been published.

## How to obtain the weights

The `.pt` files are in the `trained_models/` folder of the GitHub repository. The asset links above
are pinned to commit `7514bee8ace5c9cb859f3566ed3088a7824b692c`. They are also bundled in the
desktop-app releases. No authentication is required.

**License:** the Mothbot_Process repository has no license file. Following the convention used for
[Stark et al. (2023)](../stark-2023-pollinator-yolov5/), this entry records **AGPL-3.0**, the license of
the Ultralytics YOLO code the weights were trained with. If the authors add a license file, that
file is authoritative.

## Citation

No paper or citation file exists. Cite the software:

```bibtex
@software{mothbot_process_2026,
  author = {{Digital Naturalism Laboratories}},
  title  = {Mothbot\_Process: moth detection workflows and desktop tooling},
  year   = {2026},
  url    = {https://github.com/Digital-Naturalism-Laboratories/Mothbot_Process}
}
```
