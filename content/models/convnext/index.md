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

title              = "ConvNeXt (base)"
description        = "General-purpose image classifier included to represent a 'modern' supervised CNN architecture."
foundation         = false

# ── Catalogue ─────────────────────────────────────────────────────────────────

purpose            = ["Model embeddings"]
task               = ["Classification", "Embedding"]
architecture       = ["ConvNeXt-Base"]
base_model          = "ConvNeXt-Base, pretrained on ImageNet-22k"
year               = 2022
license            = "Apache-2.0"
status             = "published"
training_data      = ["ImageNet-1k"]
date               = 2026-09-29
vocabulary_scope   = "closed"
# geographic_scope   = ""
produces           = ["label", "embedding"]
target_taxonomic_rank = ["NA"]
image_input_size         = "224x224"
input_modality     = ["image"]
developer          = "Facebook (META), UC Berkeley"
paper_url          = "https://arxiv.org/abs/2201.03545"
pretraining_data   = ["ImageNet-22k"]

# ── Weights ───────────────────────────────────────────────────────────────────
#
# Where to download the model. The FIRST block is the link the catalogue table
# shows. Add another only if the model genuinely ships several files, the way
# FlatBug ships a YOLOv8n/s/m/l ladder.
#
# Weights are never committed here. GitHub refuses files over 100 MB and the
# authors host them anyway.

[[assets]]
key      = "weights"
provider = "huggingface"
url      = "https://huggingface.co/timm/convnext_base.fb_in22k_ft_in1k/tree/67758fcbcf9f007ec7630bf8636b74a8f24e52a0"
note     = "ConvNeXt-Base pretrained on ImageNet-22K and fine-tuned on ImageNet-1K."
# Optional, and worth adding when you know them:
filename   = "pytorch_model.bin"
size_bytes = 371195904
sha256     = "67758fcbcf9f007ec7630bf8636b74a8f24e52a0"
released   = 2022-12-13
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

hf_repo     = "timm/convnext_base.fb_in22k_ft_in1k"
hf_revision = "67758fcbcf9f007ec7630bf8636b74a8f24e52a0"
+++

**Intended use.** ConvNeXt-Base is included as a representative modern supervised convolutional neural network (CNN). For insect classification, it can be used as a feature extractor with a classifier trained on insect labels, or fine-tuned on an insect dataset.

## Architecture and training

This is a modern general purpose CNN model, it uses a hierarchical architecture with depthwise convoltions. The selected checkpoint was pretrained with supervision on ImageNet-22K and then fine-tuned on ImageNet-1K. This checkpoint has not been specifically fine-tuned for insect classification.

## Inputs and outputs

Accepts RGB images, resized and centre-cropped to 224 × 224 pixels using the checkpoint’s preprocessing settings. These are included already.

The default classification head outputs scores for 1,000 imagenet classes. With the classification head removed, the model produces a 1,024-dimensional image embedding that can be used to train an insect classifier.

## Performance

The authors report 85.8% top-1 accuracy on the ImageNet-1K validation set for ConvNeXt-Base pretrained on ImageNet-22K and fine-tuned and evaluated at 224 × 224 pixels.

## Limitations

The supplied classifier is restricted to 1,000 ImageNet categories and cannot identify arbitrary insect taxa from their names. Classification using a different insect label set requires a trained classifier or fine-tuning with labeled examples.

## How to obtain the weights

Publicly available on [Hugging Face](https://huggingface.co/timm/convnext_base.fb_in22k_ft_in1k/tree/67758fcbcf9f007ec7630bf8636b74a8f24e52a0).

## Citation

``` bibtex
@inproceedings{liu2022convnet,
  title     = {A ConvNet for the 2020s},
  author    = {Liu, Zhuang and Mao, Hanzi and Wu, Chao-Yuan and
               Feichtenhofer, Christoph and Darrell, Trevor and Xie, Saining},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2022},
  url       = {https://arxiv.org/abs/2201.03545}
}

@misc{rw2019timm,
  title     = {PyTorch Image Models},
  author    = {Wightman, Ross},
  year      = {2019},
  publisher = {GitHub},
  doi       = {10.5281/zenodo.4414861},
  url       = {https://github.com/huggingface/pytorch-image-models}
}
```
