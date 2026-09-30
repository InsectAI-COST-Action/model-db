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

title              = "TaxaBind"
description        = "Ecology-focussed general purpose model for zero-shot species classification. Informed by many modalities. "
foundation         = true

# ── Catalogue ─────────────────────────────────────────────────────────────────

category           = "classification"                  # must already exist in data/categories.toml
task               = ["Classification", "Embedding"]         # Object Detection | Instance Segmentation |
                                                 # Semantic Segmentation | Classification |
                                                 # Tracking | Embedding | Counting
architecture       = ["CLIP, with ViT-B/16 image encoder, plus other feature extractors."]                 # YOLOv8, ViT, Swin Transformer… One
                                                 # entry per architecture.
base_model          = ""                          # If this is a fine-tuned model, name the
                                                 # base model it was fine-tuned from.
year               = 2025                        # year of publication or release
license            = "MIT"                       # SPDX identifier where one exists
status             = "published"                     # draft | published | deprecated.
                                                 # Draft is the safe default: only
                                                 # `published` appears on the site.

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-30                  # when this entry was added to the zoo
vocabulary_scope   = "open"                    # closed | open.
geographic_scope   = ""                          # e.g. "France", "Global"
# Optional: one verified output profile per architecture; see static/formats/README.md.
# output_format    = ["ultralytics-detect-json"]
produces           = ["label", "embedding"]                    # bbox | mask | label | count | track | embedding
image_input_size         = "224x224"                   # or "any" for native resolution
input_modality     = ["image", "text"]                          # text | image | box | point | mask.
                                                 # List every input the model
                                                 # accepts, image included. Leave
                                                 # empty for a model that only
                                                 # takes an image.
developer          = "Multimodal Vision Research Laboratory, Washington University"                   # who made it, not who curated it
paper_url          = ""                          # paper, DOI or project page

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
url      = "https://huggingface.co/MVRL/taxabind-vit-b-16/tree/6061697951cb566e99369cc1cade059a2a37b7e5"
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

hf_repo            = "MVRL/taxabind-vit-b-16"
hf_revision        = "6061697951cb566e99369cc1cade059a2a37b7e5"
+++

<!--
  Do not repeat the model name as a heading - the page renders it already.

  The sections below are a convention, not a rule: nothing checks for them.
  They exist so two entries in the zoo can be read side by side. Delete any
  that do not apply, and add whatever does.
-->

**Intended use.** Model provides representations for classification and retrieval which can be informed by multiple modalities of training information. Can be used zero shot. Not all modalities have to be used at for inference. 

## Architecture and training

The image-text representation starts from that provided by BioCLIP. TaxaBind then aligns additional modalities with ground-level species images using contrastive learning using: iSatNat, which contains 2.7 million species-image and species-satelite image pairs, iSoundNat which contains 88,130 image-audio pairs. Geographic coordinates come from iNaturalist 2021, environmental variables come from WorldClim 2.1. 

## Inputs and outputs

The model accepts RGB images and text. It also accepts information from extra modalities including: location; environmental features; satelite images and audio. Use the evaluation preprocessing and tokeniser supplied on HuggingFace. Images are preprocessed to 224x224 pixels using bicubic resizing and the checkpoint's normalisation settings. The text encoder has a context length of 77 tokens. Both encoders produce a 512-D embedding vectors. 

## Performance

One table in the paper reports zero-shot classification accuracy using image inputs matched against taxanomic text strings. These include evaluations which contain insect classses, although no insect-only evaluation is provided. 

## Limitations

Reported benchmarks do not establish performance for a given insect monitoring workflow. 

Classification zero shot is only possible depending on the supplied candidate taxa names. Further fine tuning may be required for your task. 

## How to obtain the weights

Download the image–text checkpoint from
[MVRL/taxabind-vit-b-16](https://huggingface.co/MVRL/taxabind-vit-b-16).

## Citation

@inproceedings{sastry2025taxabind,
  title        = {{TaxaBind}: A Unified Embedding Space for Ecological Applications},
  author       = {Sastry, Srikumar and Khanal, Subash and Dhakal, Aayush and Ahmad, Adeel and Jacobs, Nathan},
  booktitle    = {Winter Conference on Applications of Computer Vision},
  year         = {2025},
  organization = {IEEE/CVF},
  url          = {https://arxiv.org/abs/2411.00683}
}
