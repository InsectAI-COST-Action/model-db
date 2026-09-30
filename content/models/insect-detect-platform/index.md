+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Insect Detect platform"
description        = "Detects arthropods on homogeneous backgrounds, trained on a colored platform background."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection"]
architecture       = ["YOLOv6"]
output_format      = ["insect-detect-csv"]
base_model         = "YOLOv6 pretrained on COCO"
year               = 2026
license            = "GPL-3.0-or-later"
status             = "published"
training_data      = ["10.5281/zenodo.7725941", "unpublished"]
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
produces           = ["bbox"]
image_input_size   = "800x448"
input_modality     = []
developer          = "Maximilian Sittinger"

# ── Weights ─────────────────────────────────────────────────────────
[[assets]]
key        = "weights"
provider   = "github"
url        = "https://github.com/maxsitt/insect-detect/releases/download/v2.0.0/platform_insect-detect-tiled_v2-0-0.tar.xz"
filename   = "platform_insect-detect-tiled_v2-0-0.tar.xz"
sha256     = "4e50fe20324f19a9f9b722e8b949b35b3b4db60cff6cf9dacb6f11a8eec46362"
released   = 2026-04-01
note       = "Luxonis NN Archive format for deployment on Luxonis OAK devices."
+++

**Intended use.** Generic insect detection model for deployment on Luxonis OAK devices,
e.g. OAK-1 used in the [Insect Detect](https://github.com/maxsitt/insect-detect) camera trap. Works only with uniform, homogeneous backgrounds, e.g. a colored platform.

## Architecture and training

Based on YOLOv6 pretrained on the COCO dataset. Trained with
[luxonis-train](https://github.com/luxonis/luxonis-train) on a tiled version [to be published]
of the [Insect Detect detection](https://doi.org/10.5281/zenodo.7725941) dataset.

## Inputs and outputs

Expects RGB images with 800x448 px size and NCHW layout as input.
Outputs bounding boxes with a single class "insect" and associated confidence scores.

The documented [Insect Detect CSV profile](/formats/detection/insect-detect-csv.json) follows the v2.0.0 camera-trap metadata writer at revision `24476f4`. It saves active tracklets with frame-normalized box corners, display labels, rounded confidence, tracking identifiers and camera metadata. This is source-inspected only: the full deployment probe requires an attached Luxonis OAK device.

## Performance

[to be published]

## Limitations

Only works on Luxonis OAK devices together with depthai v3. Fails on complex backgrounds
(e.g. vegetation) and requires camera to object distance of < 30 cm for reliable detection.

## How to obtain the weights

Weights in Luxonis NN Archive format published as
[release asset](https://github.com/maxsitt/insect-detect/releases). Other formats
including PyTorch and ONNX will be published soon.

## Citation

```bibtex
@software{sittinger_2026_19372336,
  author       = {Sittinger, Maximilian},
  title        = {Insect Detect - Software for automated insect monitoring with a DIY camera trap system},
  month        = apr,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v2.0.0},
  doi          = {10.5281/zenodo.19372336},
  url          = {https://doi.org/10.5281/zenodo.19372336},
}
```
