# Actual prediction formats

These files describe outputs of specific APIs/exporters at the source revisions
linked in each definition. They use the notation below, not JSON Schema.
`notes.serialization` identifies the actual representation; a descriptor is not
necessarily an example of JSON emitted by a model.

## Schema notation

Every descriptor has exactly four sections (use `{}` for an unused section):

- `types`: named custom types, defined using the same syntax as `structure`.
- `enums`: named lists of allowed JSON values, e.g. `"image_formats": ["png", "jpg"]`.
- `structure`: the actual data layout, containing only field names and type
  expressions, objects, or arrays. No examples, descriptions, or metadata.
- `notes`: all explanations, producer settings, sources, serialization details,
  units, numeric constraints, column order, examples, and limitations.

Type names and enum names are case-sensitive identifiers: letters, digits and
underscores, starting with a letter or underscore. Built-in type names are
reserved and cannot be redefined in `types`.

| Syntax | Meaning |
| --- | --- |
| `T[string]`, `T[number]`, `T[boolean]`, `T[null]`, `T[object]`, `T[array]` | JSON base types. `object` and `array` leave their contents unspecified. |
| `T[integer]` | Expected integer cast target (e.g. IDs and counts); conversion must not truncate a fractional value. |
| `T[float]` | Expected floating-point cast target, including whole-valued numbers; precision is specified in notes when known. |
| `T[ISO]` | String in the registry's strict UTC form `YYYY-MM-DDTHH:mm:ss.sssZ`. |
| `T[UUIDv4]` | UUID version 4 string in hyphenated 8-4-4-4-12 form. |
| `T[box]` | Custom type defined by `types.box`. Forward references are allowed. |
| `T[string](E[image_formats])` | String constrained to options in `enums.image_formats`. Enum values must agree with the applied type. |
| `T[integer](0 \| 1)` | Inline allowed values, expressed as JSON literals. |
| `T[integer](0) \| T[string]("unknown")` | Union with a separate constraint on each branch. |
| `"field": "? : T[string]"` | Field may be absent. The marker belongs in the value, not the field name. |
| `T[string] \| T[null]` | Union: either type is allowed. Null is a value, distinct from an absent field. |
| `["T[name]"]` | Repeated-item array constructor: zero or more items of the type defined in `types.name`. `name` is a placeholder, not a built-in. |
| `["T[number]", "T[number]"]` | Fixed positional tuple of two numbers. |
| `"? : [T[string]]"` | Optional array field; string-form `[expression]` is the repeated-item shorthand, useful within optional fields and unions. |

### Constructing types

`point`, `box`, `row`, and `contour` are **not built-in types**. A descriptor
must define each name it uses under `types` or obtain it from the shared type
library described below. `point` is not in that library: `T[point]` refers to
that descriptor's `types.point`. Domain-specific names have no inferred meaning. For example,
a 2D coordinate tuple and an object with `x`/`y` fields are different structures,
even if two descriptors both call them `point`.

Higher-order types are composed recursively from the built-in types using the
following constructors. They introduce no additional domain-specific primitives:

| Constructor | Definition |
| --- | --- |
| Reference `T[name]` | Resolve a built-in type or substitute the schema at `types.name`. |
| Union `A \| B` | A value may satisfy either expression; constraints belong to their respective branches. |
| Repetition `[A]` | An array with length ≥ 0 whose every item has type `A`. |
| Positional tuple `[A, B, ...]` | An array with one position per listed schema, in order. It has a fixed length unless a trailing position is optional. |
| Field object `{"field": A, ...}` | An object whose listed fields have their respective schemas. `? :` makes a field optional. |
| Restriction `T[name](...)` | The referenced type restricted to enum or literal values, interpreted under its safe cast. |

Here `A` and `B` are explanatory metavariables for schema expressions, not
literal type names. The descriptor is JSON, so an expression used as a JSON
value must be quoted. Thus the repetition constructor can be written as the
JSON schema node `["T[float]"]` or the expression string `"[T[float]]"`.
Both describe zero or more float-castable values; neither is example data.
A tuple is written as a JSON array of two or more schema nodes, such as
`["T[float]", "T[float]"]`. Comma-separated tuples inside expression strings
are not part of the language.

Array length determines the constructor **in the schema**, not the number of
items in the output: one schema entry means repetition; two or more mean a
positional tuple. This shorthand does not express an exactly-one-element tuple.
An empty schema array is invalid; `T[array]` means an array with unspecified
contents. Fixed size, minimum size, or equal-length relationships that cannot
be expressed by these constructors remain in `notes`.

