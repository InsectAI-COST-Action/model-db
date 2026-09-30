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

title              = "InsectDCT"
description        = "Model weights and Python code to detect, classify, and track insects on natural-looking background of plants and flowers"

# ── Catalogue ─────────────────────────────────────────────────────────────────

purpose            = ["Insect detection", "Insect classification"]
task               = ["Object Detection", "Classification", "Tracking"]
architecture       = ["YOLOv11"]                   # YOLOv8, ViT, Swin Transformer…
year               = 2026                        # year of publication or release
license            = "GPL-3.0-or-later"                       # SPDX identifier where one exists
status             = "published"                     # draft | published | deprecated.
                                                 # Draft is the safe default: only
                                                 # `published` appears on the site.

# Optional. Delete any line you do not have an answer for - the default is in
# the comment.
date               = 2026-09-29                  # when this entry was added to the zoo
vocabulary_scope   = "closed"                    # closed | open | taxonomic.
                                                 # Anything but `closed` is shown as
                                                 # "zero-shot" - it means the model
                                                 # handles concepts it was not
                                                 # trained on.
produces           = ["bbox"]                    # bbox | mask | label | count | track | embedding
image_input_size   = "1920x1080"                 # or "any" for native resolution
input_modality     = []                          # text | image | box | point | mask.
                                                 # List every input the model
                                                 # accepts, image included. Leave
                                                 # empty for a model that only
                                                 # takes an image.
developer          = "Kim Bjerge"                   # who made it, not who curated it
paper_url          = "https://www.biorxiv.org/content/10.64898/2026.07.07.736939v1"                          # paper, DOI or project page

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
url      = "https://github.com/kimbjerge/insectDCT/tree/main/runs/detect/insects8Motion11s/weights"
filename   = "best.pt"
size_bytes = 19398656
sha256     = "e459ae87ebe39732963e77e0fcdd0a9a28672a08"
released   = 2024-10-27
note       = "Trained YOLO11s models on dataset DV8"

[[assets]]
key      = "zenodo-record"              # the label shown in the sidebar
provider = "zenodo"          # zenodo | huggingface | github | erda | package | url
url      = "https://zenodo.org/records/21154490"
# filename   = "best.pt"
# size_bytes = 
# sha256     = ""
released   = 2024-07-03
note       = "Datasets that the models have been trained on, V6."

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

**Intended use.** YOLO models for processing time-lapse images from insect camera traps. It contains code to detect, classify, and track insects with various backgrounds of plants and flowers. 

## Architecture and training

 - **Architecture:** YOLOv11
 - **Task** Object tracking. 
 - **Trained on:** several datasets of insects on (semi-)natural backgrounds, mainly flowers and plants. 
 - **Taxonomic coverage:** mainly pollinators, see the Zenodo record for the class list. 
 - **Framework:** Ultralytics YOLOv11

## Inputs and outputs

 - **Input size:** author reports that images are resized to 1920x1080 for detection with YOLOv11, while insect crops are resized to either 128x128 or 224x224, depending on the classification model. 
 - **Channels:** standard RGB, pipeline also extracts motion-enhanced image representation to improve detection (done with YOLOv11). 
 - **Outputs:** for the detector: bounding boxes. For the hierarchical classifier: ??? 
 - **Input mode:** standalone or time-lapse images, or video. 

## Performance

Multiple, complex metrics reported in the pre-print... 

## Limitations

Lifted from the pre-print discussion section: 
```
The taxonomic classifier is currently trained on Northern and Central European
pollinator taxa, with a large part of the dataset focused on vegetation dominated by plant species of the *Sedum* genus, which implies that the pipeline will require re-training for direct transferability to other geographic regions or habitat and vegetation types. Researchers deploying the pipeline in new contexts are encouraged to supplement the existing dataset with locally collected and annotated images, following the incremental re-training workflow described above, which has been specifically designed to accommodate this kind of extension. The classes with few training samples, such as rare solitary bees and some folded-wing Lepidoptera, show reduced classification accuracy, and this imbalance could be mitigated in future versions by re-training the algorithm by users who require improved performance in those insect groups. Regarding the tracking algorithm, it can produce fragmented or merged trajectories when small insects cross paths or are temporarily occluded, and tracks should therefore be interpreted as activity proxies rather than records
of unique individuals over extended periods.
```

## How to obtain the weights

From the Github repository [insectDCT](https://github.com/kimbjerge/insectDCT), all the various model versions trained weights are in `run/detect`, saved as `.pt` checkpoint files. 

## Citation

``` bibtex
@article {Bjerge2026.07.07.736939,
	author = {Bjerge, Kim and Wogram, Simon F. A. and Serra-Marin, Pau Enric and Sakhiashvili, Otar and H{\o}ye, Toke T.},
	title = {InsectDCT: A generalized pipeline for detection, taxonomic classification, and tracking of insects in camera-trap recordings},
	elocation-id = {2026.07.07.736939},
	year = {2026},
	doi = {10.64898/2026.07.07.736939},
	publisher = {Cold Spring Harbor Laboratory},
	abstract = {Automated monitoring of insect pollinators in natural environments with insect camera traps and trained deep learning algorithms provides novel data for insect ecological studies. However, efficient and accurate image recognition analysis of the recorded images or videos is challenging, particularly for images containing small insects against complex backgrounds with diverse vegetation communities. Even when insects can be detected in images, identifying their taxonomy remains difficult, particularly in footage with low image resolution, light conditions, and distances from the plants, and in cases where insects appear blurry or only partially visible.In this work, we present InsectDCT, an AI-based pipeline for automated detection, hierarchical classification, and tracking of insects in footage of natural vegetation tested in different environments. The InsectDCT pipeline consists of three levels: insect Detection and localization, hierarchical taxonomic Classification, and spatio-temporal Tracking. In the first stage, insects are detected in time-lapse images or video recordings using the You Only Look Once (YOLO11) object detection architecture. Detection performance is improved using motion-enhanced images, which improve robustness in cluttered and 3 dimensional environments. The detector is trained on an extensive dataset that contains more than 60,000 images collected using camera traps deployed across a wide range of plant families and floral habitats. In the second stage, detected insects are classified using a hierarchical taxonomy-aware classification framework that covers 80 taxonomic groups. Classification is performed at multiple taxonomic levels, including order, family, and genus/species, allowing coarse and fine-grained ecological analyzes while accounting for varying levels of visual ambiguity. In the third stage, a multi-object tracking module is applied to high temporal-resolution image sequences and video data to associate detections of the same individual across time. InsectDCT code and all datasets are made publicly available.Competing Interest StatementThe authors have declared no competing interest.},
	URL = {https://www.biorxiv.org/content/early/2026/07/18/2026.07.07.736939},
	eprint = {https://www.biorxiv.org/content/early/2026/07/18/2026.07.07.736939.full.pdf},
	journal = {bioRxiv}
}
```
