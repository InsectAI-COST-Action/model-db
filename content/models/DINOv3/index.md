+++
# ═══════════════════════════════════════════════════════════════════════════════
#  A model card for the Insect AI Model Zoo.
# ═══════════════════════════════════════════════════════════════════════════════
#
#  To add a model:
#
#      cp -r template content/models/your-model-id
#      #  edit content/models/your-model-id/index.md
#      ./scripts/serve.sh
#
#  Name the folder in kebab-case. A model with a name of its own uses it -
#  `flatbug`, `arthronat`. A model known only as "the one from that paper" uses
#  <firstauthor>-<year>-<descriptor>, e.g. `marin-2025-pollinator-yolov5`.
#
#  Everything between the +++ lines is checked when the site builds. Get one
#  wrong and the build stops and tells you which file and what to write, in
#  plain language. You do not have to run a separate command to find out.
#
#  Every field the site displays is in this file. Anything else you want to say
#  goes in the prose below the closing +++, where you can say it in a sentence
#  instead of in a field.

# ── Identity ──────────────────────────────────────────────────────────────────

title              = "DINO v3"
description        = "Vision foundation model that produces dense feature maps for a variety of contexts without re-training; especially useful for assisted annotation or as a baseline for specialised models."
foundation         = true

# ── Catalogue ─────────────────────────────────────────────────────────────────

purpose            = ["Model embeddings"]
task               = ["Embedding"]
architecture       = ["Vision Transformer (ViT)", "ConvNeXt"] 
# base_model          = "" 
year               = 2025                        # year of publication or release
license            = "custom"                    # SPDX identifier where one exists
status             = "published" 

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-30 
vocabulary_scope   = "closed" 
geographic_scope   = "Global" 
# Optional: one verified output profile per architecture; see static/formats/README.md.
# output_format    = ["ultralytics-detect-json"]
produces           = ["embedding"]                    # bbox | mask | label | count | track | embedding
image_input_size         = "any"                  # Supports variable resolution via RoPE (256×256 to 4096×4096)
input_modality     = ["image"] 
developer          = "Facebook (Meta AI), UC Berkeley" 
paper_url          = "https://arxiv.org/abs/2508.10104" 

# ── Weights ───────────────────────────────────────────────────────────────────
#
# Where to download the model. The FIRST block is the link the catalogue table
# shows. Add another only if the model genuinely ships several files, the way
# FlatBug ships a YOLOv8n/s/m/l ladder.
#
# Weights are never committed here. GitHub refuses files over 100 MB and the
# authors host them anyway.

[[assets]]
key      = "vit-s-16"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-vits16-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 50331648  # ~48MB
gated    = true
note     = "ViT-Small/16 (21M params) — fastest inference, suitable for edge devices (Jetson Orin NX: 15-30 FPS)"

[[assets]]
key      = "vit-splus-16"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-vits16plus-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 69795840  # ~66MB
gated    = true
note     = "ViT-Small+/16 (29M params) — improved accuracy over S variant"

[[assets]]
key      = "vit-b-16"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-vitb16-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 348966093  # ~333MB
gated    = true
note     = "ViT-Base/16 (86M params) — recommended balance for most research applications"

[[assets]]
key      = "vit-l-16"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 1205223424  # ~1.1GB
gated    = true
note     = "ViT-Large/16 (300M params) — high-accuracy frozen backbone for complex downstream tasks"

[[assets]]
key      = "vit-hplus-16"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-vith16plus-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 3435973836  # ~3.2GB
gated    = true
note     = "ViT-H+/16 (840M params) — near-7B performance at manageable compute cost"

[[assets]]
key      = "vit-7b-16"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-vit7b16-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 14000000000  # ~14GB (estimate; exact size TBD)
gated    = true
note     = "ViT-7B/16 (7B params) — largest variant; requires 4-8 A100 GPUs for inference; state-of-the-art frozen features"

# ConvNeXt family pretrained on web images (LVD-1689M)

[[assets]]
key      = "convnext-tiny"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-convnexttiny-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 50331648  # ~48MB (estimate)
gated    = true
note     = "ConvNeXt-Tiny (29M params) — CNN alternative for edge deployment with ViT-compatible interfaces"

[[assets]]
key      = "convnext-small"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-convnextsmall-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 89128960  # ~85MB (estimate)
gated    = true
note     = "ConvNeXt-Small (50M params)"

[[assets]]
key      = "convnext-base"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-convnextbase-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 179093504  # ~171MB (estimate)
gated    = true
note     = "ConvNeXt-Base (89M params)"

[[assets]]
key      = "convnext-large"
provider = "huggingface"
url      = "https://huggingface.co/facebook/dinov3-convnextlarge-pretrain-lvd1689m"
filename = "model.safetensors"
size_bytes = 400896000  # ~382MB (estimate)
gated    = true
note     = "ConvNeXt-Large (198M params)"

