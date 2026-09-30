+++
# ── Identity ────────────────────────────────────────────────────────
title              = "CLIBD"
description        = "CLIP-style model that aligns insect images, DNA barcodes and taxonomic labels in one embedding space, for classifying seen and unseen species by retrieval."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "classification"
task               = ["Classification", "Embedding"]
architecture       = ["ViT-B/16", "BarcodeBERT", "BERT-Small"]
base_model         = "timm/vit_base_patch16_224; BarcodeBERT (5-mer); prajjwal1/bert-small"
year               = 2025
license            = "MIT"
status             = "published"
training_data      = ["10.5281/zenodo.8030065", "10.5281/zenodo.11973457"]
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "open"
produces           = ["label", "embedding"]
image_input_size   = "224x224"
input_modality     = ["image", "text"]
taxonomic_coverage = "Insects (BIOSCAN-1M and BIOSCAN-5M)"
pretraining_data   = ["ImageNet-21k", "ImageNet-1k", "https://huggingface.co/datasets/bioscan-ml/CanadianInvertebrates-ML", "BookCorpus", "English Wikipedia"]
developer          = "ZeMing Gong, Austin T. Wang et al."
paper_url          = "https://doi.org/10.48550/arXiv.2405.17537"
code_url           = "https://github.com/bioscan-ml/clibd"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "bioscan-ml/clibd"
hf_revision        = "3a27250e89e884f26f25ba2e939eaf5f774a0fb3"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key           = "1m-idt"
provider      = "huggingface"
repo_id       = "bioscan-ml/clibd"
variant       = "BIOSCAN-1M, image + DNA + text (main model in the paper)"
filename      = "ckpt/bioscan_clip/ver_1_0/bioscan_1m/image_dna_text_4gpu/best.pth"
revision      = "3a27250e89e884f26f25ba2e939eaf5f774a0fb3"
revision_kind = "commit"
url           = "https://huggingface.co/bioscan-ml/clibd/resolve/3a27250e89e884f26f25ba2e939eaf5f774a0fb3/ckpt/bioscan_clip/ver_1_0/bioscan_1m/image_dna_text_4gpu/best.pth"

[[assets]]
key           = "hf-repo"
provider      = "huggingface"
repo_id       = "bioscan-ml/clibd"
revision      = "3a27250e89e884f26f25ba2e939eaf5f774a0fb3"
revision_kind = "commit"
gated         = false
url           = "https://huggingface.co/bioscan-ml/clibd"
note          = "All checkpoints, the BarcodeBERT starting checkpoints and pre-extracted test/val embeddings."

[[assets]]
key           = "1m-id"
provider      = "huggingface"
repo_id       = "bioscan-ml/clibd"
variant       = "BIOSCAN-1M, image + DNA"
filename      = "ckpt/bioscan_clip/ver_1_0/bioscan_1m/image_dna_4gpu/best.pth"
revision      = "3a27250e89e884f26f25ba2e939eaf5f774a0fb3"
revision_kind = "commit"
url           = "https://huggingface.co/bioscan-ml/clibd/resolve/3a27250e89e884f26f25ba2e939eaf5f774a0fb3/ckpt/bioscan_clip/ver_1_0/bioscan_1m/image_dna_4gpu/best.pth"

[[assets]]
key           = "5m-idt"
provider      = "huggingface"
repo_id       = "bioscan-ml/clibd"
variant       = "BIOSCAN-5M, image + DNA + text"
filename      = "ckpt/bioscan_clip/ver_1_0/bioscan_5m/image_dna_text_4gpu/best.pth"
revision      = "3a27250e89e884f26f25ba2e939eaf5f774a0fb3"
revision_kind = "commit"
url           = "https://huggingface.co/bioscan-ml/clibd/resolve/3a27250e89e884f26f25ba2e939eaf5f774a0fb3/ckpt/bioscan_clip/ver_1_0/bioscan_5m/image_dna_text_4gpu/best.pth"

