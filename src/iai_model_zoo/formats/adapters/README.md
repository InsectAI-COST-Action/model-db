# ISIR adapters

These adapters use the schema handler and standard library. Flatbug and COCO
support import and export; the detection adapters below are import-only. No model
runtime, NumPy or mask decoder is imported. Native Ultralytics Results can be
consumed when the caller already uses that runtime.
Use `PYTHONPATH=src` when running from this checkout.

All adapters use [ISIR](../../../../static/formats/detection/isir.json): one
record per image, with `ir_name="ISIR"` and `ir_id=1`. Those fields identify the
compatibility contract, not an individual result. A different name/version
fails validation. The optional `category_id`, `polygons`, `area`, image
`file_name`, and per-instance `extra_information` fields preserve data needed
by these first adapters.

## Import-only detection adapters

One ISIR record always describes **one image**. Single-image adapter calls return
one dictionary; multi-image calls return a list of those dictionaries. Existing
COCO `Batch.images` follows the same rule, retaining dataset metadata separately.
No adapter combines detections from different images into one ISIR record.

| Module / entry point | Input | Return |
| --- | --- | --- |
| `ami.to_ir` | Postprocessed integer pixel boxes for one image | One ISIR record |
| `ami.to_ir_many` | Mapping from image keys to box lists | List of ISIR records |
| `yolo_txt.to_ir` | One image's TXT string or decoded numeric rows | One ISIR record |
| `yolo_txt.to_ir_many` | Mapping from image keys to TXT strings/rows | List of ISIR records |
| `ultralytics.to_ir` | One native horizontal-detection Results object or decoded projection | One ISIR record |
| `ultralytics.to_ir_many` | Results list/generator, optionally matched image contexts | List of ISIR records |
| `ultralytics.json_to_ir` | One image's Results JSON string or decoded instance list | One ISIR record |
| `ultralytics.json_to_ir_many` | Mapping from image keys to per-image JSON | List of ISIR records |
| `biomoth.to_ir` | Multi-image author CSV string or decoded row dictionaries | List of ISIR records |

These modules have no `from_ir`: constructing author runtime objects or reverse
measurement pipelines is outside their purpose. They do not read paths or scan
directories. Read files explicitly before calling them.

### Image context and collections

```python
from iai_model_zoo.formats.adapters import ImageContext, Metadata, ami

image = ImageContext(
    id="capture-123", width=200, height=100, file_name="site/frame.jpg",
    metadata=Metadata(model={"name": "known detector"}),
)
ir = ami.to_ir([[10, 20, 50, 60]], image=image)
assert ir["instances"][0]["bbox"] == [30, 60, 40, 40]
```

`ImageContext` supplies known image identity and dimensions, an optional filename,
and optional per-image `Metadata`. Positive integer dimensions are required.
Image dimensions never come from the maximum detection coordinates. Metadata is
copied and validated using the same rules as Flatbug/COCO. Missing scores/classes
remain absent; AMI supplies neither. Instance IDs are row positions within each
image, not track IDs.

Collection manifests map exact source keys to contexts. Source keys and ISIR IDs
can differ. Duplicate ISIR image IDs and input keys absent from the manifest
raise `FormatError`. Manifest-based collections use manifest order; Ultralytics
Results collections use source order. Context-specific metadata is applied to
each corresponding image.

```python
images = {
    "site/frame.jpg": image,
    "site/blank.jpg": ImageContext("capture-124", 200, 100),
}
batch = ami.to_ir_many({"site/frame.jpg": [], "site/blank.jpg": []}, images=images)
assert len(batch) == 2  # Two known empty images, each its own ISIR record.
```

By default, manifest entries absent from the supplied outputs are omitted.
`include_empty=True` explicitly asserts that those images were processed and
had no detections. Use it only with a known completed-image manifest. A missing
TXT file or CSV row cannot establish successful empty inference by itself.
Explicit empty lists/text are retained without this option.

### YOLO detection TXT

```python
from iai_model_zoo.formats.adapters import yolo_txt

ir = yolo_txt.to_ir(
    "0 0.25 0.30 0.20 0.40 0.8\n",
    image=image, profile="yolov5-detect-txt", save_conf=True,
)
```

Supported profiles are `yolov5-detect-txt`, `yolov7-detect-txt`,
`ultralytics-detect-txt`, and `yolov7-segment-txt` (the last contains boxes only).
`save_conf` is required. `tracking=True` is supported only for Ultralytics and
selects a final tracking-ID column, preserved under per-instance
`extra_information[profile].track_id`. Neither column count nor an integer-valued
sixth token determines whether that token is confidence or a track ID.

