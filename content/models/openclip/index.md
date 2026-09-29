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

title       = "OpenCLIP (ViT-B/16, LAION-2B)"
description = "A general-purpose image–text model for zero-shot classification and image feature extraction, included as a representative OpenCLIP checkpoint."
foundation  = true

# ── Catalogue ─────────────────────────────────────────────────────────────────

category           = "classification"                  # must already exist in data/categories.toml
task               = ["Classification", "Embedding"]         # Object Detection | Instance Segmentation |
                                                 # Semantic Segmentation | Classification |
                                                 # Tracking | Embedding | Counting
architecture       = "CLIP with ViT-B/16 image encoder"                   # YOLOv8, ViT, Swin Transformer…
base_model          = ""                          # If this is a fine-tuned model, name the
                                                 # base model it was fine-tuned from.
year               = 2023                        # year of publication or release
license            = "MIT"                       # SPDX identifier where one exists
status             = "published"                     # draft | published | deprecated.
                                                 # Draft is the safe default: only
                                                 # `published` appears on the site.

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-29                  # when this entry was added to the zoo
vocabulary_scope   = "open"                    # closed | open | taxonomic.
                                                 # Anything but `closed` is shown as
                                                 # "zero-shot" - it means the model
                                                 # handles concepts it was not
                                                 # trained on.
geographic_scope   = ""                          # e.g. "France", "Global"
produces           = ["label", "embedding"]                    # bbox | mask | label | count | track | embedding
image_input_size         = "224x224"                   # or "any" for native resolution
input_modality     = ["image", "text"]                          # text | image | box | point | mask.
                                                 # List every input the model
                                                 # accepts, image included. Leave
                                                 # empty for a model that only
                                                 # takes an image.
developer          = "LAION / OpenCLIP contributors"                   # who made it, not who curated it
paper_url          = "https://github.com/mlfoundations/open_clip"                          # paper, DOI or project page

# ── Weights ───────────────────────────────────────────────────────────────────
#
# Where to download the model. The FIRST block is the link the catalogue table
# shows. Add another only if the model genuinely ships several files, the way
# FlatBug ships a YOLOv8n/s/m/l ladder.
#
# Weights are never committed here. GitHub refuses files over 100 MB and the
# authors host them anyway.

[[assets]]
key        = "weights"
provider   = "huggingface"
url        = "https://huggingface.co/laion/CLIP-ViT-B-16-laion2B-s34B-b88K/tree/7288da5a0d6f0b51c4a2b27c624837a9236d0112"
filename   = "open_clip_model.safetensors"
note       = "OpenCLIP ViT-B/16 trained on the LAION-2B English subset."
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

hf_repo     = "laion/CLIP-ViT-B-16-laion2B-s34B-b88K"
hf_revision = "7288da5a0d6f0b51c4a2b27c624837a9236d0112"
+++

<!--
  Do not repeat the model name as a heading - the page renders it already.

  The sections below are a convention, not a rule: nothing checks for them.
  They exist so two entries in the zoo can be read side by side. Delete any
  that do not apply, and add whatever does.
-->

**Intended use.** Included as a representative general-purpose OpenCLIP image–text model. For insect classification, it can compare images with candidate insect names or descriptions without task-specific training, or provide image embeddings for a classifier trained on labeled insect examples. Its accuracy on the intended taxa and image types requires evaluation.

## Architecture and training

This OpenCLIP checkpoint pairs a ViT-B/16 image encoder with a Transformer text encoder. The image encoder divides images into 16 × 16-pixel patches, and both encoders produce 512-dimensional embeddings in a shared image–text space. The model was trained on the approximately two-billion-pair English subset of LAION-5B using contrastive image–text learning.

## Inputs and outputs

Accepts RGB images and text, which can be encoded separately. Images are resized and centre-cropped to 224 × 224 pixels using the checkpoint’s OpenCLIP preprocessing transforms. Text is tokenized with the matching tokenizer.

The model produces 512-dimensional image and text embeddings. For zero-shot classification, image embeddings are compared with text embeddings of candidate labels or descriptions, and the highest-scoring candidate is selected. 

## Performance

The checkpoint’s model card reports 70.2% zero-shot top-1 accuracy on ImageNet-1K, evaluated using the LAION CLIP Benchmark suite.

This measures general image classification using text prompts, not insect identification. Insect-specific performance is not reported in the checkpoint’s model card.

## Limitations

Zero-shot classification depends on the candidate labels and prompt wording. Training on general web image–text pairs does not establish reliable recognition of fine-grained insect taxa.  
## How to obtain the weights

The weights are publicly available on [Hugging Face](https://huggingface.co/laion/CLIP-ViT-B-16-laion2B-s34B-b88K/tree/7288da5a0d6f0b51c4a2b27c624837a9236d0112).

## Citation

@software{ilharco2021openclip,
  title     = {OpenCLIP},
  author    = {Ilharco, Gabriel and Wortsman, Mitchell and Wightman, Ross and
               Gordon, Cade and Carlini, Nicholas and Taori, Rohan and
               Dave, Achal and Shankar, Vaishaal and Namkoong, Hongseok and
               Miller, John and Hajishirzi, Hannaneh and Farhadi, Ali and
               Schmidt, Ludwig},
  year      = {2021},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.5143773},
  url       = {https://doi.org/10.5281/zenodo.5143773}
}

@inproceedings{schuhmann2022laion5b,
  title     = {{LAION-5B}: An Open Large-Scale Dataset for Training Next Generation Image-Text Models},
  author    = {Schuhmann, Christoph and Beaumont, Romain and Vencu, Richard and
               Gordon, Cade W and Wightman, Ross and Cherti, Mehdi and
               Coombes, Theo and Katta, Aarush and Mullis, Clayton and
               Wortsman, Mitchell and Schramowski, Patrick and
               Kundurthy, Srivatsa R and Crowson, Katherine and
               Schmidt, Ludwig and Kaczmarczyk, Robert and Jitsev, Jenia},
  booktitle = {Thirty-sixth Conference on Neural Information Processing Systems Datasets and Benchmarks Track},
  year      = {2022},
  url       = {https://openreview.net/forum?id=M3Y74vmsMcY}
}
