+++
# ── Identity ────────────────────────────────────────────────────────
title              = "BioCLIP"
description        = "CLIP model trained across the tree of life, for zero-shot species classification from a list of taxon names."
foundation         = true

# ── Catalogue ───────────────────────────────────────────────────────
purpose            = ["Insect classification", "Model embeddings"]
task               = ["Classification", "Embedding"]
architecture       = ["ViT-B/16 (CLIP)"]
base_model         = "openai/clip-vit-base-patch16"
year               = 2023
license            = "MIT"
status             = "published"
training_data      = ["10.57967/hf/1972", "unpublished"]
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "open"
geographic_scope   = "Global"
produces           = ["label", "embedding"]
target_taxonomic_rank = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]
image_input_size   = "224x224"
input_modality     = ["image", "text"]
taxonomic_coverage = "TreeOfLife-10M (454k taxa)"
pretraining_data   = ["unpublished"]
developer          = "Samuel Stevens, Jiaman Wu et al. (Imageomics Institute)"
paper_url          = "https://doi.org/10.48550/arXiv.2311.18803"
code_url           = "https://github.com/Imageomics/BioCLIP"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "imageomics/bioclip"
hf_revision        = "ce901ab3c6a913f9e9ef94ce6d27761069f4f01c"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "hf-repo"
provider     = "huggingface"
repo_id      = "imageomics/bioclip"
revision     = "ce901ab3c6a913f9e9ef94ce6d27761069f4f01c"
revision_kind = "commit"
gated        = false
url          = "https://huggingface.co/imageomics/bioclip"
note         = "Weights, open_clip config and tokenizer. open_clip loads the whole repo by id."

[[assets]]
key          = "weights"
provider     = "huggingface"
repo_id      = "imageomics/bioclip"
filename     = "open_clip_pytorch_model.bin"
revision     = "ce901ab3c6a913f9e9ef94ce6d27761069f4f01c"
revision_kind = "commit"
size_bytes   = 598599013
sha256       = "e380384f0c30d425d8c6c40f24471f9dd497fbdfa734a89c461a94aee95f0ef4"
url          = "https://huggingface.co/imageomics/bioclip/resolve/ce901ab3c6a913f9e9ef94ce6d27761069f4f01c/open_clip_pytorch_model.bin"
+++

> CLIP model trained across the tree of life, for zero-shot species classification from a list of taxon names.

**Intended use.** BioCLIP classifies an image of a single organism against a list of
taxon names you supply, with no training. It is a good first step when you have
cropped insect images and no labelled data for your taxa, and a strong image
encoder for few-shot or fine-tuned classifiers. It does not find insects in an
image: pair it with a detector such as FlatBug or ArthroNat and classify the crops.

## Architecture and training

- **Architecture:** CLIP, ViT-B/16 image encoder with a text encoder, trained
  from OpenAI's ViT-B/16 checkpoint with OpenCLIP
- **Trained on:** TreeOfLife-10M, a compilation of iNat21, BIOSCAN-1M and
  Encyclopedia of Life images, labelled from kingdom to species (454k taxa)
- **Objective:** the standard CLIP contrastive objective, with text built from the
  full taxonomic name, so the embedding follows the taxonomic hierarchy
- **Framework:** open_clip

## Inputs and outputs

- **Input:** one RGB image, resized to 224x224, normalised with the CLIP mean and
  std (`open_clip` builds this preprocessing for you); and, for zero-shot use, a
  list of text labels
- **Outputs:** a 512-dimensional image embedding; with text labels, a similarity
  score per label, whose top entry is the predicted taxon

Labels can be scientific names, common names or full taxonomic strings. The
authors' `examples/zero_shot.py` shows the prompt formats used in the paper.

## Performance

Zero-shot top-1 accuracy (%), as reported on the upstream card and in the paper:

| Evaluation set | BioCLIP | OpenAI CLIP |
| --- | --- | --- |
| Meta-Album Insects | 34.8 | 9.1 |
| Meta-Album Insects 2 | 20.4 | 9.8 |
| Mean over 10 biological tasks | 39.4 | 21.9 |

Few-shot results are in the paper.

## Limitations

- **Classifies, does not detect.** At 224x224 an insect in a field photograph or
  trap image covers a few pixels. Crop to one specimen first.
- **Insect accuracy is modest.** About one in three correct zero-shot on Meta-Album
  Insects. Treat predictions as candidates for an expert to check, and evaluate on
  your own images before relying on it.
- **Only as good as the label list.** Zero-shot picks the best match among the names
  you give; a taxon missing from the list cannot be predicted, and the model will
  still name something.
- **Training images are mostly citizen-science photographs** (iNat, EOL) plus
  BIOSCAN-1M lab images. Performance on light traps, sticky traps, or camera traps
  at night is not reported.
- **Rare taxa.** Taxa with few images in TreeOfLife-10M, which covers many insects,
  are recognised less reliably.
- Inherits the biases of OpenAI CLIP, which its authors discuss.

## License and rights

- **License:** MIT
- **Commercial use:** allowed
- **Restrictions:** none binding. The authors ask that derivative products are also open source.
- **Upstream source:** <https://huggingface.co/imageomics/bioclip>

## How to obtain the weights

From Hugging Face, pinned to commit `ce901ab3`. Public, no authentication
required. The weights are one 599 MB PyTorch file; `open_clip` downloads it with
the config and tokenizer:

```python
import open_clip

repo = "hf-hub:imageomics/bioclip"
model, _, preprocess = open_clip.create_model_and_transforms(repo)
tokenizer = open_clip.get_tokenizer(repo)
```

This loads the latest revision. To use exactly the curated one, download the
repository at the pinned commit with
`huggingface_hub.snapshot_download("imageomics/bioclip", revision="ce901ab3c6a913f9e9ef94ce6d27761069f4f01c")`
and load it from that local folder.

## Citation

```bibtex
@inproceedings{stevens2024bioclip,
  title     = {{B}io{CLIP}: A Vision Foundation Model for the Tree of Life},
  author    = {Samuel Stevens and Jiaman Wu and Matthew J Thompson and Elizabeth G Campolongo and Chan Hee Song and David Edward Carlyn and Li Dong and Wasila M Dahdul and Charles Stewart and Tanya Berger-Wolf and Wei-Lun Chao and Yu Su},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2024}
}
```
