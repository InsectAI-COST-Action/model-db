+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Ștefan et al. (2025)"
description        = "Lightweight YOLO pollinator detectors, NMS-optimized for and evaluated on smartphone time-lapse images of flower-visiting arthropods."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection"]
architecture       = ["YOLOv5", "YOLOv5", "YOLOv7"]
base_model         = "Stark et al. (2023) YOLO detectors, trained on citizen science images"
year               = 2025
license            = "GPL-3.0"
status             = "deprecated"                # hidden: see the note below the front matter
training_data      = ["unpublished"]
build              = { render = "never", list = "never", publishResources = false }
                                                 # Hugo option: no page is generated for this
                                                 # entry and it is left out of every listing.
date               = 2025-03-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Germany (evaluation: Leipzig and Halle; training images: global citizen science)"
produces           = ["bbox", "label"]
output_format      = ["yolov5-detect-txt", "yolov5-detect-txt", "yolov7-detect-txt"]
image_input_size   = "640x640"
taxonomic_coverage = "8 arthropod groups: Araneae, Coleoptera, Diptera, Hemiptera, Hymenoptera, Hymenoptera (Formicidae), Lepidoptera, Orthoptera"
developer          = "Ștefan et al."
paper_url          = "https://doi.org/10.1038/s41598-025-16140-z"
code_url           = "https://github.com/valentinitnelav/smartphone-insect-detect"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "weights"
provider     = "github"
repo         = "stark-t/PAI"
filename     = "yolov5_s_best.pt"
url          = "https://github.com/stark-t/PAI/raw/main/detectors/trained_weights/yolov5_s_best.pt"
size_bytes   = 14397237
sha256       = "9da90c43e48e4a33d9a439f5ea7d1e38ed8375414353d9ffee7fd2a61bf2997a"
note         = "The best model of the study (YOLOv5s), the one behind the NMS-optimized results. Same weights as the Stark et al. (2023) entry; the optimization here is in the inference settings."

[[assets]]
key          = "yolov5n-weights"
provider     = "github"
repo         = "stark-t/PAI"
filename     = "yolov5_n_best.pt"
url          = "https://github.com/stark-t/PAI/raw/main/detectors/trained_weights/yolov5_n_best.pt"
size_bytes   = 3844469
sha256       = "4752ab81e3cdac5d50e9cee6a7df27751872c4790c07d9ff09c74856ff5d0d8f"

[[assets]]
key          = "yolov7-tiny-weights"
provider     = "github"
repo         = "stark-t/PAI"
filename     = "yolov7_tiny_best.pt"
url          = "https://github.com/stark-t/PAI/raw/main/detectors/trained_weights/yolov7_tiny_best.pt"
size_bytes   = 12290003
sha256       = "9478b5de6fce2ae12b2bcf231093798e814325ae1119755a70d9c2baf7cc843a"

[[assets]]
key          = "code"
provider     = "github"
repo         = "valentinitnelav/smartphone-insect-detect"
url          = "https://github.com/valentinitnelav/smartphone-insect-detect"
note         = "The evaluation pipeline: detection runs, NMS grid search, COCO-style evaluation, and the analysis scripts. Archived on Zenodo: 10.5281/zenodo.15127689."

[[assets]]
key          = "evaluation-dataset"
provider     = "zenodo"
record_id    = "15096610"
url          = "https://doi.org/10.5281/zenodo.15096610"
note         = "The OOD test set: smartphone time-lapse images of flower-visiting arthropods (23,899 cropped images, 24,656 annotated boxes). CC-BY-NC-SA-4.0."
+++

> **Not a separate model; this entry is hidden from the site.** Ștefan et al. (2025) is an
> out-of-distribution evaluation of the same three YOLO detectors (same `.pt` files) that are
> listed under [Stark et al. (2023)](../stark-2023-pollinator-yolov5/). No model was trained in
> that study; it tested those weights on smartphone time-lapse images and re-tuned their NMS
> inference settings. The model card for these weights is `stark-2023-pollinator-yolov5`. The
> text below is kept as a record of the study's results.

> Lightweight YOLO pollinator detectors, NMS-optimized for and evaluated on smartphone time-lapse images of flower-visiting arthropods.

