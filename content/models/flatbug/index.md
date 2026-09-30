+++
# ── Identity ────────────────────────────────────────────────────────
title              = "flatbug"
description        = "Detects and segments terrestrial arthropods of any size on flat, uniform backgrounds, tiling large images at native resolution."

# ── Catalogue ───────────────────────────────────────────────────────
category           = "detection"
task               = ["Object Detection", "Instance Segmentation"]
architecture       = ["YOLOv8-seg","YOLO26-seg"]
base_model         = "Ultralytics yolov8{n,s,m,l}-seg; yolo26m-seg for M v2"
year               = 2026
license            = "MIT"
status             = "published"
date               = 2026-09-21

# Optional - delete a line to take the default shown.
vocabulary_scope   = "closed"
geographic_scope   = "Global"
produces           = ["bbox", "mask"]
output_format      = ["flatbug", "flatbug"]
image_input_size   = "any"
taxonomic_coverage = "Terrestrial arthropods, as a single class"
developer          = "Asger Svenning, Quentin Geissmann et al."
paper_url          = "https://doi.org/10.1111/2041-210x.70249"
code_url           = "https://github.com/darsa-group/flat-bug"

# ── Weights ─────────────────────────────────────────────────────────
hosting_status     = "link_only"
commercial_use     = "allowed"
weight_format      = ["PyTorch"]

# ── The files this model ships. The FIRST one is the link the table shows. ──

[[assets]]
key          = "share-index"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
url          = "https://anon.erda.au.dk/cgi-sid/ls.py?share_id=Bb0CR1FHG6"
note         = "ERDA share root: models/ (the five weight files), fb_yolo/ (training data) and manuscript/."

[[assets]]
key          = "m-v2"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLO26m (M v2, default)"
filename     = "models/flat_bug_M_v2.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_M_v2.pt"
size_bytes   = 54585258
released     = 2026-07-07
note         = "Default weights since flat-bug 1.2.0. Not evaluated in the paper."

[[assets]]
key          = "n"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8n"
filename     = "models/flat_bug_N.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_N.pt"
size_bytes   = 6275129
released     = 2024-10-23

[[assets]]
key          = "s"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8s"
filename     = "models/flat_bug_S.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_S.pt"
size_bytes   = 21398649
released     = 2024-10-23

[[assets]]
key          = "m"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8m"
filename     = "models/flat_bug_M.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_M.pt"
size_bytes   = 49694305
released     = 2024-10-23

[[assets]]
key          = "l"
provider     = "erda"
share_id     = "Bb0CR1FHG6"
variant      = "YOLOv8l"
filename     = "models/flat_bug_L.pt"
url          = "https://anon.erda.au.dk/share_redirect/Bb0CR1FHG6/models/flat_bug_L.pt"
size_bytes   = 84085321
released     = 2024-10-23
note         = "The best model in the paper (F1 94.2%)."

[[assets]]
key          = "pypi"
provider     = "package"
url          = "https://pypi.org/project/flat-bug/"
note         = "The flat-bug Python package. It downloads the weight file you name from the ERDA share the first time you use it."
+++

> Detects and segments terrestrial arthropods of any size on flat, uniform backgrounds, tiling large images at native resolution.

**Intended use.** flatbug is one model for finding and outlining every arthropod in an
image. It works best on top-down images of flat surfaces: scans, light boxes, sticky
traps, light-trap sheets, conveyor belts and laboratory arenas. It accepts images of any
size and finds specimens that are either very small or very large relative to the frame,
so it suits high-resolution trap images and crowded scenes. It says *where* the
arthropods are, not *what* they are: all instances are one class.

## Architecture and training

- **Architecture:** Ultralytics YOLO instance-segmentation models, wrapped in flatbug's
  own pyramid-tiling inference. The paper's models are YOLOv8-seg in four sizes (N, S, M,
  L), fine-tuned from the Ultralytics checkpoints. `flat_bug_M_v2.pt` (July 2026) is a
  YOLO26m-seg. flat-bug 1.2.0 uses it by default.
