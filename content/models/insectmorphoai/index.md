+++
# ── Identity ────────────────────────────────────────────────────────
title              = "InsectMorphoAI"
description        = "Measures insect body length from images with an oriented-box detector, and estimates body volume and biomass of bristle flies from head, thorax and abdomen masks."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection-homogeneous"
task               = ["Object Detection", "Instance Segmentation"]
architecture       = "YOLOv8-obb, YOLOv8-seg"
base_model         = "Ultralytics yolov8m-obb (DOTA-pretrained); yolov8m-seg (COCO-pretrained)"
year               = 2026
license            = "MIT"
status             = "published"
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
produces           = ["bbox", "mask", "continuous"]
taxonomic_coverage = "OBB: Diptera, Hymenoptera, Coleoptera. Segmentation: Tachinidae only (head, thorax, abdomen)"
developer          = "Shirali, Hossein et al."
paper_url          = "https://doi.org/10.1016/j.ecoinf.2026.103854"
code_url           = "https://gitlab.kit.edu/kit/iai/ber/insectmorphoAI"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = "PyTorch"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "obb"
provider     = "url"
variant      = "YOLOv8m-obb (Rapid Scan, length)"
filename     = "data/models/YOLOv8_obb/yolov8m_obb3_best.pt"
url          = "https://gitlab.kit.edu/kit/iai/ber/insectmorphoAI/-/raw/main/data/models/YOLOv8_obb/yolov8m_obb3_best.pt"
note         = "In the InsectMorphoAI GitLab repository, main branch (not pinned to a commit)."

[[assets]]
key          = "seg"
provider     = "url"
variant      = "YOLOv8m-seg (Detailed Analysis, Tachinidae)"
filename     = "data/models/YOLOv8_seg/1_yolov8m_seg_s2_v1.pt"
url          = "https://gitlab.kit.edu/kit/iai/ber/insectmorphoAI/-/raw/main/data/models/YOLOv8_seg/1_yolov8m_seg_s2_v1.pt"
note         = "In the InsectMorphoAI GitLab repository, main branch (not pinned to a commit)."

+++

> Measures insect body length from images with an oriented-box detector, and estimates body volume and biomass of bristle flies from head, thorax and abdomen masks.

**Intended use.** Non-destructive, specimen-level morphometrics from 2D images of single,
ethanol-preserved insects taken under controlled lighting on a plain background. InsectMorphoAI
has two modules. **Rapid Scan** is an oriented-bounding-box (OBB) detector that gives a
rotation-invariant body length for insects from several orders. **Detailed Analysis** is an
instance-segmentation model, trained only on bristle flies (Diptera: Tachinidae), that
outlines the head, thorax and abdomen. From these masks the software derives curvilinear body
length, an approximate 3D volume and a body-only biomass estimate. Specimens are kept intact,
so they stay available for DNA barcoding and other downstream work. The models ship inside a
Docker app with a Streamlit GUI and a command-line tool for batch processing.

## Architecture and training

**Rapid Scan (OBB module)**

- **Architecture:** YOLOv8m-obb, fine-tuned from DOTA-pretrained weights. It was chosen from
  the five YOLOv8-obb sizes (nano to extra-large) as the best balance of accuracy and speed
- **Task:** oriented object detection, one class (the insect body)
- **Trained on:** 815 images of 804 specimens from several insect orders, including Diptera,
  Hymenoptera and Coleoptera. Boxes cover the head, thorax and abdomen and leave out wings,
  legs and antennae. Split 85:15 (train:validation) by specimen
- **Training:** 200 epochs, AdamW (learning rate 0.01, batch size 16), with random
  rotation, scaling, flipping, mosaic and erasing. Best validation mAP50 0.995 and
  mAP50–95 0.846

**Detailed Analysis (segmentation module)**