**Intended use.** Detecting and classifying flower-visiting arthropods into broad taxonomic groups in
images from a fixed camera on a flower - the setup of the study was a smartphone on a tripod above the
target flower, shooting time-lapses. The study is an out-of-distribution (OOD) generalisation test: it
takes three YOLO detectors trained by Stark et al. (2023) on citizen science photos and measures how
well they transfer to field time-lapse imagery, where arthropods are small and seen against cluttered,
unseen floral backgrounds. The practical deliverable is the best model, YOLOv5s, with inference
settings (NMS confidence and IoU) re-optimized for this domain.

## Architecture and training

- **Architecture:** three lightweight detectors - YOLOv5-nano, YOLOv5-small and YOLOv7-tiny. No model
  was trained in this study.
- **Trained on (previous study, Stark et al. 2023):** curated citizen science images of flower-visiting
  arthropods, sampled through GBIF; 96.8% of the training images come from iNaturalist (53.9%) and
  Observation.org (42.9%). Eight classes: Araneae, Coleoptera, Diptera, Hemiptera, Hymenoptera,
  Hymenoptera (Formicidae, ants), Lepidoptera, Orthoptera. In-distribution test accuracy in that study
  ranged from 93 to 97%. The weights are the same files as in the Stark et al. (2023) entry of this
  zoo; see also `stark-2023-pollinator-yolov5`.
- **This study:** OOD evaluation only. Detections were first run with NMS confidence 0.001 over a grid
  of NMS IoU thresholds (0.1 to 0.9) for all three models, scored class-agnostically with
  `pycocotools`. The F1-best model and settings were then re-run for the final results: YOLOv5s at
  NMS confidence 0.202 and NMS IoU 0.3.
- **SAHI (Slicing Aided Hyper Inference)** was also tried, class-agnostically, on the images where the
  optimized model found no true positive - a side experiment, not the main evaluation.

## Inputs and outputs

- **Input:** RGB images at 640 px (`detect.py --img-size 640`). In the study these are crops around the
  target flower (average 851x796 px) from smartphone time-lapse frames (mostly 1600x1200).
- **Outputs:** one bounding box, class (one of the 8 groups) and confidence score per detection. The
  study evaluates the model both class-agnostically (as a pure arthropod detector) and with its class
  predictions collapsed to three groups: Hymenoptera, Diptera and OtherT.
- **Evaluation matching:** a detection counts as a true positive at IoU >= 0.5 with an annotated box
  (the supplementary tables repeat the evaluation at IoU >= 0.1).

## Performance

All numbers below are from the source publication (its Table 2), computed on the OOD test set: 23,899
cropped time-lapse images of 201 flower sessions, 24,656 annotated boxes, 1,281 individual arthropods.
They are the NMS-optimized YOLOv5s at evaluation IoU 0.5.

**Box-level, class-agnostic localisation** (every annotated box counts):

| Metric | Value |
| --- | --- |
| Precision | 86.6% |
| Recall | 59.4% |
| F1 | 70.5% |
| False positives | 2,265 (9.2% of ground-truth boxes) |

**Individual-level** (a pollinator counts as localised if detected in at least one frame, and as
correctly classified if its group is right in the matched frames):

| Group | N. individuals | Localised | Classification recall | Classification F1 |
| --- | --- | --- | --- | --- |
| Hymenoptera | 1,013 | 91.21% | 80.45% | 0.883 |
| Diptera | 145 | 80.69% | 66.90% | 0.588 |
| Other taxa | 123 | 56.10% | 47.97% | 0.551 |
| Total | 1,281 | 86.65% | 75.80% | 0.821 |

Box-level recall is heavily group-dependent: 70.0% for Hymenoptera and 61.4% for Diptera, but 4.6% for
Araneae and 13.8% for Hemiptera. Lepidoptera and Orthoptera had no instances in the evaluation set.
The paper also measured the false-positive rate on floral-only background frames (flowers without
visitors are the common case in time-lapse data).

## Limitations

- **Out-of-distribution drop.** The same detectors scored 93-97% accuracy in-distribution (Stark et
  al. 2023); on unseen time-lapse imagery class-agnostic F1 falls to 70.5%. Most of the loss is
  recall: 40% of annotated boxes are missed.
