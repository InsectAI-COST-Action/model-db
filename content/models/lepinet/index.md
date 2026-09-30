+++
# ── Identity ────────────────────────────────────────────────────────
title              = "lepinet"
description        = "Identifies moths and butterflies to species, genus and family from a photo of a single specimen, with coherent ranks and confidence thresholds for backing off to a coarser rank."
foundation         = false

# ── Catalogue ───────────────────────────────────────────────────────
category           = "classification"
task               = ["Classification", "Embedding"]
architecture       = ["ViT-L/14 (BioCLIP-2)", "ConvNeXt-L (DINOv3)", "EfficientNetV2-S"]
base_model         = "imageomics/bioclip-2; timm/convnext_large.dinov3_lvd1689m; torchvision efficientnet_v2_s (ImageNet)"
year               = 2026
license            = "CC-BY-NC-4.0"
status             = "published"
training_data      = ["10.15468/dl.hg37y9", "unpublished"]
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Global (mostly North America and Europe)"
produces           = ["label", "embedding"]
image_input_size   = "256x256 (ViT, resampled to 224 inside the model), 320x320 (ConvNeXt), 256x256 (EfficientNet)"
taxonomic_coverage = "Lepidoptera: 12,041 species, 4,333 genera, 102 families"
developer          = "Guillaume Mougeot (Aarhus University)"
code_url           = "https://github.com/GuillaumeMougeot/lepinet"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "prohibited"
weight_format      = ["ONNX", "Safetensors"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "gmougeot/lepinet-bioclip2-vitl14"
hf_revision        = "c84edd897829c38db599682eb735a5c730ff8d46"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "bioclip2-vitl14"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-bioclip2-vitl14"
revision     = "c84edd897829c38db599682eb735a5c730ff8d46"
revision_kind = "commit"
gated        = false
variant      = "BioCLIP-2 ViT-L/14 (recommended)"
filename     = "model.onnx"
size_bytes   = 1285435210
sha256       = "8f9c0d7067bc3bb580197f0ecb59bbb4c5d8f3ec96c44a8c07895f704275f1a3"
url          = "https://huggingface.co/gmougeot/lepinet-bioclip2-vitl14/resolve/c84edd897829c38db599682eb735a5c730ff8d46/model.onnx"
released     = 2026-09-29
note         = "Recommended: the most accurate on photos, best calibrated. 321 M parameters, 256x256 input, fp32. Also loads with transformers. Taxonomy, names, thresholds, predict.py and a GPU fp16 file (model_fp16.onnx) are in the same repo."

[[assets]]
key          = "bioclip2-vitl14-int8"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-bioclip2-vitl14"
revision     = "c84edd897829c38db599682eb735a5c730ff8d46"
revision_kind = "commit"
gated        = false
variant      = "BioCLIP-2 ViT-L/14, int8 for CPUs"
filename     = "model_int8.onnx"
size_bytes   = 330822212
sha256       = "e3ec3dc2eed868be0ae320051f4ed5d70ae072dae075bd255cf5b25835673cac"
url          = "https://huggingface.co/gmougeot/lepinet-bioclip2-vitl14/resolve/c84edd897829c38db599682eb735a5c730ff8d46/model_int8.onnx"
released     = 2026-09-29
note         = "Same model for CPUs: 1.6-1.8x faster and 4x smaller than fp32, within 0.1 pt species macro-F1 on two evaluation sets and 0.7 pt on the third. Needs onnxruntime >= 1.22."

[[assets]]
key          = "dinov3-convnextl"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-dinov3-convnextl"
revision     = "366a9892990cfa74d092ecddaf6a2dd04d6dc0f1"
revision_kind = "commit"
gated        = false
variant      = "DINOv3 ConvNeXt-L (mid-size)"
filename     = "model.onnx"
size_bytes   = 868685389
sha256       = "db66ec81210d7fa2ca7372ad6f75b96844c444025f2c0aaf811d37823a62246c"
url          = "https://huggingface.co/gmougeot/lepinet-dinov3-convnextl/resolve/366a9892990cfa74d092ecddaf6a2dd04d6dc0f1/model.onnx"
released     = 2026-09-29
note         = "217 M parameters, 320x320 input. Close behind the ViT (within noise on trap images, 1.5 points behind on photos), less reliable confidence. LICENCE DIFFERS: DINOv3 License (a derivative of Meta's DINOv3), plus a non-commercial request for the training data. int8 (CPU) and fp16 (GPU) files in the same repo."

[[assets]]
key          = "effnetv2s"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-effnetv2s"
revision     = "2c8f28357adaa3baf05a4fc068c8c5c95b9d1fcc"
revision_kind = "commit"
gated        = false
variant      = "EfficientNetV2-S (small)"
filename     = "model.onnx"
size_bytes   = 148950976
sha256       = "4e48e3a93df1ee877a327267d26b96b9194520b8e1c0481c3c514b231b3a7a42"
url          = "https://huggingface.co/gmougeot/lepinet-effnetv2s/resolve/2c8f28357adaa3baf05a4fc068c8c5c95b9d1fcc/model.onnx"
released     = 2026-09-29
note         = "37 M parameters, 256x256 input, CPU-friendly; about 2 points behind the ViT. model_fp16.onnx (109 MB) in the same repo."
+++

> Identifies moths and butterflies to species, genus and family from a photo of a single specimen.

**Intended use.** Naming a photographed moth or butterfly: from citizen-science photos, museum
images, or crops from automated light-trap cameras. It classifies one specimen per image. For trap
screens or scenes, pair it with a detector such as flatbug and classify the crops. It is built to
say *how sure* it is: below its thresholds it backs off from species to genus or family, or answers
"unknown".

## Architecture and training

Three sizes of the same recipe, each in its own Hugging Face repo:

- **BioCLIP-2 ViT-L/14** (recommended, 321 M parameters). BioCLIP-2's image tower, fine-tuned end to
  end with a cosine classifier.
- **DINOv3 ConvNeXt-L** (217 M parameters). DINOv3's self-supervised backbone, fine-tuned with a
  cosine classifier under an ArcFace margin. Distributed under the DINOv3 License.
- **EfficientNetV2-S** (37 M parameters). ImageNet-initialised, with a cosine classifier trained
  under an ArcFace margin.

All three are trained on 6.3 M GBIF occurrence images of Lepidoptera (species with at least 50
images, capped at about 2,000 per species). All three are then made robust to automated light-trap
imagery by **self-training**: about 2 % of training is unlabelled trap crops with pseudo-labels. In
every published file, genus and family probabilities are sums of their species' probabilities, so
the three ranks never contradict each other. Framework: PyTorch/fastai, exported to ONNX.

## Inputs and outputs

One RGB image, resized on its shorter side to 256 (ViT, which resamples it to 224 internally as in
training), 320 (ConvNeXt) or 256 (EfficientNet) and centre-cropped.
Pixel values go in as [0, 1]; normalisation is inside the ONNX graph. Outputs are species, genus and
family probabilities, species logits, and an L2-normalised embedding (1024-d, 1536-d or 1280-d respectively). Labels are
GBIF taxon keys, with scientific names in `names.json`. The repo's `predict.py` needs only
`onnxruntime`, `numpy` and `Pillow`.

## Performance

Species macro-F1 (every species weighted equally), measured on the published ONNX files with the
cards' own preprocessing. The ViT's in-distribution number is inflated slightly: BioCLIP-2's
pre-training saw part of the GBIF test fold. On the 217,856-image subset it never saw, the ViT
scores 0.910.

| evaluation set | BioCLIP-2 ViT-L/14 | DINOv3 ConvNeXt-L | EfficientNetV2-S |
|---|---|---|---|
| GBIF photos, full test fold: 629,742 images, 12,041 species (in-distribution) | **0.921** | 0.906 | 0.899 |
| Probe: light-trap images, unseen nights (domain shift) | **0.783** | 0.777 | 0.765 |
| Probe, held-out species (never seen in trap images) | **0.785** | 0.771 | 0.772 |

"Probe" is 15,200 light-trap images (368 Danish species) from capture nights never used in training.
"Held-out species" is the 58 of those species for which no trap image was used at all. At a 95 %
precision target (thresholds fitted on half the capture nights, verified on the other half), the
ViT answers 90 % of trap images with 96 % precision, the ConvNeXt 81 % and the EfficientNet 90 %
with 95 %, either at species or at a coarser rank. On 3,171 photos of 591 species *outside* the label
set, the ViT wrongly commits to a species on only 17 % (ConvNeXt 21 %, EfficientNet 25 %), and
otherwise backs off to a mostly correct genus or family, or says "unknown".

## Limitations

- **One specimen per image**; it does not detect.
- **Closed label set.** A species outside the 12,041 still gets one of them. The thresholds and the
  embedding help to flag it, but do not guarantee it.
- **Geographic bias.** Training images are 36 % North American and 33 % European; South America and
  Africa together are 6 %. Expect the tropics to be served worse.
- **Domain shift.** Accuracy on trap images is about 13 points below curated GBIF photos. The
  shipped thresholds are fitted on Danish light traps and should be re-fitted for other cameras.
- **Adults.** Larvae are about 1 % of training images.

## How to obtain the weights

Public, ungated Hugging Face repos, grouped in a
[collection](https://huggingface.co/collections/gmougeot/lepinet-lepidoptera-identification-6abbc33d250430f8c67db428).
The ViT and EfficientNet weights are licensed **CC-BY-NC-4.0** (non-commercial), because most
training images are CC-BY-NC. The **ConvNeXt is the exception**: as a derivative of DINOv3 it is
distributed under the **DINOv3 License**, with a separate request for non-commercial use. The
training code is GPL-3.0. Each repo ships fp32, int8 (CPU) and fp16 (GPU) ONNX files (the
EfficientNet has no int8), and the ViT also loads with `transformers` (`trust_remote_code=True`).
The asset links above are pinned to the curated commit.

## Citation

```bibtex
@software{mougeot_lepinet_2026,
  author = {Mougeot, Guillaume},
  title  = {lepinet: hierarchical Lepidoptera identification that knows what it does not know},
  year   = {2026},
  url    = {https://github.com/GuillaumeMougeot/lepinet}
}
```

Training data: GBIF.org (15 May 2025) GBIF Occurrence Download https://doi.org/10.15468/dl.hg37y9.
