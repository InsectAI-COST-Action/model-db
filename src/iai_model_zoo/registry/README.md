# Inspect available conversions

For routine conversion, use [Converter](../../../examples/conversion/README.md).
`Registry` is the read-only discovery API for applications that need to inspect
formats or explain unsupported/ambiguous selections. It requires Python 3.11+.

```python
from iai_model_zoo.registry import Registry

registry = Registry.open("/path/to/model-db")
candidates = registry.query(model="arthronat", target="coco")
plan = registry.resolve(model="arthronat", cardinality="one", target="coco")
```

`query` lists candidates; `resolve` requires one. Select `source` when a model has
different output formats and `cardinality` when both single-image and collection
importers exist. Ambiguity raises `SelectionError` with `.candidates`. Repeated
identical formats are deduplicated. `model_fields` filters exact card values;
`registry.formats` includes formats without adapters.

- `ready`: an adapter path exists; API arguments and predictions are unchecked.
- `unsupported`: a necessary adapter mapping is absent.
- `needs_context`: ISIR input cardinality has not been specified.

Plans contain detached model/format records, callable references, collection
operations and metadata fingerprints. Lookup does not import implementations,
fetch resources, or run inference. Fingerprints identify metadata, not installed
adapter code.

Model cards supply `output_format`; descriptors supply [entry-point mappings](../../../static/formats/README.md#adapter-bindings).
There are no additional model-to-adapter tables to update.

```bash
uv run --locked --project src/probe python examples/registry/resolve.py --model arthronat --query
```
