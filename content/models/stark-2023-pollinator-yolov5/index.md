+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Stark et al. (2023)"
description        = "YOLOv5 and YOLOv7 models trained on flower pollinators."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection"]
architecture       = ["YOLOv5", "YOLOv7"]
year               = 2023
license            = "CC-BY-4.0"
status             = "published"
date               = 2026-09-21

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
produces           = ["bbox"]
image_input_size         = "640x640"
developer          = "Stark et al."
paper_url          = "https://www.nature.com/articles/s41598-023-43482-3"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"

# ── The model's own card elsewhere, if it has one ───────────────────

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "weights"
provider     = "github"
filename     = "yolov7_tiny_best.pt"
url          = "https://github.com/stark-t/PAI/blob/main/detectors/trained_weights/yolov7_tiny_best.pt"
note         = "Tiny weights for YOLOv7 trained on flower pollinators."

[[assets]]
key          = "weights"
provider     = "github"
filename     = "yolov5_n_best.pt"
url          = "https://github.com/stark-t/PAI/blob/main/detectors/trained_weights/yolov5_n_best.pt"
note         = "Nano weights for YOLOv5 trained on flower pollinators."

[[assets]]
key          = "weights"
provider     = "github"
filename     = "yolov5_s_best.pt"
url          = "https://github.com/stark-t/PAI/blob/main/detectors/trained_weights/yolov5_s_best.pt"
note         = "Small weights for YOLOv5 trained on flower pollinators."
+++

> YOLOv5 and YOLOv7 models trained on flower pollinators.

**Intended use.** Detecting flower-visiting insects in field imagery.

## Architecture and training

- **Architecture:** YOLOv5 and YOLOv7
- **Task:** Object Detection (bounding boxes)
- **Trained on:** flower pollinator imagery; see the source publication
- **Taxonomic coverage:** pollinators
- **Framework:** ultralytics YOLOv5, YOLOv7

## Inputs and outputs

- **Input size:** 640x640
- **Channel order:** RGB
- **Outputs:** bounding boxes
- **Input modality:** image only (discriminative model only)

## Performance

See the source publication.

| Metric | Value | Evaluation set |
| --- | --- | --- |
| see source publication | — | — |

## Limitations

## License and rights

- **License:** CC-BY-4.0
- **Commercial use:** allowed
- **Restrictions:** Attribution required. Cite the source publication below.
- **Upstream source:** <https://github.com/stark-t/PAI/tree/main/detectors/trained_weights>

## Citation

```bibtex
@article{stark2023pollinator,
  title   = {Insect detection in flower imagery with YOLO architectures},
  author  = {Stark, Thomas et al.},
  journal = {Scientific Reports},
  volume  = {13},
  year    = {2023},
  doi     = {10.1038/s41598-023-43482-3}
}
```

## How to obtain the weights

From the `trained_weights` directory of the [stark-t/PAI](https://github.com/stark-t/PAI)
repository. No authentication is required. The directory contains multiple files.
