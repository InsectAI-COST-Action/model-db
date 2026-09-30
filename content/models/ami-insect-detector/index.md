+++
# ── Identity ────────────────────────────────────────────────────────
title              = "AMI insect detector"
description        = "Class-agnostic Faster R-CNN that boxes every insect on a nocturnal light-trap screen image; the detection stage of the AMI data companion and the Antenna platform."
foundation         = false

# ── Catalogue ───────────────────────────────────────────────────────
purpose            = ["Insect detection"]
task               = ["Object Detection"]
architecture       = ["Faster R-CNN ResNet50-FPN", "Faster R-CNN MobileNetV3-Large-FPN"]
base_model         = "torchvision fasterrcnn_resnet50_fpn; torchvision fasterrcnn_mobilenet_v3_large_fpn"
year               = 2023
license            = "AGPL-3.0-only"
status             = "published"
date               = 2026-09-30

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Global (trap images from North America, Europe and Central America)"
produces           = ["bbox"]
image_input_size   = "any"
taxonomic_coverage = "Class-agnostic: one class, 'object' (any arthropod on the trap screen)"
developer          = "Rolnick Lab (Mila / McGill) and the AMI consortium"
paper_url          = "https://doi.org/10.1007/978-3-031-72913-3_4"
code_url           = "https://github.com/RolnickLab/ami-data-companion"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "fasterrcnn-resnet50-2023"
provider     = "url"
filename     = "fasterrcnn_resnet50_fpn_tz53qv9v.pt"
size_bytes   = 330066092
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/localization/fasterrcnn_resnet50_fpn_tz53qv9v.pt"
note         = "Default: the detector the AMI API and Antenna run (MothObjectDetector_FasterRCNN_2023). Keeps boxes with score > 0.80. Defined in trapdata/ml/models/localization.py at ami-data-companion commit 55d0787."

[[assets]]
key          = "fasterrcnn-mobilenetv3-2023"
provider     = "url"
filename     = "fasterrcnn_mobilenet_v3_large_fpn_uqfh7u9w.pt"
size_bytes   = 151724126
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/localization/fasterrcnn_mobilenet_v3_large_fpn_uqfh7u9w.pt"
note         = "Fast variant for CPUs (about 6x faster per the authors, near-similar accuracy). Score threshold 0.50."

[[assets]]
key          = "fasterrcnn-resnet50-2021"
provider     = "url"
filename     = "v1_localizmodel_2021-08-17-12-06.pt"
size_bytes   = 330063958
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/localization/v1_localizmodel_2021-08-17-12-06.pt"
note         = "Legacy 2021 detector trained on real trap images. Score threshold 0.99. Kept for reproducibility."
+++

> Boxes every insect on a light-trap screen image, without naming it.

