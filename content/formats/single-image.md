+++
title = "Single-image prediction and ISIR"
+++

[Browse the format examples](../). ISIR describes detections on one image;
a batch is a collection of ISIR records, not one combined record.

## Try a conversion without installing a model

From a checkout of this repository:

```bash
python3 examples/formats/to_isir.py yolov5-detect-txt
python3 examples/formats/to_isir.py ultralytics-detect-json
python3 examples/formats/to_isir.py biomoth-csv
python3 examples/formats/to_isir.py coco
```

The script reads the small examples shown on these pages and prints ISIR JSON.
It does not download weights or run inference. Most examples use a 200 × 100
image with pixel box `[10,20,50,60]`; its ISIR box is `[30,60,40,40]` because
ISIR uses a bottom-left origin and center/width/height.

Single-image formats produce one object. BioMoth produces a list grouped by
image. The COCO example produces two records, including an explicitly empty
image. Example class vocabularies differ across formats: conversion does not
make the same integer mean the same taxon.

The Python adapter API and image-manifest examples are documented in
[the adapter README](https://github.com/InsectAI-COST-Action/model-db/blob/main/src/iai_model_zoo/formats/adapters/README.md).
Image dimensions and producer options must be supplied where the source omits
them. Unknown model identity, capture time and inference time remain unknown.

## A minimal single-image Ultralytics route

For a compatible **horizontal-detection** checkpoint, the supplied example calls
`YOLO.predict` directly and passes the one-image Results object to ISIR:

```bash
uv run --locked --project src/probe/environments/modern \
  python examples/formats/predict_ultralytics.py \
  --weights /path/to/author-detector.pt \
  --image /path/to/frame.jpg \
  --model-name "ArthroNat YOLO11n mosaic33" \
  --imgsz 640 --conf 0.25 --iou 0.7 > prediction.isir.json
```

Use a downloaded, compatible detector checkpoint from the model card. Paths and
model name above are caller-supplied; the command does not select or fetch a
model. It runs on CPU with two threads and records the explicitly selected
prediction settings. It rejects segmentation, oriented-box and classification
models, because their geometry requires different handling.

This helper was exercised with the pinned ArthroNat YOLO11n mosaic33 checkpoint
and existing specimen fixture, producing valid single-image ISIR. This checks
the interface on one image, not detection accuracy or every checkpoint variant.

This route is suited to ArthroNat's documented Ultralytics interface. It is not
a universal replacement for specialized author pipelines. The settings shown
are this example's settings, not a claim of equivalence to every author's
configuration. The locked environment also makes the first setup larger than
the small conversion-only example.

## Alternative routes worth pursuing

An alternative should have its own invocation and evidence. Keep the author
pipeline's advertised format; document the alternate format alongside it rather
than silently replacing the database entry.

| Model | Simpler route | What changes / current evidence |
| --- | --- | --- |
| ArthroNat | One `YOLO.predict` call → detection Results → ISIR | Uses the documented model API; runnable helper above. Existing checkpoint probe covers this interface. |
| BioMoth | Load the TorchScript checkpoint once; call the notebook's letterbox, parser, NMS and coordinate-restoration helpers on one image | Avoid notebook UI, folder loops and CSV append operations. The probe already executes these original functions with real weights, but a dedicated single-image wrapper has not been packaged. Keep the author parsing/NMS; directly treating the raw tensor as boxes would be wrong. |
| AMI | Extract the author's checkpoint construction and image transform; run one image and its original thresholding | Avoid database queues and persistence. The postprocessed integer boxes already have an ISIR importer. Source-inspected proposal only; preserve model-specific thresholds and integer truncation. Keeping raw scores instead would be a separate interface. |
| InsectDCT | A detector-only call can separate detection from hierarchical classification and tracking | The author uses motion-enhanced inputs. A raw RGB single-image call changes the input distribution and may change detection quality. It cannot reproduce the full pipeline's taxon labels or classifier scores. Needs a separate probe. |
| Mothbot | Direct OBB prediction plus the original JSON writer on one image | The existing probe exercises this route with real weights, excluding GUI, thumbnail writing and later identification. It yields oriented boxes, so the horizontal-detection helper deliberately rejects it. An OBB-to-ISIR convention remains to be implemented. |
| POLLINATOR | Call the pinned YOLOv5 detector on one image and retain its box results instead of drawing video frames | An alternate interface could expose machine-readable boxes that the author export discards. Preserve both model filtering and the script's additional confidence filter. No dedicated single-image alternate probe yet; modern Ultralytics is not a drop-in replacement for this legacy checkpoint. |

These proposals are grounded in the pinned source interfaces documented on the
[BioMoth](../detection/biomoth-csv/), [AMI](../detection/ami-detector-boxes/),
[InsectDCT](../detection/insectdct-csv/), [Mothbot](../detection/mothbot-detection-json/)
and [POLLINATOR](../detection/pollinator-frame-folders/) format pages. Each links
to its author source and states the limits of runtime evidence.

## What an alternative must preserve

Preserve preprocessing, coordinate restoration, thresholding/NMS, the checkpoint's
class vocabulary and image identity. Test a populated image and a known empty
image. If removing a stage changes these semantics, describe that difference;
an easier interface is not evidence of equivalent predictions.

Do not invent full-image boxes for Ecto-Trigger's presence score or recover
precise boxes from annotated JPEGs. Likewise, measurements without positions
cannot be converted into localized instances. Those outputs need a different
representation or access to an earlier inference stage.
