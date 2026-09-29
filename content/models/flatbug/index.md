+++
# ── Identity ────────────────────────────────────────────────────────
title              = "FlatBug"
description        = "YOLOv8 insect detector with pyramid-slicing inference for specimens on homogeneous backgrounds."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection-homogeneous"
task               = ["Object Detection", "Instance Segmentation"]
architecture       = "YOLOv8"
year               = 2025
license            = "MIT"
status             = "published"
date               = 2026-09-21

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
produces           = ["bbox", "mask"]
image_input_size         = "any"
developer          = "Asger Svenning et al."
paper_url          = "https://github.com/darsa-group/flat-bug"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"

# ── The model's own card elsewhere, if it has one ───────────────────

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "share-index"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
url          = "https://anon.erda.au.dk/cgi-sid/ls.py?share_id=Bb0CR1FHG6&current_dir=models&flags=f"
note         = "Directory listing for all FlatBug weights, the training dataset, and the manuscript."

[[assets]]
key          = "n"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8n"
filename     = "models/flat_bug_N.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_N.pt"
size_bytes   = 6275129
released     = 2024-10-23

[[assets]]
key          = "s"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8s"
filename     = "models/flat_bug_S.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_S.pt"
size_bytes   = 21398649
released     = 2024-10-23

[[assets]]
key          = "m"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8m"
filename     = "models/flat_bug_M.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_M.pt"
size_bytes   = 49694305
released     = 2024-10-23

[[assets]]
key          = "l"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8l"
filename     = "models/flat_bug_L.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_L.pt"
size_bytes   = 84085321
released     = 2024-10-23

[[assets]]
key          = "m-v2"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8m (v2)"
filename     = "models/flat_bug_M_v2.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_M_v2.pt"
size_bytes   = 54585258
released     = 2026-07-07
note         = "Second-generation M"
+++

> YOLOv8 insect detector with pyramid-slicing inference for specimens on homogeneous backgrounds.

**Intended use.** FlatBug is built for specimens photographed against uniform surfaces: a
light box, a conveyor belt, a plain wall, a sticky trap. The pyramid-slicing inference
strategy means it does not downscale a large image to a fixed input size; it tiles the
image at native resolution and merges the detections. That is the right trade when the
insect is small relative to a high-resolution frame, and the wrong one when it is not.

## Architecture and training

- **Architecture:** YOLOv8, as a size ladder, N, S, M and L, plus a second-generation M
- **Task:** Object Detection and Instance Segmentation (boxes and masks)
- **Trained on:** `fb_yolo`, distributed in the same ERDA share as the weights
- **Taxonomic coverage:** see the publication
- **Framework:** ultralytics

## Inputs and outputs

- **Input size:** any, pyramid slicing operates at native resolution
- **Channel order:** RGB
- **Outputs:** bounding boxes, instance masks
- **Input modality:** image only (discriminative model)

## Performance

See the source publication for evaluation metrics.

| Metric | Value | Evaluation set |
| --- | --- | --- |
| mAP@50 | see source publication | see source publication |

## Limitations

## License and rights

- **License:** MIT
- **Commercial use:** allowed
- **Restrictions:** Weights are hosted on a revocable ERDA share with no DOI. So, the share
  could be regenerated or withdrawn at any time.
- **Upstream source:** <https://anon.erda.au.dk/cgi-sid/ls.py?share_id=Bb0CR1FHG6>

## Citation

```bibtex
@misc{flatbug2025,
  title        = {FlatBug: a YOLOv8 insect detector with pyramid-slicing inference},
  author       = {{Darsa Group}},
  year         = {2025},
  howpublished = {Aarhus University ERDA share Bb0CR1FHG6},
  note         = {Code: https://github.com/darsa-group/flat-bug}
}
```

## How to obtain the weights

Five `.pt` files, all in the `models/` directory of ERDA share `Bb0CR1FHG6`. No
authentication is required. Direct links:

| Variant | File | Size |
| --- | --- | --- |
| YOLOv8n | `models/flat_bug_N.pt` | 6.3 MB |
| YOLOv8s | `models/flat_bug_S.pt` | 21.4 MB |
| YOLOv8m | `models/flat_bug_M.pt` | 49.7 MB |
| YOLOv8l | `models/flat_bug_L.pt` | 84.1 MB |
| YOLOv8m (v2) | `models/flat_bug_M_v2.pt` | 54.6 MB |

The same share also holds `fb_yolo/` (the training dataset, with `data.yaml` and the image
tree).