**Intended use.** The first stage of the AMI (Automated Monitoring of Insects) pipeline. It is
used by the [AMI data companion](https://github.com/RolnickLab/ami-data-companion) desktop app and
by the [Antenna](https://github.com/RolnickLab/antenna) web platform, on images from camera traps
that photograph a UV-lit screen at night. The boxes are passed on to a moth/non-moth filter, then to
a regional species classifier (see the [AMI moth classifiers entry](../ami-moth-classifiers/)).
The detector also works as a stand-alone, class-agnostic insect detector for other trap designs,
but expect a domain gap.

## Architecture and training

- **Architecture:** torchvision Faster R-CNN with a ResNet50-FPN backbone (default). There is also
  a MobileNetV3-Large-FPN version for CPU use. One foreground class plus background, and up to 500
  boxes per image.
- **Training data (2023 models):**
  - The Segment Anything Model (SAM) cut about 4,000 insect crops from 300 trap images.
  - After manual review, 2,600 clean crops were pasted onto trap backgrounds, making 5,000
    synthetic training images (Jain et al., 2024).
  - A comment in the code says "GBIF images and synthetic data". The paper describes only the
    synthetic trap composites.
- **Legacy 2021 model:** trained directly on annotated trap images.
- **Training code:** [RolnickLab/ami-ml](https://github.com/RolnickLab/ami-ml) (`src/localization`).

## Inputs and outputs

- **Input:** a full-resolution RGB trap image, converted with `ToTensor` only. Resizing is left to
  torchvision's internal transform, which defaults to a shortest side of 800 and a longest side of
  1333. That default comes from torchvision; the repository does not document it.
- **Output:** integer pixel boxes `[x1, y1, x2, y2]` with a score, filtered at the
  model-specific threshold shown in the asset notes. There is no class label.
- **In the AMI API** (`trapdata/api/schemas.py`), each detection is returned as `bbox{x1,y1,x2,y2}`
  with its downstream classifications attached.

## Performance

Not reported in the source publication: the ECCV 2024 paper gives no detector mAP, precision or
recall. It only reports that the MobileNetV3 variant runs about 6x faster on CPU with
near-similar accuracy.

## Limitations

- **Class-agnostic.** Moths, beetles, flies, caddisflies and spiders are all just `object`.
  Identification needs the downstream classifiers.
- **Synthetic training data.** Trained on composites built from about 300 trap images. Real scenes
  with dense clusters, overlapping insects, shadows or screen folds are not well covered, and no
  in-the-wild benchmark is published.
- **Domain.** Built for nocturnal UV light-trap screens. The authors note that diurnal traps are
  harder.
- **Small insects.** The default torchvision resize means very small insects on high-resolution
  images may be lost. Consider tiling.
- **Hosting.** The weights live only on a Digital Research Alliance of Canada object store, not on
  Zenodo or Hugging Face, and the files are unpinned. Some legacy AMI files (for example Turing-UK)
  already return 404.

## How to obtain the weights

Direct HTTPS download from the object store, with no authentication. The `AUTH_…` segment of the
URL is required. The URLs are defined in `trapdata/ml/models/localization.py` and
`trapdata/settings.py` of ami-data-companion, curated at commit
`55d0787570f8c9d92c450f4fb65a58dd25cf6634`. Installing `trapdata` downloads them automatically.

**License:** no separate license is stated for the weights. This entry records **AGPL-3.0**, the
license of the AMI code that defines, trains and serves them (ami-data-companion, ami-ml, antenna).
The AMI dataset is MIT (Zenodo 10.5281/zenodo.11358689).

## Citation

```bibtex
@inproceedings{jain2024ami,
  title     = {Insect Identification in the Wild: The {AMI} Dataset},
  author    = {Jain, Aditya and Cunha, Fagner and Bunsen, Michael J. and Ca{\~n}as, Juan Sebasti{\'a}n and
               Pasi, L{\'e}onard and Pinoy, Nathan and Helsing, Flemming and Russo, JoAnne and
               Botham, Marc S. and Sabourin, Michael and Fr{\'e}chette, Jonathan and Anctil, Alexandre and
               Lopez, Yacksecari and Navarro, Eduardo and P{\'e}rez, Filonila and Zamora, Ana C. and
               Ramirez-Silva, Jose Alejandro and Gagnon, Jonathan and August, Tom A. and Bjerge, Kim and
               Gomez Segura, Alba and B{\'e}lisle, Marc and Basset, Yves and McFarland, Kent P. and
               Roy, David B. and H{\o}ye, Toke T. and Larriv{\'e}e, Maxim and Rolnick, David},
  booktitle = {Computer Vision -- ECCV 2024},
  series    = {Lecture Notes in Computer Science},
  volume    = {15095},
  pages     = {55--73},
  publisher = {Springer, Cham},
  year      = {2024},
  doi       = {10.1007/978-3-031-72913-3_4}
}

@article{roy2024standardized,
  title   = {Towards a standardized framework for {AI}-assisted, image-based monitoring of nocturnal insects},
  author  = {Roy, D. B. and Alison, J. and August, T. A. and B{\'e}lisle, M. and Bjerge, K. and Bowden, J. J. and
             Bunsen, M. J. and Cunha, F. and Geissmann, Q. and Goldmann, K. and Gomez-Segura, A. and Jain, A. and
             Huijbers, C. and Larriv{\'e}e, M. and Lawson, J. L. and Mann, H. M. and Mazerolle, M. J. and
             McFarland, K. P. and Pasi, L. and Peters, S. and Pinoy, N. and Rolnick, D. and Skinner, G. L. and
             Strickson, O. T. and Svenning, A. and Teagle, S. and H{\o}ye, T. T.},
  journal = {Philosophical Transactions of the Royal Society B},
  volume  = {379},
  number  = {1904},
  pages   = {20230108},
  year    = {2024},
  doi     = {10.1098/rstb.2023.0108}
}
```