The default layout contains normalized center/width/height. YOLOv5's
`save_format=1` selects normalized corner coordinates. Both convert to pixel
center/width/height with bottom-left origin, without clipping or rounding.
The selected profile/options are retained as record-level native metadata.
Input row lengths must exactly match the selected layout; no suffix is guessed.
This importer does not support polygon TXT or raw network tensors.

### Ultralytics Results and JSON

```python
from iai_model_zoo.formats.adapters import ultralytics

# results = model.predict(...) from an existing Ultralytics installation
# batch = ultralytics.to_ir_many(results)

ir = ultralytics.json_to_ir(
    [{"name": "insect", "class": 0, "confidence": 0.8,
      "box": {"x1": 10, "y1": 20, "x2": 50, "y2": 60}}],
    image=image, normalized=False,
)
```

Results supply `orig_shape`, `path`, `names`, and `boxes.data`. Native tensors
are detached and moved to CPU before conversion to lists; the adapter itself
imports no tensor library. Decoded projections use the same documented fields.
Without context, `path` identifies the image. Supplied contexts can override
identity, attach metadata and choose filenames, but dimensions must agree with
`orig_shape`. Native source paths and class vocabularies are retained in
`extra_information.ultralytics`; context overrides do not erase them.

For batches, `images=[context, ...]` must match Results one-for-one. Repeated
video paths need explicit distinct frame IDs. Both tracked seven-column and
untracked six-column box tensors are supported, including empty tensors.
Track IDs remain native metadata rather than replacing per-image instance IDs.
The projection covers documented detection fields, not every Results attribute.

JSON requires `ImageContext` and an explicit `normalized` boolean matching the
producer's `normalize` option. Names, tracking IDs and extra instance fields are
retained. Empty JSON `[]` means one empty image. JSON rounding has already lost
precision; conversion cannot recover it. Segmentation, OBB, pose and
classification Results are rejected by this detection-only adapter.

### BioMoth CSV

```python
from pathlib import Path
from iai_model_zoo.formats.adapters import biomoth

# Keys must match the CSV filePath exactly, not just fileName.
images = {"WS1/frame.jpg": ImageContext("capture-123", 6040, 3420)}
# batch = biomoth.to_ir(Path("predictions_2023.csv").read_text(), images=images)
```

Rows are grouped by exact `filePath`, so identical basenames at different sites
remain separate. Each image needs manifest dimensions. The CSV header and row
lengths are validated; decoded mappings pass through the author schema. The
source path populates `image.file_name` unless the caller supplies a filename.

Boxes, class IDs and detector confidence map to their ISIR counterparts. Each
source row is retained under instance `extra_information.biomoth`, including
native extensions, calibration-dependent measurements, site and hard-coded year.
`size` is in square centimetres and is **not** mapped to ISIR's pixel-square
`area`. No calibration, capture timestamp or model identity is inferred from it.
As with TXT, a CSV without a row for an image does not establish empty inference;
use `include_empty=True` only with an explicitly completed-image manifest.

## Flatbug

```python
from iai_model_zoo.formats.adapters import Metadata, flatbug

# prediction is the decoded Flatbug JSON dictionary.
metadata = Metadata(
    model={"name": "Flatbug M_v2"},
    inference={
        "timestamp": "2026-09-30T12:00:00.000Z",  # known prediction time
        "config": {"confidence_threshold": 0.25},
    },
    context={"group_name": "trap-17"},
)
ir = flatbug.to_ir(prediction, image_id="capture-123", metadata=metadata)
restored = flatbug.from_ir(ir)
```

When `image_id` is omitted, the source image path identifies the image. Flatbug's
`identifier` can be null, a string, or a list of run identifiers; it is retained
as native metadata, not used as image identity. Instance IDs are the zero-based
source positions. Reordering instances does not change these IR IDs, although
Flatbug has no output field that can preserve them.

Flatbug boxes use original-image top-left-origin `[x1,y1,x2,y2]`. Contours are
parallel x/y arrays. ISIR boxes use bottom-left-origin center/width/height, and
polygons use lists of `[x,y]` points. Conversion uses continuous image-edge
coordinates, `y_ir = image_height - y_source`, not `height - 1 - y`. No clipping
or integer rounding is applied. Float round-off is possible after edits.

