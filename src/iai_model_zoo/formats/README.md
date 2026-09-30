# Schema handler

`schema.py` interprets the [format language](../../../static/formats/README.md).
It uses Python 3.10+ and the standard library. From a checkout, use
`PYTHONPATH=src python3 ...`; it does not depend on the probe environments.

The public entry points are `Schema.from_dict(document)`, `Schema.load(path)`,
`schema.cast(value)`, and `convert(value, source, target, transform)`.

## Type IR and data IR

Compilation resolves named references to a small graph of dataclass nodes:
`Primitive`, `Array`, `Tuple`, `Object`, `Union`, `Optional`, and `Constrained`.
Inspect `schema.structure` or `schema.types[name]` to work with types directly.
Aliases reuse resolved nodes; reference cycles and undefined names are errors.
Enum and literal constraints are cast once during compilation, including
constraints on custom/composite types. The CLI delegates to this compiler.

Casting produces ordinary Python dictionaries, lists, and scalars. A common
**data IR** is another schema defined in the same language. Conversion adapters
map source values into that schema and from there into a destination schema:

```text
source data -> source.cast -> to_ir -> ir.cast
                                         |
                 target.cast <- from_ir <-+
```

These are distinct jobs: the type graph describes structure; the common data
schema expresses the application's chosen meaning. This module does not select
one universal insect prediction schema or infer semantic equivalence from field
names, tuple lengths, or free-text notes.

For example, two small row/object formats can share an intermediate schema:

```python
from iai_model_zoo.formats import Schema, convert


def define(structure):
    return Schema.from_dict({
        "types": {}, "enums": {}, "structure": structure, "notes": {}
    })


source = define(["T[integer]", "T[float]"])
ir = define({"id": "T[integer]", "score": "T[float]"})
target = define({"identifier": "T[integer]", "confidence": "T[float]"})

record = convert(["7", "0.9"], source, ir,
                 lambda row: {"id": row[0], "score": row[1]})
result = convert(record, ir, target,
                 lambda row: {"identifier": row["id"], "confidence": row["score"]})
assert result == {"identifier": 7, "confidence": 0.9}
```

`convert` casts the source, calls the supplied transform, and casts the target.
Adapters are plain functions; there is no registry, plugin system, or implicit
field matching. Exceptions from an adapter propagate to the caller.
Decoding CSV/JPEG/tensors and encoding the destination are separate adapter
responsibilities. Schema casting consumes decoded mappings and lists/tuples.
Coordinate transforms, class vocabularies, image sizes, units, and precision
must be supplied explicitly. The test suite exercises YOLO normalized text
rows -> a pixel-corner data IR -> Ultralytics JSON using those explicit inputs.

## Concrete adapters

[ISIR adapters](adapters/README.md) use explicit image context and metadata.
Flatbug and COCO support import/export; YOLO detection TXT, Ultralytics detection
Results/JSON, BioMoth CSV and AMI box lists have import-only adapters. Multi-image
sources produce collections of single-image records. The schema handler remains
generic; coordinate semantics and source-specific metadata belong to adapters.

## Shared higher-order types

`shared_types.json` is a mapping of names to definitions in the same language:

```json
{
    "float_pair": ["T[float]", "T[float]"],
    "float_quad": ["T[float]", "T[float]", "T[float]", "T[float]"],
    "float_vector": ["T[float]"],
    "float_matrix": ["T[float_vector]"]
}
```

The default library is injected before compilation. Local `types` take
precedence; built-in names cannot be overridden. Neither input is mutated.
Use `shared_types={}` for a self-contained schema or supply your own mapping
as a replacement library. The library contains types only; any named enums used
by a supplied definition must exist in the descriptor's `enums` section.
Forward references are allowed, cycles are rejected. All injected definitions
are checked, even when the root structure does not reference them.

Shared types describe shape, not geometry. For example, `float_quad` does not
prescribe xyxy versus xywh, coordinate origin, or normalization. Those meanings
remain explicit in the relevant schema notes and adapters.

## Casting behavior

- Required fields must exist. Optional fields may be absent; a present null
  requires an explicit null type. Unlisted object fields are preserved.
- Casts return fresh containers and preserve input data. Numeric casts reject
  truncation, overflow, underflow to zero, and loss of integral values.
  Floating casts use Python binary64; fractional rounding is expected.
- `number` preserves existing Python int/float values. Numeric strings become
  an int when integral, otherwise a finite float. Strings produced from boolean
  values use `true`/`false`; boolean inputs do not implicitly become numbers.
- Arrays and positional tuples normalize to Python lists. Constraints compare
  values after casting, including numeric types, so `T[integer](3)` accepts
  `"3.0"` and produces `3`.
- Union casts prefer an outcome exactly preserving the input's value and types.
  Otherwise all successful branches must yield the same typed result. Ambiguous
  casts raise `FormatError`; branch order never silently chooses a meaning.
- Omitted optional tuple positions may be any subset of the optional suffix.
  If multiple layouts fit, casting fails. Producer options must disambiguate
  such schemas before casting (e.g. a sixth YOLO column could be confidence or
  tracking ID). A specialized descriptor can state the known row layout.
- `FormatError` includes the field/index path. This is structural casting, not
  enforcement of geometric relationships, units, or conditions recorded in notes.

Run all language and conversion tests from the repository root:

```sh
python3 scripts/check_formats.py
python3 -m unittest discover -s scripts/tests -v
```
