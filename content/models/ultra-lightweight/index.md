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

title              = "ultra-lightweight CNNs"
description        = "Extremely small CNNs, intended for insect detection on microcontrollers"
foundation         = false

# ── Catalogue ─────────────────────────────────────────────────────────────────

category           = "detection"                  # must already exist in data/categories.toml
task               = ["Classification"]         # Object Detection | Instance Segmentation |
                                                 # Semantic Segmentation | Classification |
                                                 # Tracking | Embedding | Counting
architecture       = ["MobileNetv2"]                 # YOLOv8, ViT, Swin Transformer… One
output_format      = ["ecto-trigger-tflite-score"]
                                                 # entry per architecture.
base_model          = ""                          # If this is a fine-tuned model, name the
                                                 # base model it was fine-tuned from.
year               = 2025                        # year of publication or release
license            = "GNU GPLv3"                       # SPDX identifier where one exists
status             = "published"                     # draft | published | deprecated.
                                                 # Draft is the safe default: only
                                                 # `published` appears on the site.
training_data      = ["10.5061/dryad.p5hqbzkz7"]

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-30                 # when this entry was added to the zoo
vocabulary_scope   = "closed"                    # closed | open.
geographic_scope   = ""                          # e.g. "France", "Global"
# Optional: one verified output profile per architecture; see static/formats/README.md.
# output_format    = ["ultralytics-detect-json"]
produces           = ["label"]                    # bbox | mask | label | count | track | embedding
target_taxonomic_rank = ["NA"]
image_input_size         = "120×160"                   # or "any" for native resolution
input_modality     = ["image"]                          # text | image | box | point | mask.
                                                 # List every input the model
                                                 # accepts, image included. Leave
                                                 # empty for a model that only
                                                 # takes an image.
developer          = "University of Exeter"                   # who made it, not who curated it
paper_url          = "https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.70098"                          # paper, DOI or project page

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
url      = "https://github.com/rossGardiner/ecto-trigger/tree/main/model_weights"
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

This is a collection of very small models, with fewer than 450k parameters. They are quantised to run on low powered microcontroller platforms, which is the primary design choice, to enable insect detection on these compute-limited devices. 

They are based on the MobileNetv2 architecture. Models have also been quantised using TFLite. 

They are trained on a mixture of iNaturalist data and field datasets of insects on flat backgrounds. 

## Inputs and outputs

It accepts images and produces a confidence value [0, 1], of that image containing an insect. 

The documented [Ecto-Trigger TFLite score profile](/formats/detection/ecto-trigger-tflite-score.json) follows the author deployment guide at revision `a603943`. The quantized runtime returns a `(1,1)` unsigned-byte tensor with one image-level insect-presence score, rather than instance boxes. The unquantized Keras model has a floating-point sigmoid output. This profile is source-inspected; released-artifact inference and physical deployment have not been probed.

## Performance

Reports 0.964 AUROC on test set of train distribution data. Reports 0.872 AUROC on a variant of the AMI camera traps dataset. 

## Limitations

These models are for a highly specific circumstance. They intended to aid the design of future insect camera traps by providing a way to perform insect detection on a low-powered microcontroller. 

The extremely small size of these models likely limits thier applicability to general purpose datasets. So, fine-tuning may be required. 

Also, the creating the runtime environment to use this sort of model requires some understanding of microcontrollers and how to programme them.  

## How to obtain the weights

Weights are downloadable on GitHub: https://github.com/rossGardiner/ecto-trigger/tree/main/model_weights 

## Citation

@article{https://doi.org/10.1111/2041-210x.70098,
author = {Gardiner, Ross J. and Rowlands, Sareh and Simmons, Benno I.},
title = {Towards scalable insect monitoring: Ultra-lightweight CNNs as on-device triggers for insect camera traps},
journal = {Methods in Ecology and Evolution},
volume = {17},
number = {2},
pages = {357-370},
keywords = {artificial intelligence, biodiversity monitoring, camera trap, conservation technology, edge computing, insect camera trap, insects, TinyML},
doi = {https://doi.org/10.1111/2041-210x.70098},
url = {https://besjournals.onlinelibrary.wiley.com/doi/abs/10.1111/2041-210x.70098},
eprint = {https://besjournals.onlinelibrary.wiley.com/doi/pdf/10.1111/2041-210x.70098},
abstract = {Abstract Camera traps, combined with AI, have emerged to achieve automated, scalable biodiversity monitoring. However, passive infrared (PIR) sensors that typically trigger camera traps are poorly suited for detecting small, fast-moving ectotherms such as insects. Insects comprise over half of all animal species and are key components of ecosystems and agriculture. The need for an appropriate and scalable insect camera trap is critical in the wake of concerning reports of declines in insect populations. This study proposes an alternative to the PIR trigger: ultra-lightweight convolutional neural networks running on low-powered hardware to detect insects in a continuous stream of captured images. We train such models to distinguish insect images from backgrounds. Our design achieves zero latency between trigger and image capture. Our models are rigorously tested and achieve high accuracy ranging from 91.8\% to 96.4\% AUROC on test data and 58.8\% to 87.2\% AUROC on field data from distributions unseen during training. The high specificity of our models ensures minimal saving of false positive images, maximising deployment storage efficiency. High recall scores indicate a minimal false negative rate, maximising insect detection. Analysis using saliency maps shows the learned representation of our models to be robust, with low reliance on spurious background features. Our method is also shown to operate deployed on off-the-shelf, low-powered microcontroller units, consuming a maximum power draw of less than 300 mW. This paves the way for scalable systems with longer deployment times. Overall, we fully define the properties of a successful trigger for camera traps and show how lightweight AI models, made bespoke for efficient hardware, can be realised with a specific focus on insect ectotherms. We provide these models to the community alongside a complete codebase for future modifications, and we demonstrate how they can be deployed on an example ESP32-S3 microcontroller platform. This step potentiates a major advancement for ectotherm camera traps and insect monitoring.},
year = {2026}}

