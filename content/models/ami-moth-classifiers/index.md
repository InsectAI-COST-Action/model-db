+++
# ── Identity ────────────────────────────────────────────────────────
title              = "AMI moth classifiers"
description        = "Global and regional ResNet50 moth species classifiers, a moth/non-moth filter and a 16-order arthropod classifier for crops from nocturnal light traps, as run by the AMI data companion and Antenna."
foundation         = false

# ── Catalogue ───────────────────────────────────────────────────────
category           = "classification"
task               = ["Classification"]
architecture       = ["ResNet50", "ConvNeXt-T"]
base_model         = "timm resnet50 (ImageNet); convnext_tiny_in22k"
year               = 2024
license            = "AGPL-3.0-only"
status             = "published"
training_data      = ["10.5281/zenodo.11358689", "10.15468/dl.6j5bzj", "10.15468/dl.n3zcat", "10.15468/dl.6576q9", "10.15468/dl.hsxw84"]
date               = 2026-09-30

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Global model plus regional models: NE North America, W Europe, Panama, Costa Rica, Anguilla, Kenya-Uganda"
produces           = ["label"]
image_input_size   = "128x128 (Mila models), 300x300 (Turing models)"
taxonomic_coverage = "Lepidoptera: 29,176 species (global); 79 to 5,952 per regional model. Order model: 16 arthropod orders"
developer          = "Rolnick Lab (Mila / McGill), the AMI consortium, and the Alan Turing Institute (Turing models)"
paper_url          = "https://doi.org/10.1007/978-3-031-72913-3_4"
code_url           = "https://github.com/RolnickLab/ami-data-companion"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The files this model ships. The FIRST one is the link the table shows. ──
# Base URL for all files:
# https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/

[[assets]]
key          = "global-moths-2024"
provider     = "url"
filename     = "global_resnet50_20240828_b06d3b3a.pth"
size_bytes   = 333489027
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/classification/global_resnet50_20240828_b06d3b3a.pth"
released     = 2024-08-28
note         = "Global moth species classifier, 29,176 species, ResNet50 at 128 px. Label map: moths/classification/global_category_map_with_names_20240828.json. API slug global_moths_2024."

[[assets]]
key          = "moth-nonmoth"
provider     = "url"
filename     = "moth-nonmoth_resnet50_20240417_b4fe3efe.pth"
size_bytes   = 94373731
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/classification/moth-nonmoth_resnet50_20240417_b4fe3efe.pth"
released     = 2024-04-17
note         = "Binary moth / non-moth filter that runs between the detector and the species classifier. ResNet50 at 128 px. Label map: moths/classification/05-moth-nonmoth_category_map.json."

[[assets]]
key          = "insect-orders-2025"
provider     = "url"
filename     = "convnext_tiny_in22k_worder0.5_wbinary0.5_run2_checkpoint.pt"
size_bytes   = 334241031
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/insect_orders/convnext_tiny_in22k_worder0.5_wbinary0.5_run2_checkpoint.pt"
note         = "16-class order classifier (Lepidoptera, Diptera, Hemiptera, Odonata, Coleoptera, Araneae, Orthoptera, Hymenoptera, Trichoptera, Neuroptera, Opiliones, Ephemeroptera, Plecoptera, Blattodea, Dermaptera, Mantodea). ConvNeXt-T at 128 px, January 2025. Label map: insect_orders/insect_order_category_map.json."

[[assets]]
key          = "quebec-vermont"
provider     = "url"
filename     = "quebec-vermont_resnet50_baseline_20240417_950de764.pth"
size_bytes   = 114822755
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/classification/quebec-vermont_resnet50_baseline_20240417_950de764.pth"
released     = 2024-04-17
note         = "NE North America, 2,497 species (the ECCV paper's ResNet50 baseline). Label map: 01_ami-gbif_fine-grained_ne-america_category_map-with_names.json. API slug quebec_vermont_moths_2023."

[[assets]]
key          = "uk-denmark"
provider     = "url"
filename     = "uk-denmark_resnet50_baseline_20240417_55250a8b.pth"
size_bytes   = 115691491
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/classification/uk-denmark_resnet50_baseline_20240417_55250a8b.pth"
released     = 2024-04-17
note         = "W Europe, 2,603 species (the ECCV paper's ResNet50 baseline). Label map: 02_ami-gbif_fine-grained_w-europe_category_map-with_names.json. API slug uk_denmark_moths_2023."

[[assets]]
key          = "panama-2024"
provider     = "url"
filename     = "panama_resnet50_baseline_20240417_edbb46dd.pth"
size_bytes   = 99570019
url          = "https://object-arbutus.alliancecan.ca/swift/v1/AUTH_3c987b8fc90743469d42899b1fdb48eb/ami-models/moths/classification/panama_resnet50_baseline_20240417_edbb46dd.pth"
released     = 2024-04-17
note         = "Central America (Panama), 636 species. Label map: 03_ami-gbif_fine-grained_c-america_category_map-with_names.json. API slug panama_moths_2024."

+++

> Names moths to species from light-trap crops, with a regional model per checklist, plus a
> moth/non-moth filter and an order-level classifier for everything else.

