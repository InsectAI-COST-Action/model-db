+++
# ── Identity ────────────────────────────────────────────────────────
title              = "BioMoth"
description        = "Single-class YOLO11s detector that counts moths on blacklight-sheet photos, with a size-bin lookup that turns the boxes into a biomass estimate, as a non-lethal alternative to bucket light traps."
foundation         = false

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection", "Counting"]
architecture       = ["YOLO11s"]
output_format      = ["biomoth-csv"]
base_model         = ""
year               = 2026
license            = "Apache-2.0"
status             = "published"
training_data      = ["unpublished"]
date               = 2026-09-30

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Hubbard Brook Experimental Forest, New Hampshire, USA"
produces           = ["bbox", "count"]
target_taxonomic_rank = ["NA"]
image_input_size   = "640x640"
taxonomic_coverage = "Lepidoptera (one class, 'Moth'; no genus or species identification)"
developer          = "Lutz, David A.; Suhavi, Suhavi et al. (Colby-Sawyer College, Dartmouth College)"
paper_url          = "https://doi.org/10.2139/ssrn.6943698"
code_url           = "https://github.com/Suhavi/Lepidoptera_Hubbard_Brook"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "unknown"
weight_format      = ["PyTorch"]

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "weights"
provider     = "github"
filename     = "best.torchscript"
size_bytes   = 38226894
sha256       = "a1cb34d3ec32076a0b160673addaf534697acc92b8a0f87ce5c59681f9c0eae7"
url          = "https://raw.githubusercontent.com/Suhavi/Lepidoptera_Hubbard_Brook/1d631ce7af4c0fa8eae5d60d8f2ec352fa2644f3/models/best.torchscript"
note         = "TorchScript export only (no .pt or ONNX). Trained with Ultralytics 8.3.153, file dated 2025-06-12. Pinned to commit 1d631ce."
+++

> Counts moths on blacklight-sheet photos and estimates their biomass from box sizes.

**Intended use.** Non-lethal monitoring of moth abundance and biomass from a camera photographing
a UV-lit sheet at fixed intervals through the night. It was built to replace lethal bucket light
traps in long-term ecological studies. It answers *how many moths, and how much moth mass*, not
*which moths*.

## Architecture and training

- **Architecture:** Ultralytics YOLO11s, one class (`Moth`), 640x640 input.
- **Trained on:** blacklight-sheet photos from Hubbard Brook Experimental Forest (NH, USA).
  - Five watershed sites, mid-June to mid-September 2023.
  - One photo every 10 minutes from 22:00 to 04:00, with a single Nikon camera setup.
- **Data:** the raw images are published on EDI (see Citation). The training/validation split and
  the box annotations are not released.
- **Biomass step:** this is not a learned model.
  - Box width and height are converted to cm² with a hard-coded camera-to-sheet geometry (130 cm
    distance, about 44x83 cm frame).
  - Each box goes into one of four log2 area bins, and each bin gets a fixed mean mass (2.75, 54,
    361 or 418 mg). The masses are summed.

## Inputs and outputs

- **Input:** RGB sheet photos, letterboxed to 640. The source photos are about 6000 px wide.
- **Output:** A custom batch CSV containing boxes, confidence, class and measurements after TorchScript inference and author postprocessing.
- **Thresholds:** the README recommends `conf = 0.23`, while the inference notebook uses 0.25,
  with NMS IoU 0.5.
- **Counts and biomass** are aggregated per image and per night in the `runTrends` notebook.

The documented [BioMoth CSV profile](/formats/detection/biomoth-csv.json) follows `runInference.ipynb` at revision `1d631ce`. Its active batch export writes 15 columns, including original-image pixel boxes, confidence, class, image/site metadata and calibrated dimensions. A CPU probe of the real TorchScript checkpoint and original notebook functions produced 32 rows on a specimen fixture and none on a blank control. The hard-coded year and calibration factors are preserved; this does not validate physical measurements on that fixture.

## Performance

| Metric | Value | Evaluation set |
| --- | --- | --- |
| mAP@0.5 (moth) | 0.912 | Hubbard Brook 2023 sheet images; split not stated in the available metadata |
| F1 | 0.91 at conf 0.23 | Repository README; test set not described |

It is not confirmed whether the repository checkpoint (dated June 2025) is the exact one behind the
preprint's numbers.

## Limitations

- **Single class.** All Lepidoptera become `Moth`. There is no family, genus or species output, and
  no reported analysis of other insects (caddisflies, beetles) being counted as moths.
- **Coarse biomass.** Four fixed-mass bins from 2-D box area, with no per-species allometry. The
  pixel-to-cm factor assumes the authors' exact camera distance and framing, so it must be
  recalibrated for any other setup.
- **Small moths.** Photos are about 6000 px wide and are downscaled to 640. Very small moths are
  likely to be missed. This is not a reported result.
- **Relative index, not absolute counts.** Detection is per frame with no tracking, so a resting
  moth is counted again in every 10-minute frame.
- **One site network.** One forest, one season, one camera setup. It has not been validated
  elsewhere.
- **Preprint.** The paper is not yet peer-reviewed.

## How to obtain the weights

A plain file in the GitHub repository (not Git LFS), downloadable without login. The asset link is
pinned to commit `1d631ce7af4c0fa8eae5d60d8f2ec352fa2644f3`. It loads with
`ultralytics.YOLO("best.torchscript", task="detect")`.

**License:** the repository is licensed **Apache-2.0**. The weight file's embedded Ultralytics
metadata reads AGPL-3.0, as every Ultralytics YOLO11 export does. Commercial use is therefore
recorded as unknown. Check with the authors, and with the Ultralytics license, before commercial
use.

## Citation

```bibtex
@article{lutz_biomoth_2026,
  author  = {Lutz, David A. and Suhavi, Suhavi and Jones, Jessica S. and Aldrich, Quinn M. and
             Cummings, Wyatt J. and Cui, Kangning and Ayres, Matthew P.},
  title   = {{BioMoth}: Non-Lethal Estimation of Moth Abundance and Biomass from Blacklight Sheet
             Imagery Using Computer Vision},
  journal = {SSRN preprint},
  year    = {2026},
  doi     = {10.2139/ssrn.6943698}
}
```

Images: Suhavi, S., D.A. Lutz, J.S. Jones, M.P. Ayres. 2026. Blacklight Sheet Invertebrate Photos
at Hubbard Brook Experimental Forest; 2023 ver 1. Environmental Data Initiative.
https://doi.org/10.6073/pasta/7ac5818bb45bb42c2d935ce7e3756c00
