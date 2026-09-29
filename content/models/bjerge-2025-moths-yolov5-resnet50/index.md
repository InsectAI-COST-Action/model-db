+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Bjerge et al. (2025)"
description        = "YOLOv5 model and several ResNet50 classifiers trained to identify moths to species and other broad groups of night-active insects."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection-heterogeneous"
task               = ["Object Detection"]
architecture       = "YOLOv5/ResNet50"
base_model         = ""
year               = 2025
license            = "CC-BY-4.0"
status             = "published"
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
produces           = ["bbox","label"]
input_size   = "1280x1280"
developer          = "Bjerge et al."
paper_url          = "https://zslpublications.onlinelibrary.wiley.com/doi/full/10.1002/rse2.70007"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"

# ── The model's own card elsewhere, if it has one ───────────────────

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "weights"
provider     = "github"
url          = "https://github.com/kimbjerge/MCC24-trap"
note         = "Weights are one of several files in the record; see the record's file list."

[[assets]]
key          = "insectMoths-bestF1-1280m6"
provider     = "google drive"
filename     = "insectMoths-bestF1-1280m6.pt"
url          = "https://drive.google.com/file/d/12aQpXF7T1YD3PSltI3J5gp4gZ4JQ689A/view?usp=drive_link"
note         = "The weights are referenced in the GitHub repo."

[[assets]]
key          = "100524_dhc_best_128"
provider     = "github"
filename     = "dhc_best_128.pth"
url          = "https://github.com/kimbjerge/MCC24-trap/blob/main/model_order_100524/dhc_best_128.pth"
note         = "The weights file is in the named folder."

[[assets]]
key          = "251224_dhc_best_128"
provider     = "github"
filename     = "dhc_best_128.pth"
url          = "https://github.com/kimbjerge/MCC24-trap/blob/main/model_species_251224/dhc_best_128.pth"
note         = "The weights file is in the named folder and derived from https://doi.org/10.1007/978-3-031-72913-3_4"

+++

> YOLOv5/ResNet50 model trained to detect and classify moths and other night flying insects.

**Intended use.** Detecting and classifying insects landing on a white screen, attracted to a UV lamp. Moths are classified to species, other insects to order or similar.

## Architecture and training

- **Architecture:** YOLOv5/ResNet50
- **Task:** Object Detection (bounding boxes) and classification
- **Trained on:** images from light traps for detection and GBIF examples for classification
- **Taxonomic coverage:** night-active insects, see the source publication for the exact class list
- **Framework:** ultralytics YOLOv5/ResNet50

## Inputs and outputs

- **Input size:** 1280x1280
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
- **Upstream source:** <https://github.com/kimbjerge/MCC24-trap>

## Citation

```bibtex
@article{https://doi.org/10.1002/rse2.70007,
author = {Bjerge, Kim and Karstoft, Henrik and Høye, Toke T.},
title = {Towards edge processing of images from insect camera traps},
journal = {Remote Sensing in Ecology and Conservation},
volume = {11},
number = {5},
pages = {573-589},
keywords = {biodiversity monitoring, camera trap, computer vision, edge processing, insect classification, tracking},
doi = {https://doi.org/10.1002/rse2.70007},
url = {https://zslpublications.onlinelibrary.wiley.com/doi/abs/10.1002/rse2.70007},
eprint = {https://zslpublications.onlinelibrary.wiley.com/doi/pdf/10.1002/rse2.70007},
abstract = {Abstract Insects represent nearly half of all known multicellular species, but knowledge about them lags behind for most vertebrate species. In part for this reason, they are often neglected in biodiversity conservation policies and practice. Computer vision tools, such as insect camera traps, for automated monitoring have the potential to revolutionize insect study and conservation. To further advance insect camera trapping and the analysis of their image data, effective image processing pipelines are needed. In this paper, we present a flexible and fast processing pipeline designed to analyse these recordings by detecting, tracking and classifying nocturnal insects in a broad taxonomy of 15 insect classes and resolution of individual moth species. A classifier with anomaly detection is proposed to filter dark, blurred or partially visible insects that will be uncertain to classify correctly. A simple track-by-detection algorithm is proposed to track classified insects by incorporating feature embeddings, distance and area cost. We evaluated the computational speed and power performance of different edge computing devices (Raspberry Pi's and NVIDIA Jetson Nano) and compared various time-lapse (TL) strategies with tracking. The minimum difference of detections was found for 2-min TL intervals compared to tracking with 0.5 frames per second; however, for insects with fewer than one detection per night, the Pearson correlation decreases. Shifting from tracking to TL monitoring would reduce the number of recorded images and would allow for edge processing of images in real-time on a camera trap with Raspberry Pi. The Jetson Nano is the most energy-efficient solution, capable of real-time tracking at nearly 0.5 fps. Our processing pipeline was applied to more than 5.7 million images recorded at 0.5 frames per second from 12 light camera traps during two full seasons located in diverse habitats, including bogs, heaths and forests. Our results thus show the scalability of insect camera traps.},
year = {2025}
}
```

## How to obtain the weights

From GitHub (https://github.com/kimbjerge/MCC24-trap). No authentication is
required. The record contains several files, the YOLO weights are in the google drive link.
