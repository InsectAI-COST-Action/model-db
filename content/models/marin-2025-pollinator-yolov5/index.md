+++
# ── Identity ────────────────────────────────────────────────────────
title              = "Marin et al. (2025)"
description        = "YOLOv5 model trained on flower pollinators."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection"]
architecture       = "YOLOv5"
year               = 2025
license            = "CC-BY-4.0"
status             = "published"
date               = 2026-09-21

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
produces           = ["bbox"]
image_input_size         = "1024x1024"
developer          = "Marin et al."
paper_url          = "https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.70165"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"

# ── The model's own card elsewhere, if it has one ───────────────────

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "zenodo-record"
provider     = "zenodo"
record_id    = "17130918"
url          = "https://zenodo.org/records/17130918"

[[assets]]
key          = "github-repository"
provider     = "github"
repo         = "aranchalana/POLLINATOR/tree/v1.0"
url          = "https://github.com/aranchalana/POLLINATOR/tree/v1.0"

[[assets]]
key          = "weights"
provider     = "google-drive"
filename     = "best.pt"
url          = "https://drive.google.com/file/d/1p4N0oQ08S0RkFhy1Ddd9McqCHM1mCKQW/"
note         = "Model weights for the Marin et al. model."
+++

> YOLOv5 model trained on flower pollinators.

**Intended use.** Detecting flower-visiting insects in field imagery, at 1024x1024 input.

## Architecture and training

- **Architecture:** YOLOv5
- **Task:** Object Detection (bounding boxes)
- **Trained on:** flower pollinator imagery
- **Taxonomic coverage:** pollinators
- **Framework:** ultralytics YOLOv5

## Inputs and outputs

- **Input size:** 1024x1024
- **Channel order:** RGB
- **Outputs:** bounding boxes
- **Input modality:** image only (discriminative model only)

## Performance

See the source publication for evaluation metrics.

| Metric | Value | Evaluation set |
| --- | --- | --- |
| see source publication | — | — |

## Limitations

## License and rights

- **License:** CC-BY-4.0
- **Commercial use:** allowed
- **Restrictions:** Attribution required. Cite the source publication below.
- **Upstream source:** <https://zenodo.org/records/17130918>

## Citation

```bibtex
@article{marin2025pollinator,
  title   = {Automated detection of flower-visiting insects},
  author  = {Marin et al.},
  journal = {Methods in Ecology and Evolution},
  year    = {2025},
  doi     = {10.1111/2041-210X.70165}
}
```

## How to obtain the weights

From the Google Drive link in the assets section above. The weights are in a file named `best.pt`.
