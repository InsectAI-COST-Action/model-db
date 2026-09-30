# Actual prediction formats

These files describe outputs of specific APIs/exporters at the source revisions
linked in each definition. They are descriptive JSON, not JSON Schema and not
necessarily examples of JSON emitted by a model. `serialization` identifies the
actual representation. `T[name]` refers to a type; `? :` means an optional field
or column. A one-element array describes repeated items. Text `columns` and
option notes define the exact row order; they are not named fields on disk.

## Detection

| Producer | Text export | Python prediction output | JSON export |
| --- | --- | --- | --- |
| YOLOv5 reference repository | [yolov5-detect-txt](detection/yolov5-detect-txt.json) | [yolov5-detect-results](detection/yolov5-detect-results.json), AutoShape wrapper | No JSON contract assigned here |
| YOLOv7 reference repository | [yolov7-detect-txt](detection/yolov7-detect-txt.json) | CLI internals are not a returned result API | No JSON contract assigned here |
| YOLO11 and YOLO26, Ultralytics package | [ultralytics-detect-txt](detection/ultralytics-detect-txt.json) | [ultralytics-detect-results](detection/ultralytics-detect-results.json) | [ultralytics-detect-json](detection/ultralytics-detect-json.json) |

## Instance segmentation

| Producer | Text export | Python prediction output | JSON export |
| --- | --- | --- | --- |
| YOLOv5 reference repository | [yolov5-segment-txt](detection/yolov5-segment-txt.json), polygons | CLI computes masks locally; does not return a result object | No JSON contract assigned here |
| YOLOv7 reference repository, `u7/seg` | [yolov7-segment-txt](detection/yolov7-segment-txt.json), **boxes only** | CLI computes masks locally for rendering; does not return them | No JSON contract assigned here |
| YOLO11-seg and YOLO26-seg, Ultralytics package | [ultralytics-segment-txt](detection/ultralytics-segment-txt.json), polygons | [ultralytics-segment-results](detection/ultralytics-segment-results.json) | [ultralytics-segment-json](detection/ultralytics-segment-json.json) |

Segmentation files live under `detection/` because this registry groups instance
segmentation models into the detection category. These are postprocessed
prediction representations; raw network/exported-runtime tensors are separate
interfaces and are not described by these profiles.

## Interoperability

- Default detection text exports share `class center_x center_y width height`,
  with normalized coordinates. Confidence is optional. YOLOv5 `save_format=1`
  instead writes normalized corner coordinates. Tracking through Ultralytics
  appends a track ID, even when confidence is disabled. Column count alone
  cannot distinguish confidence from a tracking ID.
- YOLOv5 and modern Ultralytics segmentation text use flattened normalized
  polygons. Their contour extraction and degenerate-polygon handling differ.
  YOLOv7 segmentation text cannot substitute for this polygon format: it has
  only boxes.
- Ultralytics JSON uses per-instance objects with pixel box corners by default.
  Segmentation adds parallel `x` and `y` coordinate arrays. `normalize=True`
  changes coordinate units without changing the JSON keys.
- Matching layouts do not establish matching label vocabularies, coordinate
  settings, or image associations. Text exports omit the class-name table and
  image dimensions. Preserve these externally.
- A segmentation polygon export does not preserve the full binary mask.
  `Results.masks.data` may use a different grid from the original image;
  `retina_masks` changes its dimensions.

The shared `ultralytics-*` definitions identify the producing package/API,
not a model generation. They apply to YOLO11 and YOLO26 through that API at
the pinned revision. Wrappers such as Flatbug can emit a different format even
when they use those architectures.

## Assigning formats to model cards

Use a profile only after checking the model's actual inference entry point and
settings. `output_format` currently holds one profile per architecture, in the
same order. Document alternate export choices in the model-card prose. Do not
infer a profile from an architecture name or replace a wrapper's custom format.
Existing model cards are consequently not assigned new formats automatically.

The definitions record source inspection, not an end-to-end inference benchmark.
Updating the source revision requires rechecking the relevant serializer code.
