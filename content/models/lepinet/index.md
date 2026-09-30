+++
# ── Identity ────────────────────────────────────────────────────────
title              = "lepinet"
description        = "Identifies moths and butterflies to species, genus and family from a photo of a single specimen, with coherent ranks and confidence thresholds for backing off to a coarser rank."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "classification"
task               = ["Classification", "Embedding"]
architecture       = "ViT-L/14 (BioCLIP-2); ConvNeXt-L (DINOv3); EfficientNetV2-S"
base_model         = "imageomics/bioclip-2"
year               = 2026
license            = "CC-BY-NC-4.0"
status             = "published"
date               = 2026-09-29

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Global (mostly North America and Europe)"
produces           = ["label", "embedding"]
image_input_size   = "224x224"
taxonomic_coverage = "Lepidoptera: 12,041 species, 4,333 genera, 102 families"
developer          = "Guillaume Mougeot (Aarhus University)"
code_url           = "https://github.com/GuillaumeMougeot/lepinet"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "prohibited"
weight_format      = ["ONNX", "Safetensors"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "gmougeot/lepinet-bioclip2-vitl14"
hf_revision        = "c239c14910fac8b07be1ace73334db778629b602"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "bioclip2-vitl14"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-bioclip2-vitl14"
revision     = "c239c14910fac8b07be1ace73334db778629b602"
revision_kind = "commit"
gated        = false
variant      = "BioCLIP-2 ViT-L/14 (recommended)"
filename     = "model.onnx"
size_bytes   = 1285434218
sha256       = "977d1efbf0015c8ac44e6dd8c31640a7a42ec55f187d401c320b93a0b796bd7c"
url          = "https://huggingface.co/gmougeot/lepinet-bioclip2-vitl14/resolve/c239c14910fac8b07be1ace73334db778629b602/model.onnx"
released     = 2026-09-29
note         = "Most accurate and best calibrated. 321 M parameters, 224x224 input, fp32. Taxonomy, names, thresholds, predict.py and a GPU fp16 file (model_fp16.onnx) are in the same repo."

[[assets]]
key          = "bioclip2-vitl14-int8"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-bioclip2-vitl14"
revision     = "c239c14910fac8b07be1ace73334db778629b602"
revision_kind = "commit"
gated        = false
variant      = "BioCLIP-2 ViT-L/14, int8 for CPUs"
filename     = "model_int8.onnx"
size_bytes   = 330820714
sha256       = "3216aff0fddc2cc1aa0d75271896b0dd02217729c94b9f2df149b9cab2331250"
url          = "https://huggingface.co/gmougeot/lepinet-bioclip2-vitl14/resolve/c239c14910fac8b07be1ace73334db778629b602/model_int8.onnx"
released     = 2026-09-29
note         = "Same model for CPUs: 1.6-1.8x faster and 4x smaller than fp32, within 0.1 pt species macro-F1 on two evaluation sets and 0.7 pt on the third. Needs onnxruntime >= 1.22."

[[assets]]
key          = "dinov3-convnextl"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-dinov3-convnextl"
revision     = "78bb30fcbd1f6eed828556ef0e416e5ed8fc2d0d"
revision_kind = "commit"
gated        = false
variant      = "DINOv3 ConvNeXt-L (mid-size)"
filename     = "model.onnx"
size_bytes   = 868685389
sha256       = "db66ec81210d7fa2ca7372ad6f75b96844c444025f2c0aaf811d37823a62246c"
url          = "https://huggingface.co/gmougeot/lepinet-dinov3-convnextl/resolve/78bb30fcbd1f6eed828556ef0e416e5ed8fc2d0d/model.onnx"
released     = 2026-09-29
note         = "217 M parameters, 320x320 input. As accurate as the ViT, less reliable confidence. LICENCE DIFFERS: DINOv3 License (a derivative of Meta's DINOv3), plus a non-commercial request for the training data. int8 (CPU) and fp16 (GPU) files in the same repo."

[[assets]]
key          = "effnetv2s"
provider     = "huggingface"
repo_id      = "gmougeot/lepinet-effnetv2s"
revision     = "142ef467d89acb8a206f00641f73bf6b300a070c"
revision_kind = "commit"
gated        = false
variant      = "EfficientNetV2-S (small)"
filename     = "model.onnx"
size_bytes   = 148950976
sha256       = "4e48e3a93df1ee877a327267d26b96b9194520b8e1c0481c3c514b231b3a7a42"
url          = "https://huggingface.co/gmougeot/lepinet-effnetv2s/resolve/142ef467d89acb8a206f00641f73bf6b300a070c/model.onnx"
released     = 2026-09-29
note         = "37 M parameters, 256x256 input, CPU-friendly; about half a point behind on light-trap images. model_fp16.onnx (109 MB) in the same repo."
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

Both are trained on 6.3 M GBIF occurrence images of Lepidoptera (species with at least 50 images,
capped at about 2,000 per species). Both are then made robust to automated light-trap imagery by
**self-training**: about 2 % of training is unlabelled trap crops with pseudo-labels. There is a
single species classifier; genus and family probabilities are sums of their species' probabilities,
so the three ranks never contradict each other. Framework: PyTorch/fastai, exported to ONNX.

## Inputs and outputs

One RGB image, resized on its shorter side to 224 (ViT) or 256 (EfficientNet) and centre-cropped.
Pixel values go in as [0, 1]; normalisation is inside the ONNX graph. Outputs are species, genus and
family probabilities, species logits, and an L2-normalised embedding (1024-d or 1280-d). Labels are
GBIF taxon keys, with scientific names in `names.json`. The repo's `predict.py` needs only
`onnxruntime`, `numpy` and `Pillow`.

## Performance

Species macro-F1 (every species weighted equally), measured on the published ONNX files with the
cards' own preprocessing. The ViT's in-distribution number is inflated slightly: BioCLIP-2's
pre-training saw part of the GBIF test fold. On the uncontaminated subset, the training pipeline
reports 0.911.

| evaluation set | BioCLIP-2 ViT-L/14 | DINOv3 ConvNeXt-L | EfficientNetV2-S |
|---|---|---|---|
| GBIF photos, random 10,000 test-fold images (in-distribution) | 0.925 | 0.926 | 0.910 |
| Probe: light-trap images, unseen nights (domain shift) | 0.772 | 0.777 | 0.765 |
| Probe, held-out species (never seen in trap images) | 0.790 | 0.771 | 0.772 |

"Probe" is 15,200 light-trap images (368 Danish species) from capture nights never used in training.
"Held-out species" is the 58 of those species for which no trap image was used at all. At a 95 %
precision target (thresholds fitted on half the capture nights, verified on the other half), the
ViT answers 87 % of trap images with 96 % precision, the ConvNeXt 81 % and the EfficientNet 90 %
with 95 %, either at species or at a coarser rank. On 3,171 photos of 591 species *outside* the label
set, the ViT wrongly commits to a species on only 14 % (ConvNeXt 21 %, EfficientNet 25 %), and
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