For example, these definitions compose without introducing a built-in `point`:

```json
{
    "types": {
        "point": ["T[float]", "T[float]"],
        "polyline": ["T[point]"],
        "polylines": ["T[polyline]"],
        "feature": {
            "outline": "T[polyline]",
            "label": "? : T[string]"
        }
    },
    "enums": {},
    "structure": ["T[feature]"],
    "notes": {
        "point": "A point is [x, y] in original-image pixels."
    }
}
```

Expanding `T[polyline]` substitutes `["T[point]"]`, then
`[["T[float]", "T[float]"]]`: a repeated array of fixed two-position arrays.
`T[polylines]` adds one more repetition layer. In contrast,
`[["T[float]"], ["T[float]"]]` is a fixed pair of variable-length arrays,
which is the layout of Flatbug's parallel x/y coordinates. Equal inner lengths
are a separate constraint documented in its notes.

### Grammar

There are two layers: the JSON schema nodes and the expressions inside JSON
strings. `json-string`, `json-literal`, and JSON objects/arrays use JSON syntax;
`identifier` is `[A-Za-z_][A-Za-z_0-9]*`. In the EBNF below, `*` means zero or more,
`+` means one or more, and `?` means optional; these are grammar notation, not
additional schema operators.

```ebnf
schema-node   = expression-string | field-object | repetition-node | tuple-node ;
field-object  = "{" (json-string ":" field-node
                    ("," json-string ":" field-node)*)? "}" ;
field-node    = schema-node | optional-expression-string ;
repetition-node = "[" schema-node "]" ;
tuple-node    = "[" tuple-item ("," tuple-item)+ "]" ;
tuple-item    = schema-node | optional-expression-string ;

expression-string          = JSON-quote(expression) ;
optional-expression-string = JSON-quote("? : " expression) ;
expression    = term ("|" term)* ;
term          = reference constraint? | "[" expression "]" ;
reference     = "T[" identifier "]" ;
constraint    = "(" (enum-reference | json-literal ("|" json-literal)*) ")" ;
enum-reference = "E[" identifier "]" ;
```

`JSON-quote` means encode the expression as a JSON string, escaping embedded
quotes and backslashes. Whitespace is allowed between expression tokens;
references keep their exact `T[name]`/`E[name]` spelling and the optional prefix
is `? : `. Each definition in `types` and the root `structure` value is a
`schema-node`. `enums`
contains JSON value arrays, so the schema-array constructor rules do not apply
there or inside literal constraints. All referenced custom names must be
defined locally or supplied by the shared library. Optional tuple entries must
form a suffix. Definitions must expand finitely: cyclic references are rejected.

The grammar describes structural syntax; safe casting, constraint compatibility,
and producer-specific conditions are the additional semantic rules below.
An object schema describes the listed fields, not an assertion that the runtime
object has no other attributes. This matters for the partial Python API profiles.

### Cast semantics

A declared type is the **expected, safe cast target**, not a requirement that
the raw value already has that runtime type. For example, `T[integer]` may
receive `3`, `3.0`, or `"3"`: consumers are expected to obtain the integer `3`.
A class ID carried in a floating tensor is therefore described as `integer`.
`T[float]` may receive `3`, `3.0`, or `"3.0"`. This rule applies recursively to
fields, array items and custom types. It does not change the producer's output.
The intended target is determined by the field's meaning, not by every cast a
language happens to permit.

`integer` and `float` refine JSON's `number`. Retain `number` when either numeric
target is appropriate or a repeated array mixes integers and floats. `int`,
`str`, `obj`, and `datetime` are not built-ins. Runtime dtypes, bit widths,
serialization, decoding conventions, bounds and precision belong in `notes`.
CSV and text floats may omit a decimal point, for example under `%g` formatting.

A safe cast preserves meaning: no fractional truncation, overflow, silent loss
of an integer ID, or arbitrary truthiness. Normal floating-point rounding of
fractional measurements is expected at the precision specified by the producer.
Missing values and null remain distinct; neither is implicitly converted to
zero or an empty string. Optionality and nullability must still be declared.

The syntax checker's enum compatibility rules implement conservative casts:

- Numeric types accept finite numbers and decimal numeric strings (including
  exponents). `integer` requires an integral value. `float` checks binary64 for
  overflow, underflow to zero, and loss of integral values; `number` leaves the
  numeric target unspecified. Booleans are not treated as numeric values.
