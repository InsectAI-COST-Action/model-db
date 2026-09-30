+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Stark et al. (2023)"
description        = "YOLOv5 and YOLOv7 detectors that locate flower-visiting arthropods in images and sort them into eight groups (spiders, beetles, flies, true bugs, bees and wasps, ants, butterflies and moths, grasshoppers)."

# ── Catalogue ───────────────────────────────────────────────────────
purpose            = ["Insect detection", "Insect classification"]
task               = ["Object Detection", "Classification"]
architecture       = ["YOLOv5", "YOLOv7"]
year               = 2023
license            = "AGPL-3.0-only"
status             = "published"
training_data      = ["https://github.com/stark-t/PAI/tree/d277ee402d605aa96795ad2751f3a7b3b4cdd6c7/data"]
date               = 2026-09-21

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Europe"
produces           = ["bbox", "label"]
target_taxonomic_rank = ["order", "family"]
output_format      = ["yolov5-detect-txt", "yolov7-detect-txt"]
image_input_size   = "640x640"
taxonomic_coverage = "8 groups: Araneae, Coleoptera, Diptera, Hemiptera, Hymenoptera, Formicidae, Lepidoptera, Orthoptera"
developer          = "Stark, Thomas; Ştefan, Valentin et al."
paper_url          = "https://doi.org/10.1038/s41598-023-43482-3"
code_url           = "https://github.com/stark-t/PAI"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "weights-folder"
provider     = "github"
url          = "https://github.com/stark-t/PAI/tree/main/detectors/trained_weights"
note         = "All three weight files, plus a README.md describing how to use them"

[[assets]]
key          = "nano"
provider     = "github"
variant      = "YOLOv5n"
filename     = "yolov5_n_best.pt"
url          = "https://github.com/stark-t/PAI/raw/main/detectors/trained_weights/yolov5_n_best.pt"
size_bytes   = 3844469
note         = "Nano. Recommended thresholds: confidence 0.2, IoU 0.5."

[[assets]]
key          = "small"
provider     = "github"
variant      = "YOLOv5s"
filename     = "yolov5_s_best.pt"
url          = "https://github.com/stark-t/PAI/raw/main/detectors/trained_weights/yolov5_s_best.pt"
size_bytes   = 14397237
note         = "Small. Highest overall accuracy of the three. Recommended thresholds: confidence 0.3, IoU 0.6."

[[assets]]
key          = "tiny"
provider     = "github"
variant      = "YOLOv7-tiny"
filename     = "yolov7_tiny_best.pt"
url          = "https://github.com/stark-t/PAI/raw/main/detectors/trained_weights/yolov7_tiny_best.pt"
size_bytes   = 12290003
note         = "Tiny. Highest recall, most false positives. Recommended thresholds: confidence 0.1, IoU 0.3."
+++

> Three light-weight YOLO detectors (YOLOv5n, YOLOv5s, YOLOv7-tiny) that find arthropods on
> flowers and assign each one to one of eight broad groups.

**Intended use.** Detecting and classifying flower-visiting arthropods to group level
(mostly order) in close-up photographs.
The models are small enough for edge use. They do not
identify families or species, apart from the ant family Formicidae, which is a separate
group from the other Hymenoptera.

## Architecture and training

- **Architecture:** YOLOv5n (1.9 M parameters), YOLOv5s (7.2 M), YOLOv7-tiny (6.2 M)
- **Task:** Object Detection (bounding boxes) with 8 classes. Each box carries one group label.
- **Classes (label id - group):** 0 - Araneae, 1 - Coleoptera, 2 - Diptera, 3 - Hemiptera,
  4 - Hymenoptera, 5 - Hymenoptera Formicidae, 6 - Lepidoptera, 7 - Orthoptera