- **Small arthropods.** The median annotated box covers 2.8% of the image area in this dataset, over
  ten times smaller than the training median (28.8%). Small, blurry flower visitors are the main
  failure mode; detection improves with box area and image sharpness.
- **Taxa imbalance.** Hymenoptera dominate the evaluation data (79% of individuals), and spiders and
  true bugs are almost never found (box-level recall 4.6% and 13.8%). Performance on any other
  background flora is untested: 60% of annotated boxes sit on just four plant species.
- **Mimicry.** Hoverflies (Syrphidae, Diptera) are misclassified as Hymenoptera often enough that the
  paper tests it explicitly: mimicry produces high-confidence mislabels, unlike the low-confidence
  errors small or blurry insects produce.
- **Tuned on the test domain.** The NMS confidence and IoU (0.202 / 0.3) were chosen by grid search on
  this very dataset to maximise F1, so they are optimal for smartphone time-lapse crops from Germany
  in 2021, not universally.
- **Not a species identifier.** Eight broad groups, order level at best; the classes
  Hymenoptera-Formicidae and Hymenoptera only separate ants from other wasps and bees.
- **SAHI is not a solution here:** the authors note it cannot most probably be deployed in real time
  on a custom camera in field conditions.

## License and rights

- **Code:** GPL-3.0, the license of the smartphone-insect-detect repository; the Zenodo archive of the
  repository (10.5281/zenodo.15127689) carries the same.
- **Weights:** the `.pt` files live in the stark-t/PAI repository, which has **no license file**.
  Until the authors state one, treat the weights' legal status as unclear; commercial use is listed
  as unknown for this reason. (The Stark et al. 2023 paper itself is open access under CC-BY-4.0.)
- **Evaluation dataset:** CC-BY-NC-SA-4.0 on Zenodo - non-commercial, share-alike. Anyone fine-tuning
  on or redistributing the OOD data inherits those terms.
- **Upstream source:** <https://github.com/valentinitnelav/smartphone-insect-detect> (branch `preprint`
  matches the preprint; `main` tracks the published version).

## Citation

```bibtex
@article{stefan2025smartphone,
  title   = {Successes and limitations of pretrained YOLO detectors applied to unseen time-lapse
             images for automated pollinator monitoring},
  author  = {{\c S}tefan, Valentin and Stark, Thomas and Wurm, Michael and Taubenb{\"o}ck, Hannes
             and Knight, Tiffany M.},
  journal = {Scientific Reports},
  volume  = {15},
  pages   = {30671},
  year    = {2025},
  doi     = {10.1038/s41598-025-16140-z}
}
```

## How to obtain the weights

Download the three `.pt` files from the
[stark-t/PAI](https://github.com/stark-t/PAI/tree/main/detectors/trained_weights) repository
(`detectors/trained_weights/`), or run the `detectors/weights/download_weights.sh` script from the
smartphone-insect-detect repository, which fetches exactly these files. No authentication is
required.

| File | Size | SHA-256 |
| --- | --- | --- |
| `yolov5_s_best.pt` (best model) | 14.4 MB | `9da90c43e48e4a33d9a439f5ea7d1e38ed8375414353d9ffee7fd2a61bf2997a` |
| `yolov5_n_best.pt` | 3.8 MB | `4752ab81e3cdac5d50e9cee6a7df27751872c4790c07d9ff09c74856ff5d0d8f` |
| `yolov7_tiny_best.pt` | 12.3 MB | `9478b5de6fce2ae12b2bcf231093798e814325ae1119755a70d9c2baf7cc843a` |

To reproduce the study's optimized setup, run YOLOv5's `detect.py` with `--img-size 640
--conf-thres 0.202 --iou-thres 0.3` (the study rounded from the grid-search optimum 0.201918). The
evaluation pipeline in the repository takes it from there: COCO conversion, `pycocotools` scoring and
the analysis scripts.

## Output format probe

The detector stage documented in code/detect.sh was probed with all three study checkpoints, saving six-column YOLO text including confidence. The repository separately converts these files to COCO for evaluation; that downstream conversion was not run.

Probe date: 2026-09-30. Reproducible setup and evidence are in
[src/probe](https://github.com/InsectAI-COST-Action/model-db/tree/main/src/probe).