- `string` accepts strings and finite numeric/boolean scalars; containers and
  null are not implicitly stringified.
- `boolean` accepts booleans, numeric 0/1, and case-insensitive text
  `true`/`false` or `0`/`1`; it does not use Python's string truthiness.
- `object` and `array` enum options retain their JSON shapes. Native containers
  such as tensors/tuples require the decoding interpretation recorded in notes.
- `null`, `ISO`, and `UUIDv4` retain their value/format restrictions. These are
  not a license to reinterpret arbitrary strings or timestamps.

Enum options describe allowed values under the declared cast. The compiler
checks them against resolved types, including aliases and composite types.
The CLI validates descriptors; the Python module can also cast decoded data.
Producer-specific decoding and precision rules still require explicit adapters.

The `ISO` type deliberately selects a narrower form than the full
[ISO 8601 standard](https://www.iso.org/iso-8601-date-and-time-format.html).
`UUIDv4` refers to [RFC 9562, section 5.4](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.4).
A producer's local timestamps or differently formatted dates remain `T[string]`;
they are not relabelled as `ISO` for consistency.

Within a type-expression string, unions join references or repeated-item arrays:
`T[RLE] | [T[polygon]]`. The optional prefix applies to the whole expression.
Named enum options are defined in `enums`; inline options occur inside a
postfix constraint. Write `T[null]` or `T[null](null)`, not bare `null`, as a
structural type expression. Complex object and tuple alternatives can be
named in `types` and joined by reference. Empty schema arrays are disallowed;
use `T[array]` for an unspecified array. Optional tuple positions must form a
suffix. Omitted optional positions are removed, not replaced by null; producer
settings in `notes` determine which positions occur.

Constraints follow the completed type reference: `T[type](...)`. There is no
literal backslash before `(`. The old `T[type(E[name])]` syntax is no longer
accepted. A constraint contains either one enum reference, `E[name]`, or one or
more JSON literals separated by `|`. Quote string literals: `T[string]("x" | "y")`.
JSON escaping still applies inside the surrounding descriptor string, for
example `"status": "T[string](\"ready\" | \"done\")"`.

Parentheses bind to the immediately preceding type. Thus
`T[integer](0 | 1) | T[string]("unknown")` permits integer 0/1 or string "unknown".
Pipes inside quoted strings or JSON containers are literal content, not union
separators. Constraints also work inside repeated arrays and optional fields,
e.g. `? : [T[integer](0 | 1)]`. Empty constraints, mixed enum/literal lists and
stacked constraints are rejected; define one enum or one literal list instead.
Constraint options must support the declared safe cast. Allowed values are
interpreted under that cast; the syntax checker does not validate model output.

For example:

```json
{
    "types": {
        "point": ["T[number]", "T[number]"]
    },
    "enums": {
        "image_formats": ["png", "jpg"]
    },
    "structure": {
        "points": ["T[point]"],
        "format": "? : T[string](E[image_formats])",
        "timestamp": "? : T[ISO]",
        "identifier": "? : T[UUIDv4] | T[null]"
    },
    "notes": {
        "points": "Each point is [x, y] in original-image pixels."
    }
}
```

### Shared types and Python handler

The [Python module](../../src/iai_model_zoo/formats/README.md) compiles this
language to a type IR and casts decoded values against it. The CLI uses the same
compiler; there is no separate parser to keep in sync.

[shared_types.json](../../src/iai_model_zoo/formats/shared_types.json) contains
ordinary schema-language definitions, currently `float_pair`, `float_quad`,
`float_vector`, and `float_matrix`. Loading a schema implicitly merges this
library into its `types`: **local definitions win**. Built-in names remain
reserved. The input descriptor and library are not mutated. Pass
`shared_types={}` to disable injection, or supply a replacement mapping.

For example, Flatbug's local `box` and ISIR's local `bbox` now each reference
`T[float_quad]`. That shared type asserts only a four-float tuple. Their different
coordinate conventions remain in their own notes and conversion adapters.

### Non-JSON outputs

The notation also describes the shape of non-JSON data, without claiming that
those producers emit JSON. `notes` must state the interpretation:

- Text rows use positional arrays. `notes.columns` gives column meanings and
  option-dependent suffixes. Variable-length numeric polygon rows remain arrays
  of numbers; their token order and coordinate pairing are specified in notes.
- CSV tables with headers use arrays of objects keyed by the actual header
  names. These describe rows after reading the header and decoding numeric
  cells; column order and raw example cells remain in notes. Multiple output
  tables use named type alternatives, with filenames recorded in notes.
- Python result objects use actual attribute names; nested arrays describe
  tensor/ndarray dimensions. Runtime classes, storage dtypes, shapes and index mappings
  are documented in notes. Python `None` is represented by `T[null]`.
- Output directories use their actual names. Variable filename maps use
  `T[object]`; filename patterns and file contents are described in notes.

The language intentionally does not encode every runtime constraint. Structural
similarity alone does not prove interoperability; serialization, units, class
vocabulary and producer options still matter.

### Validation

Run from the repository root (Python 3.10+, standard library only):

```sh
python3 scripts/check_formats.py
python3 -m unittest discover -s scripts/tests -v
```

The checker accepts individual files or directories as arguments. It checks all
four sections, structural syntax, type/enum references, optional positions,
resolved constraint compatibility, duplicate JSON keys and reserved type names. It
validates descriptor syntax, not prediction data or the truth of producer notes.
CI runs these checks before building the site. The probe's inference environments
remain independent of the notation checker.

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

## Conversion adapters

[ISIR adapters](../../src/iai_model_zoo/formats/adapters/README.md) support
Flatbug/COCO import and export, plus import-only YOLO detection TXT, Ultralytics
detection Results/JSON, BioMoth CSV and AMI box lists. Each ISIR record describes
one image; multi-image sources return collections of these records. Image context,
model identity and inference settings are supplied explicitly when absent from
the source. Tests include retained real probe outputs and metadata preservation.

## Tested author workflows

The [probe project](../../src/probe/README.md) tests the specialized models'
actual author entry points with real weights. Custom observed representations:

- [POLLINATOR frame folders](detection/pollinator-frame-folders.json): saved JPEG frames, no machine-readable boxes.
- [insectsFlowers CSV](detection/insectsflowers-csv.json): headerless pixel boxes, percentage confidence, one-based classes; historical pairing with the 2023 model is unconfirmed.
- [BeetleFlow color masks](detection/beetleflow-color-mask.json): palette images and overlays for the tested 5-class model.
- [InsectMorphoAI CSV](detection/insectmorphoai-csv.json): derived morphometric measurements from both analyses.
- [InsectDCT CSV](detection/insectdct-csv.json): final and hierarchical classification tables from the complete author pipeline.

See the [dated evidence](../../src/probe/reports/2026-09-30/README.md) for checkpoint
scope, settings and cases that could not be completed.

## Additional author-specific detection outputs

The [coverage audit](../../src/probe/reports/2026-09-30-format-expansion/README.md)
records the evidence level for every detection card, including version and stage
limits. The new profiles are:

| Profile | Author interface | Evidence |
| --- | --- | --- |
| [BioMoth CSV](detection/biomoth-csv.json) | Notebook batch measurements | Real checkpoint and original notebook functions |
| [Mothbot JSON](detection/mothbot-detection-json.json) | Detection-stage oriented boxes | Real checkpoint and original JSON writer; later stages excluded |
| [AMI boxes](detection/ami-detector-boxes.json) | Thresholded integer box list, no scores | Source inspection |
| [Insect Detect CSV](detection/insect-detect-csv.json) | Camera-trap tracking metadata | Source inspection; hardware probe blocked |
| [MCC24 CSV](detection/mcc24-csv.json) | Combined detector/order/species pipeline | Source inspection; full run failed on label-map download |
| [Grounding DINO HF results](detection/grounding-dino-hf-results.json) | Transformers 4.40.2 grounded postprocessor | Source inspection; version-specific Python tensors/phrases |
| [Ecto-Trigger TFLite score](detection/ecto-trigger-tflite-score.json) | Quantized image-level trigger | Source inspection; no instance boxes |

These profiles preserve emitted units, score meanings, field names and quirks.
An `output_format` link documents an interface; the descriptor's `notes.evidence`
and card prose identify whether it was observed or only source-inspected.


## Human-readable examples

The site’s **Formats** navigation and model-table format links lead to
[example pages](../../content/formats/_index.md), with raw schemas linked alongside.
[Runnable examples](../../examples/formats/README.md) demonstrate conversion to
single-image ISIR and a minimal Ultralytics prediction route. Alternate author
pipeline routes are described separately, with their evidence and limitations.
