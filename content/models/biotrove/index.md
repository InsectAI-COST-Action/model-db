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

title              = "BioTrove-CLIP"
description        = "CLIP based VLM trained on biodiversity images."
foundation         = true

# ── Catalogue ─────────────────────────────────────────────────────────────────

category           = "classification"                  # must already exist in data/categories.toml
task               = ["Classification", "Embedding"]         # Object Detection | Instance Segmentation |
                                                 # Semantic Segmentation | Classification |
                                                 # Tracking | Embedding | Counting
architecture       = ["CLIP"]                 # YOLOv8, ViT, Swin Transformer… One
                                                 # entry per architecture.
base_model          = ""                          # If this is a fine-tuned model, name the
                                                 # base model it was fine-tuned from.
year               = 2024                        # year of publication or release
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
developer          = "Iowa State University, New York University, and University of Arizona"                   # who made it, not who curated it
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
key      = "BioTrove-CLIP-O"
provider = "huggingface"
url      = "https://huggingface.co/BGLab/BioTrove-CLIP/blob/f4776d5e84dc7305e191c38443f905dc89ed606b/biotroveclip-vit-b-16-from-openai-epoch-40.pt"
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

hf_repo            = "BGLab/BioTrove-CLIP"
hf_revision        = "f4776d5e84dc7305e191c38443f905dc89ed606b"
+++

<!--
  Do not repeat the model name as a heading - the page renders it already.

  The sections below are a convention, not a rule: nothing checks for them.
  They exist so two entries in the zoo can be read side by side. Delete any
  that do not apply, and add whatever does.
-->

**Intended use.** This model supports zero-shot classification of organism images by comparing images with candidate species names in a shared semantic space. It also provides a useful baseline for further training for insect applications.

## Architecture and training

The model pairs a Vision Transformer image encoder with a text encoder
using the CLIP contrastive learning objective. Training uses BioTrove-Train, a curated subset containing approximately 40 million images covering 33,000 species,  across birds, arachnids, insects, plants, fungi, molluscs, and reptiles, sourced from citizen science repositories. 



## Inputs and outputs

The models accept RGB images and text. Use the OpenCLIP preprocessing and
tokenizer appropriate to the selected architecture, including image
resizing/cropping to 224 × 224 pixels and CLIP normalization.

The encoders return image and text embeddings. For zero-shot classification,
compare normalized image embeddings with normalized embeddings of candidate
labels and select the highest-scoring label.

## Performance

The mosel achives 16.9\% zero-shot top-1 accuracy on the "insects-2" benchmark which contains 4000 images across 102 categories of insect pests. 

## Limitations

Zero shot performance is shown to vary substantially across benchmarks. This model is similar to later editions which include a greater training scope and further benchmarks on insects. 

May require further fine tuning for use in insect classification applications. 

## How to obtain the weights

All three checkpoints are publicly available from [BGLab/BioTrove-CLIP](https://huggingface.co/BGLab/BioTrove-CLIP)


## Citation
@inproceedings{NEURIPS2024_b92854f8,
  title     = {{BioTrove}: A Large Curated Image Dataset Enabling AI for Biodiversity},
  author    = {Yang, Chih-Hsuan and Feuer, Ben and Jubery, Zaki and Deng, Zi K. and Nakkab, Andre and Hasan, Zahid and Chiranjeevi, Shivani and Marshall, Kelly and Baishnab, Nirmal and Singh, Asheesh K and Singh, Arti and Sarkar, Soumik and Merchant, Nirav and Hegde, Chinmay and Ganapathysubramanian, Baskar},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {37},
  pages     = {102101--102120},
  publisher = {Curran Associates, Inc.},
  year      = {2024},
  doi       = {10.52202/079017-3241},
  url       = {https://proceedings.neurips.cc/paper_files/paper/2024/hash/b92854f80ba4feefb973959b259dbc2c-Abstract-Datasets_and_Benchmarks_Track.html}
}
