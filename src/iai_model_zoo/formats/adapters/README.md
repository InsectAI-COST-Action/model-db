# Flatbug and COCO adapters

These adapters consume and return decoded dictionaries. They use the schema
handler and standard library; no model runtime, NumPy or mask decoder is needed.
Use `PYTHONPATH=src` when running from this checkout.

Both adapters use [ISIR](../../../../static/formats/detection/isir.json): one
record per image, with `ir_name="ISIR"` and `ir_id=1`. Those fields identify the
compatibility contract, not an individual result. A different name/version
fails validation. The optional `category_id`, `polygons`, `area`, image
`file_name`, and per-instance `extra_information` fields preserve data needed
by these first adapters.

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
cannot be implicitly collapsed into one Flatbug contour. Nonzero box angles
are rejected by both adapters.

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