- **Trained on:** 17,709 images with 21,218 bounding boxes. The images come from GBIF
  occurrence records (54% from iNaturalist and 43% Observation.org, totaling ~97%) of species present in
  Europe, and were hand-annotated by entomologists. The split is 14,348 training images,
  plus 1,680 validation and 1,680 test images (210 per group). The images are not
  redistributed. The [image URLs and annotations](https://github.com/stark-t/PAI/tree/main/data)
  are published instead, with scripts to rebuild the dataset.
- **Training:** 640 px input, batch size 8, 300 epochs. The same hyper-parameters were
  used for all three models. Training scripts and more details in the GitHub repo.
- **Framework:** the original [ultralytics/yolov5](https://github.com/ultralytics/yolov5)
  and [WongKinYiu/yolov7](https://github.com/WongKinYiu/yolov7) repositories, not the
  `ultralytics` pip package.

## Inputs and outputs

- **Input size:** 640x640 (RGB images resized to 640 px by the YOLO loader at training time)
- **Channel order:** RGB
- **Outputs:** bounding boxes, each with a group label and a confidence score
- **Input modality:** image only
- **Thresholds:** the paper tuned the confidence and IoU thresholds per model by grid
  search. Use the values recommended in the table below. The defaults of the YOLO scripts give
  different results.

## Performance

These are the values reported in the source publication (Table 2), on the held-out test
set of 1,680 images (210 per group). Each model uses its own best thresholds.

| Model | Conf. & IoU threshold | Overall accuracy | Precision | Recall | False positive rate | Mean IoU |
| --- | --- | --- | --- | --- | --- | --- |
| YOLOv5n | 0.2 & 0.5 | 0.945 | 0.843 | 0.831 | 0.031 | 0.783 |
| YOLOv5s | 0.3 & 0.6 | 0.962 | 0.909 | 0.869 | 0.021 | 0.805 |
| YOLOv7-tiny | 0.1 & 0.3 | 0.951 | 0.845 | 0.891 | 0.028 | 0.803 |

In a separate test on 1,061 hoverfly (Syrphidae) images, YOLOv7-tiny classified the
hoverflies correctly as Diptera and rarely confused them with the Hymenoptera they mimic.

## Limitations

- **Close-up citizen-science photos only.** The training images are mostly smartphone and
  camera photos in which the arthropod fills a large part of the frame (median relative
  box area about 0.34). Accuracy drops when arthropods are small or several appear in one
  image. The authors have tested the models on time-lapse camera imagery in a later study, with
  expected lower performance there, see Ştefan et al. (2025) at https://doi.org/10.1038/s41598-025-16140-z
- **Small and crowded groups.** All three models missed more Hemiptera and ants
  (Formicidae) than other groups. These classes have the smallest boxes and the most boxes
  per image.
- **Coarse taxonomy.** There are eight groups, most at order level. An arthropod outside
  these groups, such as Neuroptera or Opiliones, will be forced into one of the eight
  classes or missed.
- **European taxa.** Images were sampled from species present in Europe, and for the four
  main pollinator orders only from families known to visit flowers.
- **YOLOv7-tiny** produces more false positives on the background than the two YOLOv5
  models.

## License and rights

- **License:** AGPL-3.0-only (porting the license of the Ultralytics YOLO code the weights were
  trained with)
- **Commercial use:** allowed under AGPL-3.0 copyleft terms.
- **Notes:** YOLOv5 is AGPL-3.0 and YOLOv7 is GPL-3.0. Both are compatible with an
  AGPL-3.0 model. The *Scientific Reports* article itself is CC-BY-4.0.
- **Restrictions:** Attribution required. Cite the source publication below.
- **Upstream source:** <https://github.com/stark-t/PAI/tree/main/detectors/trained_weights>

## Citation

```bibtex
@article{stark2023pollinator,
  title   = {{YOLO} object detection models can locate and classify broad groups of
             flower-visiting arthropods in images},
  author  = {Stark, Thomas and Ştefan, Valentin and Wurm, Michael and
             Spanier, Robin and Taubenböck, Hannes and Knight, Tiffany M.},
  journal = {Scientific Reports},
  volume  = {13},
  pages   = {16364},
  year    = {2023},
  doi     = {10.1038/s41598-023-43482-3}
}
```

## How to obtain the weights

The three `.pt` files are in the
[trained_weights](https://github.com/stark-t/PAI/tree/main/detectors/trained_weights) 
of the stark-t/PAI repository and download without authentication. 

See also the [detectors README](https://github.com/stark-t/PAI/tree/main/detectors#readme).

## Output format probe

The author-recommended detect.py commands were run with the nano, small and tiny study checkpoints. Their --save-txt --save-conf output has six columns: class, normalized center x/y, width, height, confidence. A blank control produces no label file.

Probe date: 2026-09-30. Reproducible setup and evidence are in
[src/probe](https://github.com/InsectAI-COST-Action/model-db/tree/main/src/probe).