[[assets]]
key           = "5m-id"
provider      = "huggingface"
repo_id       = "bioscan-ml/clibd"
variant       = "BIOSCAN-5M, image + DNA"
filename      = "ckpt/bioscan_clip/ver_1_0/bioscan_5m/image_dna_4gpu/best.pth"
revision      = "3a27250e89e884f26f25ba2e939eaf5f774a0fb3"
revision_kind = "commit"
url           = "https://huggingface.co/bioscan-ml/clibd/resolve/3a27250e89e884f26f25ba2e939eaf5f774a0fb3/ckpt/bioscan_clip/ver_1_0/bioscan_5m/image_dna_4gpu/best.pth"
+++

> CLIP-style model that aligns insect images, DNA barcodes and taxonomic labels in one embedding space, for classifying seen and unseen species by retrieval.

**Intended use.** Taxonomic classification of single insect specimens, from order down to
species, by comparing a query against a reference database. CLIBD has three encoders, for
images, DNA barcodes and taxonomic text, trained so that the same specimen lands in the same
place in a shared embedding space. You embed a query (usually an image) and give it the
labels of the closest labelled image or DNA barcode in your reference set. Because
classification is by retrieval rather than a fixed classifier head, it can name species the
model never saw in training, as long as your reference set holds labelled images or barcodes
of them. Aligning images with DNA also allows image-to-DNA retrieval: matching an image
against species that only have barcodes on file. It does not find insects in an image: crop
to one specimen first.

## Architecture and training

- **Architecture:** three pretrained encoders fine-tuned together:
  - **Image:** ViT-B/16 (`vit_base_patch16_224` in timm), pretrained on ImageNet-21k and
    fine-tuned on ImageNet-1k
  - **DNA:** BarcodeBERT with 5-mer tokenisation, pretrained by masked language modelling
    on 893k DNA barcodes that do not overlap with BIOSCAN-1M
  - **Text:** BERT-Small, which encodes the taxonomic labels
- **Objective:** CLIP-style contrastive learning extended to three modalities. An NT-Xent
  loss is applied symmetrically to each pair of modalities (image–DNA, DNA–text,
  image–text), and the three losses are summed. The temperature is learned, starting at
  0.07. The repository also provides checkpoints that update only LoRA layers
