+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Bjerge et al. (2023)"
description        = "YOLOv5 model trained on flower pollinators."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection"]
architecture       = ["YOLOv5"]
year               = 2023
license            = "CC-BY-4.0"
status             = "published"
training_data      = ["10.5281/zenodo.7395751"]
date               = 2026-09-21

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
produces           = ["bbox"]
image_input_size         = "1280x1280"
developer          = "Bjerge et al."
paper_url          = "https://journals.plos.org/sustainabilitytransformation/article?id=10.1371/journal.pstr.0000051"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"

# ── The model's own card elsewhere, if it has one ───────────────────

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "zenodo-record"
provider     = "zenodo"
record_id    = "7395752"
url          = "https://zenodo.org/records/7395752/files/YOLOv5models.zip"
note         = "Weights are one of several files in the record; see the record's file list."

[[assets]]
key          = "weights-640-m"
provider     = "zenodo"
record_id    = "7395752"
filename     = "insect1201-bestF1-640v5m.pt"
url          = "https://zenodo.org/records/7395752/files/YOLOv5models.zip"
released     = 2023-12-01
note         = "The weights file is inside the YOLOv5models.zip archive in the Zenodo record."

[[assets]]
key          = "weights-1280-s"
provider     = "zenodo"
record_id    = "7395752"
filename     = "insect1201-bestF1-1280v5s6.pt"
url          = "https://zenodo.org/records/7395752/files/YOLOv5models.zip"
released     = 2023-12-01
note         = "The weights file is inside the YOLOv5models.zip archive in the Zenodo record."

[[assets]]
key          = "weights-1280-m"
provider     = "zenodo"
record_id    = "7395752"
filename     = "insect1201-bestF1-1280v5m6.pt"
url          = "https://zenodo.org/records/7395752/files/YOLOv5models.zip"
released     = 2023-12-01
note         = "The weights file is inside the YOLOv5models.zip archive in the Zenodo record."

+++

> YOLOv5 model trained on flower pollinators.

**Intended use.** Detecting pollinators visiting flowers in field imagery. 
It is built for the cluttered-background case where the insect is a small
fraction of the frame and the flowers are visually dominant.

## Architecture and training

- **Architecture:** YOLOv5
- **Task:** Object Detection (bounding boxes)
- **Trained on:** flower pollinator imagery, see the source publication for the dataset
  composition
- **Taxonomic coverage:** pollinators, see the source publication for the exact class list
- **Framework:** ultralytics YOLOv5

## Inputs and outputs

- **Input size:** 1280x1280, the authors report this as the best-performing configuration
- **Channel order:** RGB
- **Outputs:** bounding boxes
- **Input modality:** image only (discriminative model)

## Performance

See the source publication.

| Metric | Value | Evaluation set |
| --- | --- | --- |
| see source publication | — | — |

## Limitations

## License and rights

- **License:** CC-BY-4.0
- **Commercial use:** allowed
- **Restrictions:** Attribution is required by the license. Cite the source publication
  listed under Citation below.
- **Upstream source:** <https://zenodo.org/records/7395752>

## Citation

```bibtex
@article{bjerge2023pollinator,
  title   = {Detection of flower-visiting insects with deep learning},
  author  = {Bjerge, Kim et al.},
  journal = {PLOS Sustainability and Transformation},
  year    = {2023},
  doi     = {10.1371/journal.pstr.0000051}
}
```

## How to obtain the weights

From Zenodo record [`7395752`](https://zenodo.org/records/7395752). No authentication is
required. The record contains several files, the weights are in the `YOLOv5models.zip` file.

## Output format probe

The published 1280s6 checkpoint was tested with the author’s
[insectsFlowers CSV exporter](https://github.com/kimbjerge/insectsFlowers/blob/eacd588d8069e6882c287f9039abf7064b210a20/yolov5/detectCSVNI2v2.py).
It produced headerless CSV rows with pixel corners, one-based class IDs and
integer percentage confidence, alongside YOLO text. That repository describes
a later study; its historical pairing with this 2023 model is unconfirmed, so
the advertised format remains unassigned. Probe date: 2026-09-30.
