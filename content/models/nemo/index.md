+++
title = "Nemo"
description = "Hierarchical classification of adult moths and butterflies, with GBIF taxon labels and image embeddings."
foundation = false
purpose = ["Insect classification", "Model embeddings"]
task = ["Classification", "Embedding"]
architecture = ["EfficientNetV2-S with normalized hierarchical classifier"]
year = 2026
license = "CC-BY-NC-SA-4.0"
status = "published"
training_data = ["unpublished"]
date = 2026-10-13
vocabulary_scope = "closed"
geographic_scope = "Global; regional presets restrict the species vocabulary"
produces = ["label", "embedding"]
target_taxonomic_rank = ["family", "genus", "species"]
image_input_size = "384x384 RGB; use the published preprocessing adapter"
taxonomic_coverage = "Adult Lepidoptera: 12,632 species, 4,476 genera and 104 families"
developer = "Asger Svenning"
code_url = "https://github.com/asgersvenning/mini_trainer"
hosting_status = "link_only"
commercial_use = "prohibited"
weight_format = ["PyTorch", "ONNX"]
hf_repo = "asgersvenning/MAMBO-v3"
hf_revision = "a70e530787b731276ba5e6dc8429e3627e370ce5"

[[assets]]
key = "pytorch"
provider = "huggingface"
repo_id = "asgersvenning/MAMBO-v3"
revision = "a70e530787b731276ba5e6dc8429e3627e370ce5"
revision_kind = "commit"
filename = "bundle/models/pytorch/best.pt"
size_bytes = 153951029
sha256 = "174b9214bfea2df69e4f5c5d16afd841fec961db4274f3e6bf474cef9cab5e8a"
url = "https://huggingface.co/asgersvenning/MAMBO-v3/resolve/a70e530787b731276ba5e6dc8429e3627e370ce5/bundle/models/pytorch/best.pt"
note = "Native checkpoint; use the published runtime and class vocabulary."

[[assets]]
key = "onnx"
provider = "huggingface"
repo_id = "asgersvenning/MAMBO-v3"
revision = "a70e530787b731276ba5e6dc8429e3627e370ce5"
revision_kind = "commit"
filename = "bundle/models/onnx/model.onnx"
size_bytes = 1527453
sha256 = "aa02baa22765a04de03c5ba46029e2a66ca7e430bfddce0a001af5cec2e7c15d"
url = "https://huggingface.co/asgersvenning/MAMBO-v3/resolve/a70e530787b731276ba5e6dc8429e3627e370ce5/bundle/models/onnx/model.onnx"
note = "Classification graph; requires model.onnx.data from the same directory."

[[assets]]
key = "onnx-data"
provider = "huggingface"
repo_id = "asgersvenning/MAMBO-v3"
revision = "a70e530787b731276ba5e6dc8429e3627e370ce5"
revision_kind = "commit"
filename = "bundle/models/onnx/model.onnx.data"
size_bytes = 151838720
sha256 = "9ffb389ec4c6fe9864a4dfb16b167cf68950d7fa35b3fa39d84b1987b1845f4e"
url = "https://huggingface.co/asgersvenning/MAMBO-v3/resolve/a70e530787b731276ba5e6dc8429e3627e370ce5/bundle/models/onnx/model.onnx.data"
note = "External tensors for the classification graph."

[[assets]]
key = "onnx-embedding"
provider = "huggingface"
repo_id = "asgersvenning/MAMBO-v3"
revision = "a70e530787b731276ba5e6dc8429e3627e370ce5"
revision_kind = "commit"
filename = "bundle/models/onnx-embedding/model.onnx"
size_bytes = 1932003
sha256 = "70130c3dbc2b8a6bc4610bb213a1aaf029816fb634faf104bbb27ffa997dfc44"
url = "https://huggingface.co/asgersvenning/MAMBO-v3/resolve/a70e530787b731276ba5e6dc8429e3627e370ce5/bundle/models/onnx-embedding/model.onnx"
note = "Embedding graph; requires its accompanying model.onnx.data."

[[assets]]
key = "onnx-embedding-data"
provider = "huggingface"
repo_id = "asgersvenning/MAMBO-v3"
revision = "a70e530787b731276ba5e6dc8429e3627e370ce5"
revision_kind = "commit"
filename = "bundle/models/onnx-embedding/model.onnx.data"
size_bytes = 151838720
sha256 = "9ffb389ec4c6fe9864a4dfb16b167cf68950d7fa35b3fa39d84b1987b1845f4e"
url = "https://huggingface.co/asgersvenning/MAMBO-v3/resolve/a70e530787b731276ba5e6dc8429e3627e370ce5/bundle/models/onnx-embedding/model.onnx.data"
note = "External tensors for the embedding graph."
+++

**Intended use.** Classify photographs or detector crops of individual adult moths
and butterflies. Nemo (MAMBO_v3) returns hierarchical GBIF labels and optional
1,280-dimensional embeddings; it does not locate insects within an image.

The model was trained for 30 epochs on 5,063,857 GBIF-sourced images in the
global-lepi collection, whose training image set is not bundled with the release.
The [published provenance](https://huggingface.co/asgersvenning/MAMBO-v3/resolve/a70e530787b731276ba5e6dc8429e3627e370ce5/bundle/MODEL_PROVENANCE.toml) records training and checkpoint identity,
including the limits of the reconstructed initialization history.

Use the [deployment API](https://github.com/asgersvenning/mini_trainer/blob/models/mambo-v3/v0.3.1/deployment/README.md)
for decoding, resizing and normalization. Regional presets and custom species
lists filter predictions from the same global model; they are not separately
trained checkpoints. The ONNX runtime is the default CPU option; PyTorch also
supports CUDA.

**Limits.** The vocabulary is closed and targets adults. Confidence thresholds
and performance depend on image domain and selected scope. See the
[pinned model card](https://huggingface.co/asgersvenning/MAMBO-v3/blob/a70e530787b731276ba5e6dc8429e3627e370ce5/README.md) for evaluations on GBIF, camera-trap crops and
recent iNaturalist images. Model weights are non-commercial CC-BY-NC-SA-4.0;
the runtime code is MIT-licensed.
