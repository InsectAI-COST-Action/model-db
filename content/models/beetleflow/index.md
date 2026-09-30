+++
# ── Identity ────────────────────────────────────────────────────────
title              = "BeetleFlow"
description        = "Segments the body parts (head, pronotum, elytra, legs, antennae, and more) of pinned ground-beetle specimens in cropped images, for trait measurement."
foundation         = false

# ── Catalogue ───────────────────────────────────────────────────────
category           = "trait-quantification"
task               = ["Semantic Segmentation"]
architecture       = ["Mask2Former", "Swin Transformer (Swin-L)"]
base_model         = "facebook/mask2former-swin-large-ade-semantic"
year               = 2025
license            = "MIT"
status             = "published"
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "USA (NEON sites)"
produces           = ["mask"]
output_format      = ["beetleflow-color-mask", "beetleflow-color-mask"]
image_input_size   = "512x512"
input_modality     = ["image"]
taxonomic_coverage = "Carabidae (NEON pitfall-trap ground beetles)"
developer          = "Fangxun Liu, S M Rayeed, Samuel Stevens et al. (Imageomics Institute)"
paper_url          = "https://doi.org/10.48550/arXiv.2511.00255"
code_url           = "https://github.com/Imageomics/BeetleFlow"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["Safetensors"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "imageomics/BeetleFlow"
hf_revision        = "521d768f2cbb89066b98396ac79b4fd5590d7bae"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "hf-repo"
provider     = "huggingface"
repo_id      = "imageomics/BeetleFlow"
revision     = "521d768f2cbb89066b98396ac79b4fd5590d7bae"
revision_kind = "commit"
gated        = false
url          = "https://huggingface.co/imageomics/BeetleFlow"
note         = "Two checkpoints in subfolders, 5-class and 9-class. transformers loads either with subfolder=\"5-class\" or \"9-class\"."

[[assets]]
key          = "weights-5-class"
provider     = "huggingface"
repo_id      = "imageomics/BeetleFlow"
filename     = "5-class/model.safetensors"
revision     = "521d768f2cbb89066b98396ac79b4fd5590d7bae"
revision_kind = "commit"
size_bytes   = 865903448
sha256       = "2867e36bd9882ab82d36b707e0228dc003df5a1f64928b43f6a66ca42407aef1"
url          = "https://huggingface.co/imageomics/BeetleFlow/resolve/521d768f2cbb89066b98396ac79b4fd5590d7bae/5-class/model.safetensors"
note         = "Head, pronotum, elytra, legs, antennae (+ background). Needs 5-class/config.json alongside."

[[assets]]
key          = "weights-9-class"
provider     = "huggingface"
repo_id      = "imageomics/BeetleFlow"
filename     = "9-class/model.safetensors"
revision     = "521d768f2cbb89066b98396ac79b4fd5590d7bae"
revision_kind = "commit"
size_bytes   = 865907576
sha256       = "ab798ad6e661c99a34516b132ae36e647558dfd09af8830f89c91947a2ac0b0e"
url          = "https://huggingface.co/imageomics/BeetleFlow/resolve/521d768f2cbb89066b98396ac79b4fd5590d7bae/9-class/model.safetensors"
note         = "Adds eyes, mouthparts, tail and pin to the 5-class scheme. Needs 9-class/config.json alongside."
+++

> Segments the body parts (head, pronotum, elytra, legs, antennae, and more) of pinned ground-beetle specimens in cropped images, for trait measurement.

**Intended use.** Pixel-level segmentation of body parts on cropped images of
single, pinned ground beetles, so that part-specific traits (elytra length,
pronotum area and so on) can be measured at scale. It is the segmentation stage
of the BeetleFlow pipeline (detection → cropping → segmentation) from the
Imageomics Institute. It does not find beetles in an image and does not identify
them.

## Architecture and training

Mask2Former with a Swin-Large backbone, fine-tuned from
`facebook/mask2former-swin-large-ade-semantic`. Two checkpoints are released:

| Checkpoint | Parts (besides background) | Labelled beetles (train / test) |
| --- | --- | --- |
| 5-class | head, pronotum, elytra, legs, antennae | 272 / 68 |
| 9-class | head, eyes, mouthparts, pronotum, elytra, tail, legs, antennae, pin | 264 / 66 |

Training images are manually annotated pinned specimens from the
[Beetles as Sentinel Taxa](https://huggingface.co/datasets/imageomics/sentinel-beetles)
dataset (NEON pitfall-trap carabids, CC BY 4.0). Trained for 30 epochs at
512×512 with AdamW (lr 1e-4) on one A100.

## Inputs and outputs

Input: an RGB crop of one specimen, resized to 512×512 and normalised with the
ADE20K mean and std by `Mask2FormerImageProcessor`. Output: a per-pixel class
map over the part labels of the chosen checkpoint. Crops are expected to come
from the BeetleFlow detection and cropping stages; see the
[repository](https://github.com/Imageomics/BeetleFlow) for batch inference.

## Performance

As reported on the model card, on the held-out BeetleFlow segmentation test
split (68 images for 5-class, 66 for 9-class), at 512×512:

| Checkpoint | Mean IoU | Mean accuracy |
| --- | --- | --- |
| 5-class | 0.851 | 0.910 |
| 9-class | 0.774 | 0.866 |

Large structures segment well (elytra and pronotum IoU > 0.9). Thin or small
parts do worse: antennae 0.66 (5-class), and in the 9-class model tail 0.53,
mouthparts 0.60 and eyes 0.68.

## Limitations

- Trained only on **pinned ground beetles (Carabidae) photographed under museum
  lighting** at NEON. Expect degradation on other beetle families, other
  preparations, and any field or trap photographs.
- **Not usable for other insect orders** without fine-tuning. The part labels
  (pronotum, elytra) are beetle-specific.
- Needs a **clean single-specimen crop**. Poor upstream cropping lowers mask
  quality, and it cannot handle full trays or several specimens in one image.
- The test sets are small (66–68 images) and come from the same source as the
  training data, so the reported IoU says nothing about out-of-distribution use.
- Thin appendages (antennae, legs, tail) are the least reliable, which matters
  for traits measured from them.

## License and rights

- **License:** MIT
- **Commercial use:** allowed
- **Restrictions:** None stated. The training images are CC BY 4.0.
- **Upstream source:** <https://huggingface.co/imageomics/BeetleFlow>

## How to obtain the weights

Open on Hugging Face, no gate. Links above are pinned to commit `521d768`. Each checkpoint is about
866 MB of Safetensors and loads with `transformers`
(`Mask2FormerForUniversalSegmentation.from_pretrained("imageomics/BeetleFlow", subfolder="5-class")`).

## Citation

```bibtex
@inproceedings{liu2025beetleflow,
  title     = {BeetleFlow: An Integrative Deep Learning Pipeline for Beetle Image Processing},
  author    = {Liu, Fangxun and Rayeed, S M and Stevens, Samuel and East, Alyson and Chiang, Cheng Hsuan and Lee, Colin and Yi, Daniel and Yang, Junke and Naik, Tejas and Wang, Ziyi and Kilrain, Connor and Buckwalter, Elijah H. and Hou, Jiacheng and Bueno, Saul Ibaven and Wang, Shuheng and Ma, Xinyue and Liu, Yifan and Tao, Zhiyuan and Zhang, Ziheng and Sokol, Eric and Belitz, Michael and Record, Sydne and Stewart, Charles V. and Chao, Wei-Lun},
  booktitle = {NeurIPS 2025 Workshop for Imageomics: Discovering Biological Knowledge from Images Using AI},
  year      = {2025}
}
```

The authors also ask that the
[sentinel-beetles dataset](https://doi.org/10.57967/hf/8716) be cited.

## Output format probe

The author batch_inference.py script was run with the 5-class checkpoint and an author test image. It saved an RGB palette mask and an additive overlay at the original 301 × 154 resolution. The 9-class checkpoint was not tested. The script increments output filenames per folder, so multiple same-extension images in a folder overwrite each other.

Probe date: 2026-09-30. Reproducible setup and evidence are in
[src/probe](https://github.com/InsectAI-COST-Action/model-db/tree/main/src/probe).