- **Trained on:** BIOSCAN-1M, about 1 million insect records, each with an image, a DNA
  barcode and an expert taxonomic label. Fewer than 10% of records are labelled to
  species. Records without species labels are still used for contrastive training. Species
  were split into *seen* and *unseen* sets, and unseen species were kept out of training.
  Versions trained on BIOSCAN-5M (using the BIOSCAN-5M paper's splits) are also released
- **Training:** 50 epochs on four 80 GB A100 GPUs, batch size 2000, Adam with a one-cycle
  learning-rate schedule (1e-6 to 5e-5) and automatic mixed precision
- **Variants released:** image + DNA + text (I+D+T, the main model in the paper), image +
  DNA (I+D) and image + text (I+T), each trained on BIOSCAN-1M and on BIOSCAN-5M
- **Framework:** PyTorch 2.0.1, Python 3.10

## Inputs and outputs

- **Image input:** one RGB image of a single specimen. At inference, images are resized
  to 256×256 and centre-cropped to 224×224
- **DNA input:** a DNA barcode (COI) sequence, cut to at most 660 bases and split into
  non-overlapping 5-mers
- **Text input:** the taxonomic labels joined together (order, family, genus, species),
  down to the most specific rank available
- **Outputs:** one embedding per input. For classification, the query embedding is
  compared by cosine similarity with a reference set ("keys") of labelled image or DNA
  embeddings. The prediction is the order, family, genus and species of the closest key
- **You supply the reference set.** Accuracy depends on it: species with more reference
  records are classified more accurately. Text labels can also serve as keys, but this
  works much worse than image or DNA keys, especially for unseen species

## Performance

From the source publication. Top-1 macro accuracy (%) on the authors' BIOSCAN-1M test
split, for the I+D+T model. "Seen" species were in the training data. "Unseen" species
were not; they are only in the reference set. H.M. is the harmonic mean of the two.

| Query → key | Rank | Seen | Unseen | H.M. |
| --- | --- | --- | --- | --- |
| Image → image | Genus | 74.6 | 60.4 | 66.8 |
| Image → image | Species | 59.3 | 45.0 | 51.2 |
| DNA → DNA | Species | 95.6 | 90.4 | 92.9 |
| Image → DNA | Genus | 70.6 | 20.8 | 32.1 |
| Image → DNA | Species | 51.6 | 8.6 | 14.7 |

For comparison, species-level image → image macro accuracy was 5.9 (H.M.) for the image
encoder before alignment, and 17.1 for BioCLIP on the same test set (BioCLIP was trained
on different BIOSCAN-1M splits, so it may have seen the "unseen" species). Micro accuracy,
averaged over specimens rather than species, is much higher: 79.6 (seen) and 69.7 (unseen)
for image → image at species level.

On the INSECT dataset (21,212 image–barcode pairs, 1,213 species), using CLIBD's image
and DNA encoders in Bayesian zero-shot learning raised species-level accuracy from 38.3 /
20.8 (seen / unseen) with the original encoders to 57.9 / 25.1.

The paper's main results are for the BIOSCAN-1M models. The BIOSCAN-5M checkpoints are
not evaluated in the main text.

## Limitations

- **Classifies, does not detect.** Images must show one specimen. The model was trained on
  BIOSCAN lab images of single specimens on a plain background. Performance on field
  photographs, trap images or other imaging systems is not reported
- **Needs a labelled reference set.** Predictions can only be species that are in your
  reference database. A species with no images or barcodes on file cannot be predicted,
  and the model will still return its nearest match
- **Unseen species from images are hard.** Image → image accuracy drops from 59.3 to 45.0
  (macro, species) for unseen species. Image → DNA works poorly for unseen species (8.6%
  macro at species level), so identifying a species from an image when only its barcode is
  on file is not yet reliable
- **Rare species are classified worse.** Accuracy rises with the number of reference
  records per species, and macro accuracy is well below micro accuracy
- **Insects only, and BIOSCAN only.** Trained and tested on BIOSCAN-1M/5M, plus the INSECT
  dataset for the zero-shot experiments. Other taxa and other regions have not been tested
- **DNA barcodes are less available than images.** The DNA and cross-modal features only
  help where barcodes exist
- **Setup is research-grade.** Running the model means cloning the code repository and
  following its configs. There is no packaged inference API

## License and rights

- **License:** MIT, the license of the GitHub code repository (copyright 3dlg-hcvc). The
  Hugging Face repository that hosts the weights states no license of its own, so the
  weights are taken to be released under the same MIT license as the code
- **Commercial use:** allowed under MIT. The base encoders and the BIOSCAN datasets have
  their own licenses
- **Upstream source:** <https://huggingface.co/bioscan-ml/clibd>
- **Code:** <https://github.com/bioscan-ml/clibd>

## How to obtain the weights

From Hugging Face, pinned to commit `3a27250e`. Public, no authentication required. The
repository holds the six CLIBD checkpoints (I+D+T, I+D and I+T, each for BIOSCAN-1M and
BIOSCAN-5M), the BarcodeBERT starting checkpoints, and pre-extracted embeddings of the test
and validation splits. The code repository's README also lists mirror links on an SFU
server and a zip of LoRA checkpoints.

The authors download everything under `ckpt/` into the code repository:

```bash
git clone https://github.com/bioscan-ml/clibd && cd clibd
huggingface-cli download bioscan-ml/clibd --include "ckpt/*" --revision 3a27250e89e884f26f25ba2e939eaf5f774a0fb3 --local-dir .
python scripts/inference_and_eval.py 'model_config=for_bioscan_1m/final_experiments/image_dna_text_seed_42.yaml'
```

Checkpoint paths are set in the YAML configs under `bioscanclip/config/model_config/`. You
may need to move files to match them.

## Citation

```bibtex
@inproceedings{gong2025clibd,
  title     = {{CLIBD}: Bridging Vision and Genomics for Biodiversity Monitoring at Scale},
  author    = {Gong, ZeMing and Wang, Austin T. and Huo, Xiaoliang and Haurum, Joakim Bruslund
               and Lowe, Scott C. and Taylor, Graham W. and Chang, Angel X.},
  booktitle = {The Thirteenth International Conference on Learning Representations},
  year      = {2025},
  url       = {https://openreview.net/forum?id=d5HUnyByAI}
}
```
