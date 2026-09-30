+++
# ── Identity ────────────────────────────────────────────────────────
title              = "SAM 3"
description        = "Promptable foundation model that finds, segments and tracks every instance of a concept given as a short text phrase or an example box, in images and video."
foundation         = true

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection", "Instance Segmentation", "Tracking"]
architecture       = ["ViT (ViTDet) + DETR detector + SAM 2 tracker"]
base_model         = ""
year               = 2025
license            = "custom"
status             = "published"
date               = 2026-09-30

# Optional - delete a line to take the default shown.
vocabulary_scope   = "open"
geographic_scope   = "Global"
produces           = ["bbox", "mask", "track"]
image_input_size   = "1008x1008"
input_modality     = ["text", "image", "box", "point", "mask"]
developer          = "Meta Superintelligence Labs (Carion, Gustafson, Hu et al.)"
paper_url          = "https://arxiv.org/abs/2511.16719"
code_url           = "https://github.com/facebookresearch/sam3"
pretraining_data   = "SA-Co (Meta data engine, over 4M unique concepts)"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch", "Safetensors"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "facebook/sam3"
hf_revision        = "3c879f39826c281e95690f02c7821c4de09afae7"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "sam3"
provider     = "huggingface"
filename     = "sam3.pt"
size_bytes   = 3450062241
gated        = true
url          = "https://huggingface.co/facebook/sam3/tree/3c879f39826c281e95690f02c7821c4de09afae7"
released     = 2025-11-19
note         = "Original SAM 3 checkpoint (848M parameters) for the facebookresearch/sam3 code. The same repo has model.safetensors (3,439,938,512 bytes) for transformers. Gated: request access on Hugging Face and log in before downloading."

[[assets]]
key          = "sam3.1"
provider     = "huggingface"
filename     = "sam3.1_multiplex.pt"
size_bytes   = 3502755717
gated        = true
url          = "https://huggingface.co/facebook/sam3.1/tree/daa63191845a41281374e725f4c9e51c7a824460"
released     = 2026-03-27
note         = "SAM 3.1 Object Multiplex: shared-memory multi-object tracking, significantly faster in video. Needs the latest facebookresearch/sam3 code. Same license and gate."
+++

> Segments every instance of a concept, given as a phrase such as "moth" or "bee", or as one example box.

**Intended use.** Open-vocabulary detection, segmentation and tracking without training. For insect
work this means:
- **Annotation assist:** prompt "insect" or "moth" on trap images to get masks you correct, rather
  than drawing them.
- **Zero-shot baselines** for new trap designs.
- **Video tracking** of prompted individuals.

It returns *where* the instances are, not *which species*. Pair it with a classifier such as
[lepinet](../lepinet/) or [BioCLIP 2](../bioclip-2/) for identification. Unlike SAM 1 and SAM 2,
which segment the one object you click, SAM 3 finds *all* matching instances from a single prompt.

## Architecture and training

- **Model:** 848M parameters in total. A detector and a tracker share one vision encoder, a ViT
  with patch size 14, 32 layers and width 1024, run at 1008 px.
- **Detector:** DETR-based, conditioned on a text phrase, geometry (points, boxes, masks) and image
  exemplars.
- **Tracker:** inherits the SAM 2 transformer encoder-decoder, for video and interactive
  refinement.
- **Training data:** SA-Co, built by a data engine with humans and AI in the loop. It annotated over
  4 million unique concepts, which the authors call the largest open-vocabulary segmentation
  dataset to date.
- **SAM 3.1** (March 2026) adds Object Multiplex, a shared memory for tracking many objects at once.

## Inputs and outputs

- **Input:** an RGB image or video (a JPEG folder or MP4), resized to 1008x1008. Prompts can be a
  short noun phrase, positive or negative example boxes, points or masks.
- **Output:** one mask, box and score per instance. Video also gives per-frame masks with a
  persistent object ID.
- **Loading:** the `sam3` package (`build_sam3_image_model`, `Sam3Processor`) or `transformers`.
- **Requirements:** Python 3.12 or later, PyTorch 2.7 or later, and a CUDA GPU.

## Prompting for insects

The text prompt is a **short noun phrase**, not a sentence and not a class list. SAM 3 returns
every instance matching that one concept, so run one prompt per concept you want.

- **Broad:** `insect` or `arthropod` to find every specimen on a trap sheet, sticky plate or
  flower photo. This is a good first pass for counting or for making crops for a classifier.