- **Architecture:** YOLOv8m-seg. YOLOv8-seg beat Mask R-CNN (ResNet-50-FPN) on an initial
  dataset, and the medium size was the best balance of accuracy and speed
- **Task:** instance segmentation with three classes: head, thorax, abdomen
- **Trained on:** 1,320 images of 702 Tachinidae specimens from 105 species, split
  70:15:15 by specimen. The first 820 images were annotated with Grounding DINO and SAM.
  The model trained on them pseudo-labelled 500 more, which an expert corrected in
  LabelMe, including the outlines of body parts hidden behind wings or legs
- **Training:** fine-tuned from the model trained on the initial 820 images, which beat
  training from COCO-pretrained weights. Adam, 100 epochs, learning rate 0.01, weight
  decay 0.0005

**Both modules**

- **Images:** taken with the Entomoscope system and focus-stacked in Helicon Focus. The
  datasets are on Zenodo ([10.5281/zenodo.18959238](https://doi.org/10.5281/zenodo.18959238))
- **Framework:** PyTorch and Ultralytics YOLOv8, with OpenCV for post-processing
  (Python 3.11)

## Inputs and outputs

- **Input:** an RGB image of one specimen per image. The paper does not report the
  training or inference image size
- **Calibration:** every measurement needs a pixel-to-mm scaling factor k̂ for the imaging
  setup, measured from a reference object such as a micrometer slide imaged under the
  same conditions. Profiles for Entomoscope camera–lens setups are built in. For other
  setups, enter a custom factor, and calibrate again for each optical configuration
- **Rapid Scan outputs:** an oriented box. Length (mm) is the box's longest side × k̂. The
  box also gives a width, but the authors did not evaluate it. The app can add a biomass
  estimate from standard length–weight relationships
- **Detailed Analysis outputs:** head, thorax and abdomen masks. From these the software:
  - fits a natural cubic spline through the centre of each mask to get curvilinear length
  - estimates volume by stacking frustums (truncated cones) along that spline, treating
    each cross-section as a circle with the mask's local width as diameter, then
    converting with k̂³
  - converts volume V (mm³) to body-only weight W (g) with the built-in Tachinidae
    calibration: W_wet = 0.0314·V − 0.0135 and W_dry = 0.0050·V − 0.0018 (valid for
    V ≥ 0.4 mm³)
- **Export:** one CSV with all measurements, plus optional annotated images

## Performance

From the source publication. The validation set was 100 Tachinidae specimens from 23
species (mean length 9.36 mm, mean body-only dry weight 6.1 mg), kept apart from the
training data. The reference lengths were measured by hand on a Zeiss Axio Zoom V16
photomicroscope. Weights were measured after the legs were removed.

**Length**

| Module | Metric | Value | Evaluation set |
| --- | --- | --- | --- |
| Rapid Scan (OBB) | R² / Pearson R | 0.976 / 0.988 [0.982–0.992] | 100 Tachinidae vs. manual linear length |
| Rapid Scan (OBB) | MAE / RMSE | 0.211 mm (≈2.3% of mean length) / 0.290 mm | same |
| Detailed Analysis (seg) | R² / Pearson R | 0.953 / 0.976 [0.964–0.984] | 100 Tachinidae vs. manual curvilinear length |
| Detailed Analysis (seg) | MAE / RMSE | 0.309 mm (≈3.3%) / 0.408 mm | same |

**Body-only biomass (R², linear fit)**

| Predictor | Wet weight after leg removal | Body-only dry weight |
| --- | --- | --- |
| OBB linear length | 0.629 | 0.610 |
| Segmentation curvilinear length | 0.658 | 0.627 |
| Segmentation frustum volume | 0.880 | 0.823 (MAE 0.0010 g, RMSE 0.0015 g) |

The segmentation model reached a mask mAP50 of 0.995 on its held-out test set. The OBB
module's accuracy on orders other than Diptera was only shown in example images, with no
numbers.

## Limitations

- **Volume and biomass are Tachinidae-only.** The segmentation model and the
  volume-to-weight equations were trained and validated on one family. The authors warn
  that the segmentation model will fail on insects with a different body plan, such as
  beetles or stick insects. Each new family needs its own annotations, training and
  weight calibration
- **The volume assumes a round body.** Each cross-section is treated as a circle. This
  suits the roughly cylindrical tachinid body, but volume will likely be overestimated for
  dorsoventrally flattened taxa, and the error is hard to predict for laterally compressed
  or irregular shapes. Dense hairs, folded wings, damage and legs covering the body outline
  also distort the widths
- **Body-only biomass.** Volume comes from the head, thorax and abdomen, so the estimates
  leave out appendages. In the validation set, dried legs were 16.99% ± 4.12% of total dry
  weight. The equations should not be used outside the validated range (V ≥ 0.4 mm³)
- **Controlled imaging only.** Both models were trained on ethanol-preserved specimens
  imaged one at a time with the Entomoscope. Field photos, cluttered backgrounds, bulk
  samples with overlapping insects, damaged specimens, and dry-pinned, point-mounted or
  critical-point-dried material have not been tested. Heavily twisted specimens or
  non-standard views may give worse estimates
- **Cross-order OBB accuracy is not quantified.** The OBB model was trained on several
  orders, but its length error was measured only on Tachinidae
- **Calibration is essential.** A wrong or reused pixel-to-mm factor scales every length
  linearly and every volume cubically
- **One specimen per image.** The pipeline has no logic for separating touching specimens
  in bulk images

## License and rights

- **License:** MIT, the license of the InsectMorphoAI GitLab repository, which also holds
  the weight files. The paper is open access under CC-BY-4.0
- **Commercial use:** allowed under MIT. However, the weights are Ultralytics YOLOv8
  checkpoints, and running them needs the `ultralytics` package, which is AGPL-3.0. For
  closed-source commercial use, check whether you need an Ultralytics Enterprise License
- **Hosting:** the weights are committed to the `main` branch of a KIT GitLab repository,
  with no DOI or release tag. They could change or be removed without a version bump
- **Upstream source:** <https://gitlab.kit.edu/kit/iai/ber/insectmorphoAI>

## Citation

```bibtex
@article{shirali2026insectmorphoai,
  title     = {InsectMorphoAI: A deep learning framework for automated insect morphometrics
               and biomass estimation with taxon-specific volumetric validation},
  author    = {Shirali, Hossein and Ascenzi, Aleida and W{\"u}hrl, Lorenz and Beyer, Nils
               and Di Lorenzo, Noemi and Vaccarella, Emanuele and Klug, Nathalie
               and Meier, Rudolf and Cerretti, Pierfilippo and Pylatiuk, Christian},
  journal   = {Ecological Informatics},
  volume    = {96},
  pages     = {103854},
  year      = {2026},
  publisher = {Elsevier},
  doi       = {10.1016/j.ecoinf.2026.103854}
}
```

## How to obtain the weights

Both weight files are in the InsectMorphoAI GitLab repository. No account is needed:

| Module | File |
| --- | --- |
| Rapid Scan (YOLOv8m-obb) | `data/models/YOLOv8_obb/yolov8m_obb3_best.pt` |
| Detailed Analysis (YOLOv8m-seg, Tachinidae) | `data/models/YOLOv8_seg/1_yolov8m_seg_s2_v1.pt` |

The easiest way to use them is to clone the repository and run the Docker app
(`install_app.sh` or `install_app.bat`), which serves the GUI at `http://localhost:8501`.
For large batches, install the requirements in a Python environment and use the headless
tool:

```bash
python utils/ultimate_headless.py --input ./images --output ./results --analysis-type both
```

Use `--analysis-type obb` or `seg` to run one module only, and `--custom-lens-factor` (mm/px)
for imaging setups without a built-in profile.