# ── The model's own card, if it has one elsewhere ─────────────────────────────
#
# If the authors already keep a card on Hugging Face, point at it rather than
# copying it here - a copy starts drifting the moment they edit theirs.
#
# hf_revision is a COMMIT HASH, not a branch. Find it under "revisions" on the
# model's Hugging Face page. A branch name can move, and the license and
# commercial-use terms recorded above are what that card said when this entry
# was curated; pinning is what keeps that claim checkable.
#
# The site then shows both links: the pinned revision as curated, and the
# author's current version.

hf_repo     = "facebook/dinov3"
hf_revision = ""
+++

<!--
  Do not repeat the model name as a heading - the page renders it already.

  The sections below are a convention, not a rule: nothing checks for them.
  They exist so two entries in the zoo can be read side by side. Delete any
  that do not apply, and add whatever does.
-->

**Intended use.** Extract visual features from images without needing labeled training data. Ideal for insect classification, phenotyping, and behavior analysis when you have many images but few annotations. Works well as a starting point (backbone) for other tasks like segmentation or object tracking, but produces features—not final predictions—so you'll need additional lightweight components for those outputs.

## Architecture and training

DINOv3 uses Vision Transformer (ViT) and ConvNeXt architectures trained without human labels. Instead, it learns by having smaller models mimic a larger teacher model through self-distillation. The training uses 1.7 billion unlabeled images from the web, scaled up 6× in model size and 12× in data compared to DINOv2.

Key features include rotary positional embeddings (allowing arbitrary image resolutions), register tokens for better global context, and a novel Gram anchoring technique that preserves fine-grained spatial details.

## Inputs and outputs

**Inputs:** RGB images at any resolution (256×256 to 4096×4096 tested). No text prompts required.

**Outputs:** Global image embeddings (for classification) and dense feature maps (for segmentation, depth estimation, detection). Normalization uses standard ImageNet statistics.

## Performance

Frozen backbone evaluation (no fine-tuning required):

| Benchmark | ViT-S/16 | ViT-B/16 | ViT-L/16 | ViT-7B/16 |
|-----------|----------|----------|----------|-----------|
| Classification (IN-ReaL) | 87.0% | 89.3% | 90.2% | 90.4% |
| Long-tail (IN-R) | 60.4% | 76.7% | 88.1% | 91.1% |
| Segmentation (ADE20k) | 47.0% | 51.8% | 54.9% | 55.9% |
| Depth estimation (NYUv2 ↓RMSE) | 0.403 | 0.373 | 0.352 | 0.309 |

Domain-specific: Forest canopy height mapping achieved R²=0.86 (vs. 0.53 for DINOv2). Sources: Meta AI DINOv3 technical report (2025).

## Limitations

**Critical constraints for insect monitoring:**

- **Not end-to-end detection**: Produces features only; requires separate heads for bounding boxes or masks
- **Small insects**: Dense features may degrade for very small specimens (<50px²); test higher-resolution variants
- **Fine-grained taxonomy**: Trained on general web data; specialized insect features may require fine-tuning
- **Compute & memory requirements**: ViT-7B needs 4-8 A100 GPUs; ViT-L (300M) minimum for research-grade accuracy. Smaller models are available for edge deployment. 

DINOv3 differs from Grounding DINO—it lacks text-grounded detection. Use Grounding DINO for query-based detection, DINOv3 for unsupervised feature extraction.

## How to obtain the weights

**Hugging Face:** All variants under `facebook/dinov3-*`. 

**Loading example (PyTorch Hub):**
```python
model = torch.hub.load('facebookresearch/dinov3', 'dinov3_vitb16')
```

## Citation

``` bibtex
@misc{simeoni2025dinov3,
  title={{DINOv3}},
  author={Sim{\'e}oni, Oriane and Vo, Huy V. and Seitzer, Maximilian and Baldassarre, Federico and Oquab, Maxime and Jose, Cijo and Khalidov, Vasil and Szafraniec, Marc and Yi, Seungeun and Ramamonjisoa, Micha{\"e}l and Massa, Francisco and Haziza, Daniel and Wehrstedt, Luca and Wang, Jianyuan and Darcet, Timoth{\'e}e and Moutakanni, Th{\'e}o and Sentana, Leonel and Roberts, Claire and Vedaldi, Andrea and Tolan, Jamie and Brandt, John and Couprie, Camille and Mairal, Julien and J{\'e}gou, Herv{\'e} and Labatut, Patrick and Bojanowski, Piotr},
  year={2025},
  eprint={2508.10104},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://arxiv.org/abs/2508.10104},
}
```