**Intended use.** The classification stages of the AMI (Automated Monitoring of Insects) pipeline,
run by the [AMI data companion](https://github.com/RolnickLab/ami-data-companion) and the
[Antenna](https://github.com/RolnickLab/antenna) platform. Each crop from the
[AMI insect detector](../ami-insect-detector/) is processed in three steps:
1. The **moth/non-moth** filter checks it.
2. Moths go to a **species classifier**: pick the regional model matching your checklist, or the
   global one.
3. Optionally, the **order classifier** labels the other arthropods.

## Architecture and training

- **Species classifiers:** ResNet50 (timm, ImageNet-initialised), trained on **AMI-GBIF**,
  which is GBIF occurrence images for regional moth checklists.
  - Settings: 128 px, 30 epochs, RandAugment plus *MixRes* (mixed-resolution augmentation, which
    simulates low-resolution trap crops).
  - The April 2024 NE-America, W-Europe and Panama files are the ResNet50 baselines of Jain et al.
    (ECCV 2024); their species counts match the paper's Table 1.
  - The paper's best model (ConvNeXt-B) is **not** the one deployed.
  - The global model (29,176 species, August 2024) follows the same recipe.
- **Turing models** (Costa Rica, Kenya-Uganda, Anguilla): ResNet50 at 300 px, trained by the Alan
  Turing Institute team with the AMI tooling.
- **Moth/non-moth:** ResNet50 at 128 px, trained on AMI-GBIF moths plus about 350k non-moth images.
- **Order classifier:** ConvNeXt-T (`convnext_tiny_in22k`) at 128 px, with 16 arthropod orders,
  trained at Mila in January 2025.
- **Training code:** [RolnickLab/ami-ml](https://github.com/RolnickLab/ami-ml).

## Inputs and outputs

- **Input:** one crop per call, square-resized to the model's input size (128 or 300 px), with
  ImageNet normalisation.
- **Output:** softmax scores over the model's label map.
- **Label maps** are separate JSON files at the same base URL (named in each asset note) and map
  indices to species names or GBIF keys.
- **In the AMI API** each classification carries the top label, the full `labels`, `scores` and
  `logits` vectors, and a `taxon_rank`: SPECIES, SUPERFAMILY for the binary model, or ORDER.

## Performance

Jain et al. (ECCV 2024) report micro top-1 accuracy (in %) on **AMI-Traps**: 2,893 expert-annotated
trap images and 52,948 insects from NE America, W Europe and Central America. The model is the
deployed ResNet50 architecture.

| Model | Species (macro) | Genus | Family | Evaluation set |
| --- | --- | --- | --- | --- |
| NE-America (quebec-vermont) | 71.86 (64.96) | 80.07 | 90.44 | AMI-Traps, NE America |
| W-Europe (uk-denmark) | 79.39 (72.84) | 78.95 | 89.13 | AMI-Traps, W Europe |
| C-America (panama-2024) | – | 47.44 | 69.18 | AMI-Traps, C America (no species-level labels) |

Moth/non-moth ResNet50 on all 51,120 AMI-Traps crops: accuracy 86.48, precision 68.31, recall
95.03, F1 79.48. On crops larger than 150 px: accuracy 92.95, F1 93.70.

The global model, the Turing models, the order classifier and the Panama-2023 model have no
published metrics.

## Limitations

- **Closed set, Lepidoptera only** (species models). A moth not on the regional checklist still
  receives one of its species. Match the model to your region.
- **Domain gap.** Trained on human-taken GBIF photos. Accuracy on held-out GBIF images is about
  87 %, against 72–79 % on real trap crops.
- **Long tail.** Species with few training images reach only 27–49 % on AMI-GBIF.
- **Low validation coverage.** The Central America and Turing models have little or no in-the-wild
  validation.
- **Small crops.** Moth/non-moth precision drops on small crops, most of which are non-moths.
- **Not the best model.** The deployed models are ResNet50 baselines, not the paper's
  best-performing ConvNeXt-B.
- **Hosting.** The weights live only on a Digital Research Alliance of Canada object store and are
  unpinned. A legacy file (Turing-UK) already returns 404.

## How to obtain the weights

Direct HTTPS download from the object store, with no authentication. The `AUTH_…` segment of the
URL is required. The paths are defined in `trapdata/ml/models/classification.py` and the base URL
in `trapdata/settings.py` of ami-data-companion, curated at commit
`55d0787570f8c9d92c450f4fb65a58dd25cf6634`. `trapdata` downloads them automatically. Each
classifier needs its label-map JSON, from the same base URL.

The Alan Turing Institute models (Costa Rica, 5,952 species; Kenya-Uganda, 3,045; Anguilla, 79;
ResNet50 at 300 px, no published metrics) are at the same base URL:
`moths/classification/turing-{costarica_v03_resnet50_2024-06-04-16-17,kenya-uganda_v01_resnet50_2024-11-19-18-44,anguilla_v01_resnet50_2024-06-28-17-01}_state.pt`.

Older models are defined in the same file but not exposed by the API:
- UK-Denmark mixres 2023
- Quebec-Vermont mixres 2022
- Panama 2022 (148 species)
- Panama 2023 (1,060 species)
- the 2022 EfficientNetV2-B3 moth/non-moth model

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
```
