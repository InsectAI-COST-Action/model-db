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

title              = "REPLACE WITH THE MODEL NAME"
description        = "One sentence, in plain language, saying what the model does."
foundation         = false

# ── Catalogue ─────────────────────────────────────────────────────────────────

purpose            = ["REPLACE"]                 # Insect detection - simple background |
                                                 # Insect detection - complex background |
                                                 # Insect classification | Functional group
                                                 # classification | Behaviour classification |
                                                 # Trait quantification | Model embeddings
task               = ["REPLACE"]                 # Localisation | Binary Classification |
                                                 # Multiclass Classification | Instance
                                                 # Segmentation | Semantic Segmentation |
                                                 # Tracking | Counting | Regression |
                                                 # Zero-shot Detection | Zero-shot
                                                 # Classification
architecture       = ["REPLACE"]                 # YOLOv8, ViT, Swin Transformer… One
                                                 # entry per architecture.
base_model          = ""                          # If this is a fine-tuned model, name the
                                                 # base model it was fine-tuned from.
year               = 2025                        # year of publication or release
license            = "MIT"                       # SPDX identifier where one exists
status             = "draft"                     # draft | published | deprecated.
                                                 # Draft is the safe default: only
                                                 # `published` appears on the site.

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-22                  # when this entry was added to the zoo
vocabulary_scope   = "closed"                    # closed | open.
geographic_scope   = ""                          # e.g. "France", "Global"
# Optional: one verified output profile per architecture; see static/formats/README.md.
# output_format    = ["ultralytics-detect-json"]
produces           = ["bbox"]                    # bbox | mask | label | count | track | embedding
image_input_size         = "640x640"                   # or "any" for native resolution
input_modality     = []                          # text | image | box | point | mask.
                                                 # List every input the model
                                                 # accepts, image included. Leave
                                                 # empty for a model that only
                                                 # takes an image.
developer          = "REPLACE"                   # who made it, not who curated it
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
url      = "https://..."
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

hf_repo     = ""
hf_revision = ""
+++

<!--
  Do not repeat the model name as a heading - the page renders it already.

  The sections below are a convention, not a rule: nothing checks for them.
  They exist so two entries in the zoo can be read side by side. Delete any
  that do not apply, and add whatever does.
-->

**Intended use.** One or two sentences on what this model is for, and the
situation it was built for. A reader who is scanning five entries should be able
to tell from this paragraph whether this one is theirs.

## Architecture and training

What the model is, how it was trained, and on what. Name the training data.

## Inputs and outputs

What it expects (image size, channels, preprocessing) and what it returns.
Anything a user must do to their images before the model works is worth saying.

## Performance

Report what the source publication reports, **with the evaluation set named**.
Do not re-run it and do not estimate: an mAP without its benchmark is not a
comparable quantity. If nothing is reported, write "Not reported in the source
publication", that is a useful fact in itself.

## Limitations

**This is the section that matters most.** An empty limitations section is worse
than no card at all, because it implies somebody checked. Say where the model
fails: backgrounds, life stages, image quality, resolution, occlusion, scale,
taxa it has never seen and cannot be expected to handle.

## How to obtain the weights

Where they live, what the license actually permits, and whether the link is
pinned. Say here if there is anything a downloader has to do, request access,
accept a gate, convert a format.

## Citation

BibTeX, or the reference as the authors would want it cited.