- **Groups** at roughly the level of common names: `moth`, `butterfly`, `bee`, `wasp`, `fly`,
  `beetle`, `ladybug`, `ant`, `dragonfly`, `grasshopper`, `spider`, `caterpillar`.
- **Parts and states:** `insect wing`, `antenna`, `insect leg`, `pupa`, `egg cluster`. These help
  with trait measurements or life-stage screening.
- **Context:** `flower`, `leaf`, `sticky trap` segment the surroundings, for example to measure
  flower visits.
- **Visual exemplars** instead of text: draw one box around a specimen you want, and SAM 3 finds the
  others that look like it. Add a *negative* box on debris, a shadow or a trap edge to suppress
  that kind of false positive. This is the practical route for taxa that have no common name.
- **Video:** give a prompt on one frame, and the tracker keeps the same ID for each individual
  through the clip. You can add or remove objects with clicks.

Scientific names (for example "Bombus terrestris") and fine distinctions between species are
outside what SAM 3 was trained or evaluated for. Use the prompt to find the specimens, then
identify them with a dedicated classifier.

## Performance

All numbers are as reported by the authors, on general-domain benchmarks. There is no
insect-specific evaluation.

| Benchmark | Metric | SAM 3 | Human |
| --- | --- | --- | --- |
| SA-Co/Gold, instance segmentation | cgF1 | 54.1 | 72.8 |
| SA-Co/Gold, box detection | cgF1 | 55.7 | 74.0 |
| LVIS, instance segmentation | AP | 48.5 | – |
| COCO, box detection | AP | 56.4 | – |
| SA-V test, video | cgF1 / pHOTA | 30.3 / 58.0 | 53.1 / 70.5 |

Source: [facebookresearch/sam3 README](https://github.com/facebookresearch/sam3) and Carion et al.
(2025). cgF1 is the paper's concept-level F1 for promptable concept segmentation.

## Limitations

- **Concepts, not species.** Prompts are short noun phrases. "Insect", "moth" or "bee" work at that
  level. Latin binomials and fine distinctions between similar taxa are not what it was trained or
  evaluated for.
- **No insect benchmark.** Expect misses on very small insects in high-resolution trap images at
  1008 px (tile large images), and false positives on debris, shadows and trap texture.
- **Heavy.** 848M parameters and about 3.4 GB per checkpoint; a CUDA GPU is required by the
  reference code. Not an edge model.
- **Gated.** Every user must request access on Hugging Face and authenticate before downloading.

## How to obtain the weights

Both repositories are **gated**: request access on
[facebook/sam3](https://huggingface.co/facebook/sam3) or
[facebook/sam3.1](https://huggingface.co/facebook/sam3.1), then log in (`hf auth login`) before
downloading. The asset links above are pinned to the curated commits.

**License:** the **SAM License** (Meta, November 2025), which covers both code and weights. It is a
royalty-free license that permits use, modification, redistribution and commercial use. It requires
passing the license on with any redistribution and complying with trade controls, and it excludes
ITAR and other prohibited end uses. This is not an OSI license, so it is recorded here as `custom`.
The full text is the
[LICENSE file upstream](https://github.com/facebookresearch/sam3/blob/2345a4ad109ac29c569da749c91d84f10dc08c40/LICENSE).

## Citation

```bibtex
@misc{carion2025sam3segmentconcepts,
  title         = {SAM 3: Segment Anything with Concepts},
  author        = {Nicolas Carion and Laura Gustafson and Yuan-Ting Hu and Shoubhik Debnath and Ronghang Hu and
                   Didac Suris and Chaitanya Ryali and Kalyan Vasudev Alwala and Haitham Khedr and Andrew Huang and
                   Jie Lei and Tengyu Ma and Baishan Guo and Arpit Kalla and Markus Marks and Joseph Greer and
                   Meng Wang and Peize Sun and Roman Rädle and Triantafyllos Afouras and Effrosyni Mavroudi and
                   Katherine Xu and Tsung-Han Wu and Yu Zhou and Liliane Momeni and Rishi Hazra and Shuangrui Ding and
                   Sagar Vaze and Francois Porcher and Feng Li and Siyuan Li and Aishwarya Kamath and Ho Kei Cheng and
                   Piotr Dollár and Nikhila Ravi and Kate Saenko and Pengchuan Zhang and Christoph Feichtenhofer},
  year          = {2025},
  eprint        = {2511.16719},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  url           = {https://arxiv.org/abs/2511.16719}
}
```