- **Task:** object detection and instance segmentation (boxes and masks).
- **Trained on:** the flatbug dataset. It combines 23 public and newly annotated
  datasets from laboratory and field imaging systems: 6,131 images and 113,550
  annotated arthropods, split into 5,153 training and 978 validation images. The
  compilation is on Zenodo ([10.5281/zenodo.14761446](https://doi.org/10.5281/zenodo.14761446),
  CC-BY-4.0), and a YOLO-formatted copy is in `fb_yolo/` in the ERDA share.
- **Training schedule:** a modified Ultralytics training loop with 1024 px tiles and
  flatbug's own augmentations (`fb_train`).
- **Framework:** PyTorch and Ultralytics (`ultralytics>=8.4,<=8.4.90` for flat-bug 1.2.0).

## Inputs and outputs

- **Input:** an RGB image of any size, or a video (`fb_predict`).
- **How it runs:** the model always sees 1024×1024 tiles. flatbug first scales the whole
  image down to fit one tile. It then runs again at larger scales, 1.5× per step, until
  it reaches native resolution. Tiles overlap, and non-maximum suppression merges the
  detections from all tiles and scales. So the input size really is "any". The cost is
  run time, which grows with image area.
- **Outputs:** one box, contour (polygon) and confidence score per instance. Results can
  be exported as JSON or COCO, as crops and as overlay plots.
- **Defaults worth knowing:** confidence threshold 0.2 and NMS IoU threshold 0.2. The
  minimum object size is 32 px, measured as the square root of the box area; at native
  resolution this is the smallest object flatbug reports. Every default can be changed
  with a YAML config.

## Performance

Reported in the paper. Validation was on the held-out split of the flatbug dataset (978
images, 21,409 instances, 23 sub-datasets). The figure is the median F1 across
sub-datasets, with a 95% interval.

| Model | F1 | Evaluation set |
| --- | --- | --- |
| YOLOv8l (`flat_bug_L.pt`) | 94.2% [91.1, 95.7] | flatbug validation split |
| YOLOv8m (`flat_bug_M.pt`) | 93.1% [90.3, 94.6] | flatbug validation split |
| YOLOv8s (`flat_bug_S.pt`) | 92.8% [89.5, 94.5] | flatbug validation split |
| YOLOv8n (`flat_bug_N.pt`) | 91.7% [86.1, 93.7] | flatbug validation split |
| YOLO26m (`flat_bug_M_v2.pt`) | Not reported in the source publication | — |

In leave-one-dataset-out tests, the model was scored on imaging systems it had never
seen in training. F1 fell by 7.1% on average (95% interval: 0.9% to 12.5%), mostly
because recall dropped. Fine-tuning on the new system recovered the loss.

## Limitations

- **Localisation only.** One class. Identifying taxa needs a separate classifier run on
  the crops.
- **Flat, uniform backgrounds.** Training images are mostly top-down views of flat
  surfaces. On cluttered natural backgrounds (flowers, foliage, soil), expect more
  missed and false detections; the detection-heterogeneous models suit that better.
- **New imaging systems cost about 7% F1**, mostly as missed specimens. Validate on your
  own images before relying on counts, and fine-tune if you can.
- **Very small objects.** By default, flatbug drops detections smaller than 32 px at
  native resolution. Specimens only a few pixels across are not recovered.
- **Mask detail.** By default each instance's mask is a single polygon, with no holes.
  Set `PREFER_POLYGONS: false` to get raster masks instead; these are capped at 1024 px.
- **The default model changed.** flat-bug 1.2.0 uses `flat_bug_M_v2.pt`, which has no
  published evaluation. Earlier releases used `flat_bug_M.pt`. For results that match
  the paper, pass the weights file explicitly (`-w flat_bug_L.pt`).
- **Run time** grows with image area and with the number of pyramid levels. Very large
  scans are slow on a CPU.

## License and rights

- **License:** MIT, the license of the flat-bug repository. The ERDA share has no
  separate license file for the weights. The Zenodo dataset is CC-BY-4.0.
- **Commercial use:** allowed under MIT. However, the weights are Ultralytics YOLO
  checkpoints: they carry Ultralytics' AGPL-3.0 notice in their metadata, and you need
  the `ultralytics` package, which is AGPL-3.0, to run them. For closed-source
  commercial use, check whether you need an Ultralytics Enterprise License.
- **Hosting:** the weights are on a public ERDA share at Aarhus University, with no
  DOI. The authors could regenerate or withdraw the share, and the files can change
  without a version bump.
- **Upstream source:** <https://github.com/darsa-group/flat-bug>

## Citation

```bibtex
@article{svenning2026flatbug,
  title   = {A general method for detection and segmentation of terrestrial arthropods in images},
  author  = {Svenning, Asger and Mougeot, Guillaume and Alison, Jamie and Chevalier, Daphne
             and Molina, Nisa Chavez and Ong, Song-Quan and Bjerge, Kim and Carrillo, Juli
             and H{\o}ye, Toke Thomas and Geissmann, Quentin},
  journal = {Methods in Ecology and Evolution},
  volume  = {17},
  number  = {3},
  pages   = {727--739},
  year    = {2026},
  doi     = {10.1111/2041-210x.70249}
}
```

## How to obtain the weights

The easiest way is the Python package. It fetches weights from the ERDA share the first
time you use them:

```bash
uv pip install flat-bug --torch-backend=auto
fb_predict -i <image_dir> -o <output_dir> -w flat_bug_L.pt
```

Leave out `-w` to use the default `flat_bug_M_v2.pt`. To download by hand, the five `.pt`
files are in `models/` in ERDA share `Bb0CR1FHG6`. You do not need an account:

| Variant | File | Size | Released |
| --- | --- | --- | --- |
| YOLO26m (v2, default) | `models/flat_bug_M_v2.pt` | 54.6 MB | 2026-07-07 |
| YOLOv8n | `models/flat_bug_N.pt` | 6.3 MB | 2024-10-23 |
| YOLOv8s | `models/flat_bug_S.pt` | 21.4 MB | 2024-10-23 |
| YOLOv8m | `models/flat_bug_M.pt` | 49.7 MB | 2024-10-23 |
| YOLOv8l | `models/flat_bug_L.pt` | 84.1 MB | 2024-10-23 |

The same share also holds `fb_yolo/` (the training dataset in YOLO format) and
`manuscript/`.
