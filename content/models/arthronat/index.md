+++
# ── Identity ────────────────────────────────────────────────────────
title              = "ArthroNat"
description        = "YOLO11 model trained on arthropods over natural backgrounds."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection"]
architecture       = ["YOLO11"]
base_model         = "https://huggingface.co/Ultralytics/YOLO11"
year               = 2026
license            = "AGPLv3"
status             = "published"
training_data      = ["https://github.com/edgaremy/arthropod-detection-dataset/tree/95a3bea80bcc0dc6e5bf20a28b436a9c30cffbf7/src", "10.5281/zenodo.14761447"]
date               = 2026-05-08

# Optional - delete a line to take the default shown.
vocabulary_scope   = "open"
geographic_scope   = "France"
produces           = ["bbox"]
output_format      = ["ultralytics-detect-results"]
image_input_size   = "640x640"
input_modality     = ["image"]
developer          = "Remy et al."
paper_url          = "https://www.biorxiv.org/content/10.64898/2026.05.06.723207v1.full"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "prohibited"
weight_format      = ["PyTorch", "ONNX"]

# ── The model's own card elsewhere, if it has one ───────────────────
hf_repo            = "edgaremy/arthropod-detector"
hf_revision        = "54edf7364582e9efda68c04edfd672cfe109fb4a"

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "hf-repo"
provider     = "huggingface"
repo_id      = "edgaremy/arthropod-detector"
revision     = "8b8dfa2b5904395566232c2308b928f113ee8645"
revision_kind = "commit"
gated        = false
url          = "https://huggingface.co/edgaremy/arthropod-detector"
note         = "Eight files: four trained variants, each as .pt and .onnx."

[[assets]]
key          = "n-mosaic33"
provider     = "huggingface"
repo_id      = "edgaremy/arthropod-detector"
variant      = "YOLO11n, mosaic33"
filename     = "yolo11n_ArthroNat_mosaic33.pt"
revision     = "54edf7364582e9efda68c04edfd672cfe109fb4a"
revision_kind = "commit"
url          = "https://huggingface.co/edgaremy/arthropod-detector/resolve/54edf7364582e9efda68c04edfd672cfe109fb4a/yolo11n_ArthroNat_mosaic33.pt"

[[assets]]
key          = "n-flatbug"
provider     = "huggingface"
repo_id      = "edgaremy/arthropod-detector"
variant      = "YOLO11n, ArthroNat + FlatBug"
filename     = "yolo11n_ArthroNat%2Bflatbug.pt"
revision     = "54edf7364582e9efda68c04edfd672cfe109fb4a"
revision_kind = "commit"
url          = "https://huggingface.co/edgaremy/arthropod-detector/resolve/54edf7364582e9efda68c04edfd672cfe109fb4a/yolo11n_ArthroNat%2Bflatbug.pt"

[[assets]]
key          = "l-mosaic33"
provider     = "huggingface"
repo_id      = "edgaremy/arthropod-detector"
variant      = "YOLO11l, mosaic33"
filename     = "yolo11l_ArthroNat_mosaic33.pt"
revision     = "54edf7364582e9efda68c04edfd672cfe109fb4a"
revision_kind = "commit"
url          = "https://huggingface.co/edgaremy/arthropod-detector/resolve/54edf7364582e9efda68c04edfd672cfe109fb4a/yolo11l_ArthroNat_mosaic33.pt"

[[assets]]
key          = "l-flatbug"
provider     = "huggingface"
repo_id      = "edgaremy/arthropod-detector"
variant      = "YOLO11l, ArthroNat + FlatBug"
filename     = "yolo11l_ArthroNat%2Bflatbug.pt"
revision     = "54edf7364582e9efda68c04edfd672cfe109fb4a"
revision_kind = "commit"
url          = "https://huggingface.co/edgaremy/arthropod-detector/resolve/54edf7364582e9efda68c04edfd672cfe109fb4a/yolo11l_ArthroNat%2Bflatbug.pt"
+++

> YOLO11 model trained on arthropods over natural backgrounds.

**Intended use.** ArthroNat is for arthropods photographed in the field, against vegetation,
soil and other natural substrate, the setting where an insect is a small part of a visually
busy frame. It is the counterpart to FlatBug, which is built for uniform backgrounds.

## Architecture and training

- **Architecture:** YOLO11, as `n` and `l` variants
- **Task:** Object Detection (bounding boxes)
- **Trained on:** ArthroNat; two training mixes are published: the base ArthroNat data, and
  a variant additionally trained on FlatBug data
- **Taxonomic coverage:** not published as a fixed class list in this registry
- **Framework:** ultralytics

## Inputs and outputs

- **Input size:** 640x640
- **Channel order:** RGB
- **Outputs:** bounding boxes
- **Input modality:** image only (discriminative model)

## Performance

Check the source publication for metrics.

| Metric | Value | Evaluation set |
| --- | --- | --- |
| mAP@50 | see source publication | see source publication |

## Limitations

## License and rights

- **License:** MIT
- **Commercial use:** allowed
- **Restrictions:** None stated.
- **Upstream source:** <https://huggingface.co/edgaremy/arthropod-detector>

## Citation

```bibtex
@article{arthronat2026,
  title   = {ArthroNat: arthropod detection over natural backgrounds},
  author  = {Emy, Edgar et al.},
  journal = {bioRxiv},
  year    = {2026},
  note    = {https://www.biorxiv.org/content/10.64898/2026.05.06.723207v1.full}
}
```

## How to obtain the weights

From Hugging Face, pinned to commit `54edf736`. The repository holds eight files, four
trained variants, each published in both PyTorch and ONNX form:

| Variant | PyTorch | ONNX |
| --- | --- | --- |
| YOLO11n, mosaic33 | `yolo11n_ArthroNat_mosaic33.pt` | `yolo11n_ArthroNat_mosaic33.onnx` |
| YOLO11n, ArthroNat + FlatBug | `yolo11n_ArthroNat+flatbug.pt` | `yolo11n_ArthroNat+flatbug.onnx` |
| YOLO11l, mosaic33 | `yolo11l_ArthroNat_mosaic33.pt` | `yolo11l_ArthroNat_mosaic33.onnx` |
| YOLO11l, ArthroNat + FlatBug | `yolo11l_ArthroNat+flatbug.pt` | `yolo11l_ArthroNat+flatbug.onnx` |

No authentication is required.

```bash
from huggingface_hub import hf_hub_download

path = hf_hub_download(
    repo_id="edgaremy/arthropod-detector",
    filename="yolo11n_ArthroNat_mosaic33.pt",
    revision="54edf7364582e9efda68c04edfd672cfe109fb4a",
)
```

## Output format probe

The author-documented Ultralytics Python interface was probed on CPU with the pinned YOLO11n mosaic33 checkpoint. It returned Results objects with pixel-coordinate boxes; no JSON export was requested. Other weight variants were not run.

Probe date: 2026-09-30. Reproducible setup and evidence are in
[src/probe](https://github.com/InsectAI-COST-Action/model-db/tree/main/src/probe).
