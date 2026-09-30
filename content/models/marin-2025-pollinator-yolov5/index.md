+++
# ── Identity ────────────────────────────────────────────────────────
title              = "POLLINATOR — Serra-Marin et al. (2025)"
description        = "YOLOv5m detector of flower-visiting insects in daytime and nighttime field imagery."

# ── Catalogue ───────────────────────────────────────────────────────
purpose            = ["Insect detection"]
task               = ["Object Detection"]
architecture       = ["YOLOv5m"]
base_model         = "ultralytics/yolov5 (yolov5m.pt)"
year               = 2025
license            = "AGPLv3 (weights)"
status             = "published"
date               = 2026-09-21
vocabulary_scope   = "closed"
geographic_scope   = "Studied in the Balearic Islands, Spain"
produces           = ["bbox"]
output_format      = ["pollinator-frame-folders"]
image_input_size   = "1024x1024"
input_modality     = ["image"]
taxonomic_coverage = "Flower-visiting insects; one detection class: pollinator"
developer          = "Arancha Lana; Serra-Marin et al."
paper_url          = "https://doi.org/10.1111/2041-210X.70165"
code_url           = "https://github.com/aranchalana/POLLINATOR"

# ── Weights ─────────────────────────────────────────────────────────
# Hugging Face declares AGPLv3 for the weights; Zenodo declares CC-BY-4.0
# for the software archive. See License and rights below.
hosting_status     = "link_only"
commercial_use     = "unknown"
weight_format      = ["PyTorch"]

[[assets]]
key          = "weights"
provider     = "huggingface"
repo_id      = "pauenric/POLLINATOR_Serra_Marin_et_al_2025"
filename     = "pollinator_serra_marin_2025_best.pt"
revision     = "900afc5bdecdd5d34b723934dcb84d6bdceb8709"
revision_kind = "commit"
gated        = false
url          = "https://huggingface.co/pauenric/POLLINATOR_Serra_Marin_et_al_2025/resolve/900afc5bdecdd5d34b723934dcb84d6bdceb8709/pollinator_serra_marin_2025_best.pt"
+++

**Intended use.** Find flower-visiting insects in field images and video frames
for subsequent human review. Flowers and vegetation make this a detector for
heterogeneous backgrounds.

## Architecture and training

