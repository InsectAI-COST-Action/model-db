+++
# ── Identity ────────────────────────────────────────────────────────
title              = "BEEomass"
description        = "EfficientNetV2 modified to produced 'biomass factor' as output."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "regression"
task               = ["Regression"]
architecture       = "EfficientNetV2"
year               = 2026
license            = "CC-BY-4.0"
status             = "published"
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "open"
produces           = ["continuous"]
image_input_size   = "224x224"
developer          = "Baghooee et al."
paper_url          = "https://doi.org/10.32942/X2Q687"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"

# ── The model's own card elsewhere, if it has one ───────────────────

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "zenodo-record"
provider     = "zenodo"
record_id    = "22097250"
url          = "https://zenodo.org/records/22097250/files/2026-08-25_BEEomass_model.zip"
note         = ""

+++

> EfficientNetV2 regression model that estimates the dry biomass of individual arthropods from images.

**Intended use.** Estimating individual dry biomass of terrestrial arthropods from
segmented images of single specimens, as an alternative to drying and weighing each one.
It is designed for images from [EntoScan](https://github.com/darsa-group/EntoScan), a
modified flatbed scanner, but the authors report that it generalises to other calibrated
imaging setups (it was also trained and tested on Biodiscover images). The model does not
predict mass directly. It predicts a size-normalised **Biomass Factor (BF)**, and dry mass
is recovered from BF using the image's known physical scale.

## Architecture and training

- **Architecture:** EfficientNetV2 (variant v2_s), ImageNet-pretrained, with the final
  layer replaced by a single-output regression head (dropout 0.6 → linear → scalar)
- **Task:** Regression (one Biomass Factor value per image)
- **Target:** BF = M^(1/3) / L, in mg^(1/3) mm^-1, where M is dry mass (mg) and L is the
  physical width of the 224 px field of view, L = 25.4 × (224 / s) / DPI (mm), with s the
  resize factor applied to the segmented image. Under isometric scaling BF is constant, so
  it captures body "compactness" rather than absolute size
- **Trained on:** paired images and dry biomass measurements from EntoScan (field-collected
  specimens from pan traps in Denmark, Malaise traps in Sweden, and vacuum sampling, plus
  lab-reared *Drosophila*) and the Biodiscover dataset (2,037 images). Each specimen was
  imaged several times in different poses. Data were split 80/10/10 into train, validation
  and test sets at the specimen level. The combined training data holds 9,481 images of
  3,142 weighed specimens
- **Taxonomic coverage:** terrestrial arthropods, mainly insects (e.g. Diptera,
  Hymenoptera, Coleoptera, Plecoptera, Ephemeroptera, Trichoptera) plus spiders.
  The model is taxon-agnostic and does not classify specimens
- **Loss and optimisation:** MSE on BF. AdamW (learning rate 1e-4, weight decay 1e-5),
  batch size 32, 500 epochs, StepLR halving the learning rate every 100 epochs. The
  checkpoint with the lowest validation loss was kept
- **Augmentation (training only):** scale augmentation (image shrunk by s ~ U(0.5, 1) onto a
  white 224 × 224 canvas, with the BF target adjusted to match), random horizontal flips,
  90° rotations, colour jitter, a random choice of Gaussian blur or sharpening, and a
  ±20% multiplicative jitter on the target
- **Framework:** PyTorch

## Inputs and outputs

- **Input size:** 224x224. Specimens are first segmented from the background (the authors
  use FlatBug), resized so the longest side is 224 px with aspect ratio preserved, then
  padded with white to a square
- **Channel order:** RGB
- **Outputs:** one scalar Biomass Factor per image. Dry mass is recovered as
  M = (BF × L)^3, which requires the acquisition resolution (DPI) and resize factor for
  each image
- **Input modality:** image only (discriminative model)

## Performance

Values from the source publication, measured on the held-out test sets. Confidence
intervals (95%) come from 500 bootstrap iterations, sampling one image per specimen.
The baseline is a linear model on the square root of segmented area.

| Metric | Value | Evaluation set |
| --- | --- | --- |
| R² | 0.95 [0.93, 0.97] | EntoScan test set (area baseline: 0.75) |
| MAE (mg) | 0.08 [0.06, 0.09] | EntoScan test set (area baseline: 0.20) |
| R² | 0.89 [0.81, 0.94] | Biodiscover test set (area baseline: 0.70) |
| MAE (mg) | 0.07 [0.05, 0.10] | Biodiscover test set (area baseline: 0.14) |

The authors also demonstrate the model in two case studies: detecting
temperature-induced size differences in five lab-reared *Drosophila* species, and tracking
seasonal biomass dynamics in field-collected *Pachygnatha degeeri* spiders.

## Limitations

- The Biomass Factor assumes a fairly consistent size–mass relationship. Taxa that depart
  strongly from isometric scaling, or have unusual body forms, may be predicted less
  accurately. Taxa outside the training data have not been evaluated
- Predictions depend on accurate segmentation. Segmentation errors, especially in dense or
  overlapping bulk samples, carry through to the biomass estimate
- Dry mass can only be recovered when the physical scale (DPI) of the image is known, so
  images need a calibrated setup
- The source publication is a preprint and has not been peer reviewed

## License and rights

- **License:** CC-BY-4.0
- **Commercial use:** allowed
- **Restrictions:** Attribution is required by the license. Cite the source publication
  listed under Citation below.
- **Upstream source:** <https://zenodo.org/records/22097250>
- **Code:** <https://github.com/darsa-group/BEEomass>

## Citation

```bibtex
@article{baghooee2026beeomass,
  title   = {EntoScan and BEEomass: a standardized imaging system and a physically
             motivated model for high-throughput dry biomass estimation of arthropods},
  author  = {Baghooee, Melika and Thalheim, Robert and Hasan, Fevziye and Toft, S{\o}ren
             and Kristensen, Torsten Nyg{\aa}rd and Geissmann, Quentin},
  journal = {EcoEvoRxiv},
  year    = {2026},
  doi     = {10.32942/X2Q687},
  note    = {Preprint}
}
```

## How to obtain the weights

From Zenodo record [`22097250`](https://zenodo.org/records/22097250). No authentication is
required. The weights are in the `2026-08-25_BEEomass_model.zip` file. Training and
inference scripts (`02-train.py`, `03-predict.py`) are in the
[BEEomass GitHub repository](https://github.com/darsa-group/BEEomass).
