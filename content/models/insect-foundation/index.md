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

title              = "Insect-Foundation (vision backbone)"
description = "An arthropod-specific foundation model that learns visual features for downstream tasks."
foundation         = true

# ── Catalogue ─────────────────────────────────────────────────────────────────

category           = "classification"                  # must already exist in data/categories.toml
task               = ["Classification", "Embedding"]         # Object Detection | Instance Segmentation |
                                                 # Semantic Segmentation | Classification |
                                                 # Tracking | Embedding | Counting
architecture       = ["ViT-B/16"]                 # YOLOv8, ViT, Swin Transformer… One
                                                 # entry per architecture.
base_model          = ""                          # If this is a fine-tuned model, name the
                                                 # base model it was fine-tuned from.
year               = 2024                        # year of publication or release
license            = "Not found"                       # SPDX identifier where one exists
status             = "published"                     # draft | published | deprecated.
training_data      = ["https://github.com/uark-cviu/InsectFoundationModel/releases/tag/v1"]
                                                 # Draft is the safe default: only
                                                 # `published` appears on the site.

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-30                  # when this entry was added to the zoo
vocabulary_scope   = "closed"                    # closed | open.
geographic_scope   = ""                          # e.g. "France", "Global"
# Optional: one verified output profile per architecture; see static/formats/README.md.
# output_format    = ["ultralytics-detect-json"]
produces           = ["embedding", "label"]                    # bbox | mask | label | count | track | embedding
image_input_size         = "224x224"                   # or "any" for native resolution
input_modality     = ["image"]                          # text | image | box | point | mask.
                                                 # List every input the model
                                                 # accepts, image included. Leave
                                                 # empty for a model that only
                                                 # takes an image.
developer          = "University of Arkansas and University at Albany"                   # who made it, not who curated it
paper_url          = "https://openaccess.thecvf.com/content/CVPR2024/html/Nguyen_Insect-Foundation_A_Foundation_Model_and_Large-scale_1M_Dataset_for_Visual_CVPR_2024_paper.html"


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
provider = "github"          # zenodo | huggingface | github | erda | package | url
url        = "https://github.com/uark-cviu/InsectFoundationModel/releases/download/v1/vit_base_patch16_pretrained.pth"
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

The visual backbone is ViT-B/16 and produces 768-dimensional hidden representations.

Training uses Insect-1M, which contains 1,017,036 images covering 34,212
species. Despite its name, the dataset includes other arthropods as well as insects.

## Inputs and outputs

Model accepts RGB images. Its default evaluation
pipeline resizes the shorter side to 224 pixels using bicubic interpolation,
then centre-crops to 224 × 224 pixels. Pixel values are scaled to [0, 1] and normalized using channel means
(0.485, 0.456, 0.406) and standard deviations (0.229, 0.224, 0.225).

## Performance

The paper reports 75.8% top-1 and 92.1% top-5 accuracy on IP102.

## Limitations

IP102 results do not establish performance on every insect taxon, geographic
region, life stage, or imaging setup. 

The pretrained visual backbone is not a complete species-identification
service. Classification requires a additional suitable trained head. 

The release does not clearly document which reported pretraining variant
the downloadable checkpoint represents. 


## How to obtain the weights

[`vit_base_patch16_pretrained.pth`](https://github.com/uark-cviu/InsectFoundationModel/releases/download/v1/vit_base_patch16_pretrained.pth)
from the authors' GitHub release. 

## Citation

@InProceedings{Nguyen_2024_CVPR,
  author    = {Nguyen, Hoang-Quan and Truong, Thanh-Dat and
               Nguyen, Xuan Bac and Dowling, Ashley and
               Li, Xin and Luu, Khoa},
  title     = {Insect-Foundation: A Foundation Model and Large-scale 1M Dataset for Visual Insect Understanding},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  month     = {June},
  year      = {2024},
  pages     = {21945--21955},
  url       = {https://openaccess.thecvf.com/content/CVPR2024/html/Nguyen_Insect-Foundation_A_Foundation_Model_and_Large-scale_1M_Dataset_for_Visual_CVPR_2024_paper.html}
}
