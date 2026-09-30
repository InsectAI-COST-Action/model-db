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

title              = "BioCAP"
description        = "This model adapts CLIP to align species descriptions and images in a shared space. "
foundation         = true

# ── Catalogue ─────────────────────────────────────────────────────────────────

purpose            = ["Insect classification", "Model embeddings"]
task               = ["Classification", "Embedding"]
architecture       = ["OpenAI CLIP ViT-B/16"]
# base_model          = "" 
year               = 2025
license            = "MIT"
status             = "published" 

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-30 
vocabulary_scope   = "open" 
geographic_scope   = "" 
# output_format    = ["ultralytics-detect-json"]
produces           = ["label", "embedding"]
image_input_size         = "224x224" 
input_modality     = ["image", "text"] 
developer          = "Imageomics Institute" 
paper_url          = "https://arxiv.org/abs/2510.20095" 

# ── Weights ───────────────────────────────────────────────────────────────────
#
# Where to download the model. The FIRST block is the link the catalogue table
# shows. Add another only if the model genuinely ships several files, the way
# FlatBug ships a YOLOv8n/s/m/l ladder.
#
# Weights are never committed here. GitHub refuses files over 100 MB and the
# authors host them anyway.

[[assets]]
key      = "weights"              # the label shown in the sidebar
provider = "huggingface"          # zenodo | huggingface | github | erda | package | url
url      = "https://huggingface.co/imageomics/biocap/tree/4e544d1d08781b6afee77bd7c1a85d04bd567d1b"
# Optional, and worth adding when you know them:
# filename   = "model.pt"
# size_bytes = 6275129
# sha256     = "..."
# released   = 2024-10-23
# note       = "Which checkpoint this is, and anything a downloader should know."

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

hf_repo            = "imageomics/biocap"
hf_revision        = "4e544d1d08781b6afee77bd7c1a85d04bd567d1b"
+++

<!--
  Do not repeat the model name as a heading - the page renders it already.

  The sections below are a convention, not a rule: nothing checks for them.
  They exist so two entries in the zoo can be read side by side. Delete any
  that do not apply, and add whatever does.
-->

**Intended use.** BioCAP supports zero-shot species classification,
biological image-text retrieval, and image feature extraction. Its scope includes animals,
plants, fungi, insects, etc.

## Architecture and training

This model further trained OpenAI's CLIP ViT-B/16 checkpoint on a dataset of 10 million biology images paired with descriptive captions of thier appearance. 

The training architecture uses shared image and text encoders to align the descriptions and images into a shared space. 

It produces output vectors in a 512-D embedding space. 

## Inputs and outputs

Accepts RGB images and text, which can be encoded separately. Images are
processed at 224 × 224 pixels using the checkpoint's CLIP preprocessing
transforms. Pixel values are scaled to [0, 1] and normalized using channel means
(0.48145466, 0.4578275, 0.40821073) and standard deviations
(0.26862954, 0.26130258, 0.27577711).

## Performance

Reported top-1 classification accuracy on Meta-Album Insects: 41.9%. 

Reported top-1 classification accuracy on Meta-Album Insects 2: 23.7%

## Limitations

It is not yet well understood how applicable these large scale models are on field-imagery. 

Training data includes classes across the tree-of-life. Insects may not be eqivialently represented alongside other animal taxa. 

## How to obtain the weights

Download `open_clip_model.safetensors` and the matching supporting files from
the [pinned Hugging Face revision](https://huggingface.co/imageomics/biocap/tree/4e544d1d08781b6afee77bd7c1a85d04bd567d1b).

## Citation

@inproceedings{zhang2026biocap,
  title     = {{BioCAP}: Exploiting Synthetic Captions Beyond Labels in Biological Foundation Models},
  author    = {Zhang, Ziheng and Ma, Xinyue and Chowdhury, Arpita and
               Campolongo, Elizabeth G. and Thompson, Matthew J. and
               Zhang, Net and Stevens, Samuel and Lapp, Hilmar and
               Berger-Wolf, Tanya and Su, Yu and Chao, Wei-Lun and
               Gu, Jianyang},
  booktitle = {The Fourteenth International Conference on Learning Representations},
  year      = {2026},
  url       = {https://openreview.net/forum?id=SCKLkfgevy}
}