Scale values and native top-level fields (mask dimensions, run identifiers,
unknown extensions) are preserved under `extra_information.flatbug`. Source
arrays must have equal instance counts, and each contour's x/y lengths must
match. Areas use the original values; they are not replaced by bbox area or
recomputed from simplified contours. When mask and image dimensions differ,
Flatbug's mask-grid area is retained as `extra_information.flatbug.mask_area`
on each instance instead of incorrectly labelling it as ISIR image-grid area.
Contours from the author serializer are already in image coordinates.

Export requires one contour per instance, a category ID, area, and confidence.
No masks, confidence scores, or scales are synthesized. For records imported
from another format, an explicit fallback is available for scale/confidence:

```python
restored = flatbug.from_ir(ir, scale=1.0, confidence=0.5)
```

Fallbacks fill only missing values. These numbers must be a deliberate caller
choice, not a claim about the source inference. Missing contours/areas require
an explicit derivation before export. Multipart polygons and opaque COCO RLE
cannot be implicitly collapsed into one Flatbug contour. Nonzero box angles are exported as axis-aligned envelopes by both adapters.

## COCO

```python
from iai_model_zoo.formats.adapters import Metadata, coco

# dataset is COCO dataset JSON with images, annotations and categories.
batch = coco.to_ir(dataset, metadata=Metadata(model={"name": "known-model"}))
ir_images = batch.images
restored = coco.from_ir(batch)
```

`coco.Batch` holds per-image ISIR records in `images` and dataset-level fields
in `metadata`. Categories, licenses, info and unknown dataset fields are kept
once, rather than repeated per image. Empty images are retained. The adapter
checks unique IDs and image/category references. Export groups annotations by
image; their IDs and meaning are retained, but source annotation ordering is
not a contract.

The adapter supports dataset JSON, not a prediction-only COCO result list.
Image dimensions and category vocabularies must come from an actual dataset or
explicit caller context. Every annotation currently needs a bbox; deriving one
from segmentation-only annotations is a separate operation. Optional COCO info,
licenses and image metadata may be absent. Observed Flatbug-exporter placeholders
such as `info.year=""` and `date_captured=0` remain placeholders.

COCO boxes use top-left-origin `[x,y,width,height]`. Polygon lists are transformed
into ISIR polygons without dropping disconnected components. RLE is retained
unchanged under the instance's `extra_information.coco.fields.segmentation`.
Its grid size must match the image on import/export; the adapter does not decode
or validate the compressed run stream. `iscrowd` and other annotation extensions
remain in the same namespace. Changing an IR box does not alter its segmentation
or recompute area; callers must update dependent geometry deliberately.

The `score` and author-exported `conf` fields map to ISIR confidence. Export
restores the original field name(s); newly supplied confidence uses `score`.
Conflicting `score` and `conf` values are rejected. Ground-truth annotations
without either remain without confidence.

To construct COCO from Flatbug IR, supply the destination category vocabulary
and any required integer IDs explicitly:

```python
from iai_model_zoo.formats.adapters import coco, flatbug

ir = flatbug.to_ir(prediction)
batch = coco.Batch(
    images=[ir],
    metadata={"categories": [{"id": 1, "name": "insect"}]},
)
dataset = coco.from_ir(batch, image_ids={ir["image"]["id"]: 1})
```

Optional `annotation_ids` maps `(IR image ID, IR instance ID)` pairs to globally
unique COCO integer IDs. This is necessary if several imported images reuse
instance IDs. Category IDs are not renumbered or assigned guessed class names;
edit the IR category IDs explicitly when changing vocabularies.

### Class-agnostic COCO export

Missing `category_id` values default to a generic `object` category on export.
An existing category named `object` is reused; otherwise an unused positive ID
is chosen. The category is added only when needed. This is serialization metadata,
not a classification prediction or a change to the ISIR input.

`coco.from_ir(batch, fallback_category={"id": 9, "name": "object"})` customizes
the category; `fallback_category=None` disables the default. The same option is
available through `Converter.convert(..., export_options={...})`. Existing IDs
and scores remain untouched; unknown existing IDs still fail validation.
Conflicting explicit category definitions are rejected.

## Populating metadata

`Metadata(model=..., inference=..., context=...)` makes the source of extra
information explicit. Unknown sections are omitted, inputs are copied, and all
supplied fields are validated against ISIR. Nothing reads the current clock,
generates UUIDs, infers a model from a filename, or interprets COCO contributor
metadata as model identity.

A practical division of responsibilities is:

