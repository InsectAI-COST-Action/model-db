+++
# ── Identity ────────────────────────────────────────────────────────
title              = "BioCLIP 2"
description        = "Larger successor to BioCLIP, trained on 214M organism images, for zero-shot species classification from a list of taxon names."
foundation         = true

# ── Catalogue ───────────────────────────────────────────────────────
category           = "classification"
task               = ["Classification", "Embedding"]
architecture       = ["ViT-L/14 (CLIP)"]
base_model         = "laion/CLIP-ViT-L-14-laion2B-s32B-b82K"
year               = 2025
license            = "MIT"
status             = "published"
training_data      = ["10.57967/hf/6786", "LAION-2B-en"]
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "open"
geographic_scope   = "Global"
produces           = ["label", "embedding"]
image_input_size   = "224x224"
input_modality     = ["image", "text"]
taxonomic_coverage = "TreeOfLife-200M (952k taxa)"
pretraining_data   = ["LAION-2B-en"]
developer          = "Jianyang Gu, Samuel Stevens et al. (Imageomics Institute)"
paper_url          = "https://doi.org/10.48550/arXiv.2505.23883"
code_url           = "https://github.com/Imageomics/bioclip-2"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["Safetensors", "PyTorch"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "imageomics/bioclip-2"
hf_revision        = "2957b322090f9cb17ae72c71981c7218a28d81e0"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "hf-repo"
provider     = "huggingface"
repo_id      = "imageomics/bioclip-2"
revision     = "2957b322090f9cb17ae72c71981c7218a28d81e0"
revision_kind = "commit"
gated        = false
url          = "https://huggingface.co/imageomics/bioclip-2"
note         = "Weights in two formats, open_clip config and tokenizer. open_clip loads the whole repo by id."

[[assets]]
key          = "weights-safetensors"
provider     = "huggingface"
repo_id      = "imageomics/bioclip-2"
filename     = "open_clip_model.safetensors"
revision     = "2957b322090f9cb17ae72c71981c7218a28d81e0"
revision_kind = "commit"
size_bytes   = 1710517724
sha256       = "b7b2bf6fbc95799e42630e394cf95803892ab447c1a8ab629dbc82fbeaf7dfef"
url          = "https://huggingface.co/imageomics/bioclip-2/resolve/2957b322090f9cb17ae72c71981c7218a28d81e0/open_clip_model.safetensors"

[[assets]]
key          = "weights-pytorch"
provider     = "huggingface"
repo_id      = "imageomics/bioclip-2"
filename     = "open_clip_pytorch_model.bin"
revision     = "2957b322090f9cb17ae72c71981c7218a28d81e0"
revision_kind = "commit"
size_bytes   = 1710639510
sha256       = "035208dd616321f6c220384efaa1f10e9fcd8e1f2998ddefc88687718d186a85"
url          = "https://huggingface.co/imageomics/bioclip-2/resolve/2957b322090f9cb17ae72c71981c7218a28d81e0/open_clip_pytorch_model.bin"
note         = "The same weights as a PyTorch file. Only needed if your tools cannot read Safetensors."
+++

> Larger successor to BioCLIP, trained on 214M organism images, for zero-shot species classification from a list of taxon names.

**Intended use.** Like [BioCLIP](../bioclip/), BioCLIP 2 classifies an image of a
single organism against a list of taxon names you supply, with no training, and
works as an image encoder for few-shot or fine-tuned classifiers. It is larger and
trained on twenty times more images, and is markedly more accurate on insects; the
cost is a 1.7 GB model that is slower to run. It does not find insects in an image:
pair it with a detector such as FlatBug or ArthroNat and classify the crops.

## Architecture and training

- **Architecture:** CLIP, ViT-L/14 image encoder with a text encoder, trained from
  LAION-2B CLIP ViT-L/14 with OpenCLIP
- **Trained on:** TreeOfLife-200M, about 214M images of 952k taxa from GBIF, EOL,
  BIOSCAN-5M and FathomNet, plus 26M LAION-2B images replayed so the model keeps
  its general knowledge
- **Objective:** the same hierarchical contrastive training as BioCLIP, at larger
  scale
- **Framework:** open_clip

## Inputs and outputs

- **Input:** one RGB image, resized to 224x224, with the CLIP mean and std
  (`open_clip` builds this preprocessing for you); and, for zero-shot use, a list of
  text labels
- **Outputs:** a 768-dimensional image embedding; with text labels, a similarity
  score per label, whose top entry is the predicted taxon

## Performance

Zero-shot top-1 accuracy (%), as reported on the upstream card and in the paper:

| Evaluation set | BioCLIP 2 | BioCLIP | CLIP ViT-L/14 |
| --- | --- | --- | --- |
| Meta-Album Insects | 55.3 | 34.9 | 9.0 |
| Meta-Album Insects 2 | 27.7 | 20.5 | 11.7 |
| Mean over 10 species tasks | 55.6 | 37.6 | 25.5 |

Few-shot results, and results on tasks beyond species classification, are in the paper.

## Limitations

- **Classifies, does not detect.** At 224x224 an insect in a field photograph or
  trap image covers a few pixels. Crop to one specimen first.
- **Better, not solved.** About one in two correct zero-shot on Meta-Album Insects,
  and about one in four on Insects 2. Treat predictions as candidates for an expert
  to check, and evaluate on your own images before relying on it.
- **Only as good as the label list.** Zero-shot picks the best match among the names
  you give; a taxon missing from the list cannot be predicted, and the model will
  still name something.
- **Biased towards common taxa.** TreeOfLife-200M is long-tailed, so predictions lean
  towards well-photographed species, as the authors note.
- **Heavier than BioCLIP.** Around 1.7 GB of weights; a GPU helps for large image sets.
- Performance on light traps, sticky traps or night camera traps is not reported.

## License and rights

- **License:** MIT
- **Commercial use:** allowed
- **Restrictions:** None stated.
- **Upstream source:** <https://huggingface.co/imageomics/bioclip-2>

## How to obtain the weights

From Hugging Face, pinned to commit `2957b322`. Public, no authentication required.
The same weights are published twice, as Safetensors and as a PyTorch file, each
about 1.7 GB; `open_clip` downloads what it needs with the config and tokenizer:

```python
import open_clip

repo = "hf-hub:imageomics/bioclip-2"
model, _, preprocess = open_clip.create_model_and_transforms(repo)
tokenizer = open_clip.get_tokenizer(repo)
```

This loads the latest revision; the files above are pinned to the curated one.

## Citation

```bibtex
@inproceedings{gu2025bioclip2,
  title     = {{B}io{CLIP} 2: Emergent Properties from Scaling Hierarchical Contrastive Learning},
  author    = {Gu, Jianyang and Stevens, Sam and Campolongo, Elizabeth and Thompson, Matthew and Zhang, Net and Wu, Jiaman and Kopanev, Andrei and Mai, Zheda and White, Alexander and Balhoff, James and Dahdul, Wasila and Rubenstein, Daniel and Lapp, Hilmar and Berger-Wolf, Tanya and Chao, Wei-Lun and Su, Yu},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {38},
  pages     = {102778--102811},
  year      = {2025}
}
```