The [repository](https://github.com/aranchalana/POLLINATOR/tree/ecbafff8fd03efaa299f8d07eb121b9ccd05c6dd)
describes fine-tuning pretrained YOLOv5m weights. Its
[dataset configuration](https://github.com/aranchalana/POLLINATOR/blob/ecbafff8fd03efaa299f8d07eb121b9ccd05c6dd/POLLINATOR-MERGE-ALL/data.yaml)
defines one class, `pollinator`. The
[MERGED-ALL v4 export](https://github.com/aranchalana/POLLINATOR/blob/ecbafff8fd03efaa299f8d07eb121b9ccd05c6dd/POLLINATOR-MERGE-ALL/README.roboflow.txt)
documents 16,389 images, orientation correction, stretching to 1024 × 1024 pixels,
and augmentation with flips and rotations. This describes the repository's
export; its exact correspondence to the downloaded checkpoint is unverified.

Static inspection on 2026-09-29 of the checkpoint now published as
`pollinator_serra_marin_2025_best.pt` confirms
`weights = yolov5m.pt`, one class (`0: pollinator`), and architecture depth/width
multipliers of 0.67/0.75. Its training options record `imgsz = 1024`,
`epochs = 150`, and SGD. These are configured values, not proof that all 150
epochs completed: the saved epoch is `-1`, and `best_fitness` and optimizer state
are absent (`None`).

The checkpoint records dataset path `./NEW_DATA_TOT/data.yaml`, run directory
`runs/train/exp4`, timestamp `2025-06-19T22:26:14.768546` (no timezone), and
Ultralytics YOLOv5 commit `17c500461d7b14a24133d91bc6437af62914074c`.
It does not embed that dataset's image list or split membership.

## Inputs and outputs

- **Input:** RGB images; 1024 × 1024 is the documented training size.
- **Output:** bounding boxes, confidence scores and the `pollinator` class.
- **Video processing:** the [supplied script](https://github.com/aranchalana/POLLINATOR/blob/ecbafff8fd03efaa299f8d07eb121b9ccd05c6dd/YOLOv5_POLLINATOR_detect_and_save_with_and_without_object.py)
  converts OpenCV frames to RGB and saves frames into `with_object` and
  `without_object` folders. It calls `model(img_rgb)` without explicitly setting
  inference size; the training size is not enforced by that script.

## Performance

[Table 2 of the paper](https://doi.org/10.1111/2041-210X.70165) reports five-fold
averages for these combined-data experiments:

| Evaluation dataset | Reported train/validation/test images | Precision | Recall | mAP@0.5 | F1 |
| --- | --- | --- | --- | --- | --- |
| ACS data merged | 10,192 / 3,542 / 3,550 | 0.95 | 0.95 | 0.97 | 0.95 |
| ACS + external data | 12,682 / 4,373 / 4,380 | 0.93 | 0.93 | 0.95 | 0.93 |

Neither the repository nor the inspected checkpoint establishes which table
row or fold corresponds to `pollinator_serra_marin_2025_best.pt`; these are study results, not verified
checkpoint-specific scores. No inference or benchmark was run during inspection.

## Limitations

Small insects, leaves mistaken for insects, and unseen plant backgrounds cause
errors. Species identification and confirmation of flower contact require human
review. A detection alone does not establish a pollination interaction.

## How to obtain the weights

The weights can be obtained from either location:

- **Google Drive:** download the checkpoint from the authors'
  [weights folder](https://drive.google.com/drive/folders/1X3buOu6bhYmx0hesPwmcU_FB693SCfHn),
  linked in the original repository's
  [download instructions](https://github.com/aranchalana/POLLINATOR/blob/ecbafff8fd03efaa299f8d07eb121b9ccd05c6dd/runs/train/merged_ALL/weights/read.txt)
  as `best.pt`. This link is not version-pinned.
- **Hugging Face:** download
  [`pollinator_serra_marin_2025_best.pt`](https://huggingface.co/pauenric/POLLINATOR_Serra_Marin_et_al_2025/resolve/900afc5bdecdd5d34b723934dcb84d6bdceb8709/pollinator_serra_marin_2025_best.pt).
  This download is pinned to
  [commit `900afc5b`](https://huggingface.co/pauenric/POLLINATOR_Serra_Marin_et_al_2025/commit/900afc5bdecdd5d34b723934dcb84d6bdceb8709)
  and requires no authentication.

The renamed file matches the previously inspected checkpoint: it contains
42,336,660 bytes and has SHA-256
`9b62c544b5dc31122d93db8ea9363aa4012a1b7636e57de740fa6ae6a2cc600e`.
Use these values to check whether a later download matches this checkpoint. The
[Zenodo v1.0 release](https://zenodo.org/records/17130918) archives the code and
download pointers, not the checkpoint itself.

## License and rights

Zenodo declares **CC-BY-4.0** for the software archive, credited to Arancha Lana.
The dataset configuration also declares CC BY 4.0. The
[Hugging Face model card](https://huggingface.co/pauenric/POLLINATOR_Serra_Marin_et_al_2025/blob/900afc5bdecdd5d34b723934dcb84d6bdceb8709/README.md)
declares **AGPLv3** (`agpl-3.0`) for the model repository containing
`pollinator_serra_marin_2025_best.pt`.

## Citation

```bibtex
@article{serramarin2025pollinator,
  title   = {Comparative assessment of automated and manual monitoring in comprehensive plant–pollinator communities},
  author  = {Serra-Marin, Pau Enric and Solé-Ribalta, Albert and Lana, Arancha and Borge-Holthoefer, Javier and Hervías-Parejo, Sandra and Traveset, Anna},
  journal = {Methods in Ecology and Evolution},
  volume  = {16},
  number  = {12},
  pages   = {2960--2978},
  year    = {2025},
  doi     = {10.1111/2041-210X.70165}
}
```

Software: Arancha Lana (2025). *aranchalana/POLLINATOR: First stable release of
POLLINATOR code* (v1.0). [Zenodo](https://doi.org/10.5281/zenodo.17130918).

## Output format probe

The author video script was run with the published checkpoint. It saves JPEG frames into with_object and without_object folders and exports no machine-readable boxes. The tested frames exercised without_object only; the annotated with_object branch is documented by the source.

Probe date: 2026-09-30. Reproducible setup and evidence are in
[src/probe](https://github.com/InsectAI-COST-Action/model-db/tree/main/src/probe).
