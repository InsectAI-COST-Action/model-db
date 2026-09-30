# Formats and conversion

For model outputs, start with [the conversion guide and runnable example](../../../examples/conversion/README.md).
`Converter` looks up adapters and converts existing predictions to COCO or another
supported target. Model loading and inference stay in the consuming application.
The conversion API requires Python 3.11+ to read model-card TOML.

## Schema API

The independent schema handler uses Python 3.10+ and the standard library.
From a checkout, set `PYTHONPATH=src`.

```python
from iai_model_zoo.formats import Schema

schema = Schema.load("static/formats/detection/flatbug.json")
validated = schema.cast(decoded_prediction)
```

`Schema.from_dict(document)` accepts an in-memory descriptor. Casting returns
fresh Python containers and raises `FormatError` with the failing field/index
path. It validates structure and safe casts; geometric and semantic checks belong
to the adapters. Unknown fields are preserved.

See the [language specification](../../../static/formats/README.md) for syntax,
casting rules, shared types and constraints. `shared_types={}` disables the
injected shared type library; an explicit mapping replaces it. Local definitions
otherwise take precedence over shared definitions.

## Lower-level interfaces

- `schema.structure` and `schema.types` expose the compiled type graph for tools.
- `convert(value, source, target, transform)` casts the source, calls an explicit
  transform, then casts the target. This is a schema utility, distinct from
  `Converter.convert`, which selects and executes registered output adapters.
- [Direct adapter APIs](adapters/README.md) expose format-specific options and
  preservation limits. They remain available independently of `Converter`.
- [Registry lookup](../registry/README.md) inspects available conversion paths
  without importing or executing adapters.

Run checks from the repository root:

```bash
python3 scripts/check_formats.py
uv run --locked --project src/probe python -m unittest discover -s scripts/tests -q
```