| IR fields | Appropriate source |
| --- | --- |
| `model.name`, `model.uuid` | Selected model registry entry and stable model identity, with explicit caller overrides. A new random UUID per conversion would identify the wrong thing. |
| `inference.timestamp`, `inference.config` | The prediction runner's recorded execution time and effective settings. Conversion time is not inference time. |
| `context.timestamp`, coordinates, CRS, tags/groups | Image capture metadata, manifest or user input. Capture time is distinct from inference time; timestamps need a known timezone. |
| Image ID, dimensions and path | Native output when available; an explicit manifest ID can override Flatbug's path-based default. |
| IR name/version | Adapter compatibility contract, currently `ISIR` / `1`. |

Resolve metadata before calling the adapter. For example, combine registry model
fields with caller overrides using `{**registry_model, **overrides}` and supply
that dictionary to `Metadata(model=...)`. This keeps precedence visible instead
of hiding it in the converter. When provenance matters, record source references
in an explicitly named entry under `extra_information`; automatic registry or
EXIF lookup is not part of these adapters yet.

COCO supports image-specific metadata via a callback:

```python
batch = coco.to_ir(
    dataset,
    metadata=lambda image: Metadata(
        model=registry_model,
        context=capture_context_by_id.get(image["id"]),
    ),
)
```

The callback receives a copy of the COCO image entry. Missing capture context
stays absent; naive or placeholder source date strings are not promoted to ISO
timestamps.

Keep enriched ISIR records as metadata sidecars when exporting native formats.
Neither native format has standard fields for all ISIR model/inference/context
metadata. Export emits native fields and preserves same-format native extras;
it does not insert an undocumented IR envelope. Cross-format export therefore
does not carry every source-specific extension (e.g. Flatbug scales into COCO).
The retained IR remains the complete record.

## Validation

The tests cover geometry, explicit metadata, missing fields, version rejection,
empty images, RLE/multipart preservation, ID collisions and cross-format export.
All six retained Flatbug/COCO probe JSON files are also round-tripped; numeric
casts may change JSON number spelling, so this is value-level preservation,
not byte-for-byte serialization equality.

```sh
python3 -m unittest discover -s scripts/tests -v
```


Import-only tests additionally cover real BioMoth CSV, retained YOLO TXT and
ArthroNat tensor observations, image grouping, empty manifests, ambiguous TXT
columns and native metadata retention. A controlled compatibility check with
pinned Ultralytics 8.4.90 exercises actual Results objects and JSON export for
tracked, untracked and empty inputs in both coordinate modes; this is not a new
checkpoint inference run.

## Grounding DINO and MCC24 imports

The pinned HF grounded postprocessor returns a list of image results. Use
`source="grounding-dino-hf-results"`, `cardinality="collection"`, ordered
`ConversionContext(images=[...])`, and `import_options={"normalized": False}`
for pixel coordinates (or `True` for normalized coordinates). Boxes, scores and
phrases must have equal lengths. Phrases are retained as metadata; COCO export
uses the generic object category. Custom Grounding DINO postprocessors require
separate matching contracts.

Use `source="mcc24-csv"`, `cardinality="collection"` and an image manifest keyed
by exact CSV `fileName` values for MCC24. Detection percentage confidence is
converted to 0–1. Detector/classifier IDs and order/species scores stay in native
metadata. Malformed CSV, invalid boxes and duplicate detection keys are rejected.
`include_empty=True` is available only when the caller knows missing rows mean a
completed image with no detections.

Both additions are tested with source-contract fixtures, not new inference runs.
See the [native/alternative coverage review](../../../../content/formats/coverage.md).

## Mothbot native JSON and direct OBB Results

Use `model="mothbot"` (or `source="mothbot-detection-json"`) for the author
JSON writer's detection-stage output. For direct Ultralytics OBB prediction,
use `source="ultralytics-obb-results"` instead. Both support one image or a
collection; optional image contexts supply explicit IDs. Collection contexts
may be ordered or keyed by exact source path.

Both importers preserve an oriented ISIR `bbox` and `angle` plus its polygon.
Angles are radians counterclockwise in ISIR's bottom-left coordinates. Native
angle fields and labels/classes remain namespaced metadata. No classification
is required. COCO writes the rotated box's axis-aligned envelope and the original
polygon as segmentation; returning from COCO retains polygon geometry but does
not automatically reconstruct the original rotated box parameters.

An ISIR box with an angle but no polygon can also export to COCO: its corners
are computed from the oriented box. Native polygon areas are not invented.
Existing supplied contours remain authoritative for segmentation.

See [the real-checkpoint evidence](../../../probe/reports/2026-09-30-mothbot-conversion/README.md).
