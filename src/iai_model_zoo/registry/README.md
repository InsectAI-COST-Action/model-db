# Output adapter lookup

Python 3.11+ is required to open a snapshot. The registry joins model-card
`output_format` values to format descriptors and their small `notes.adapters`
entry-point mappings. It imports no adapters, loads no models, and performs no
inference or network requests. Consuming repositories own model execution.

```python
from iai_model_zoo.registry import Registry
registry = Registry.open('/path/to/model-db')
candidates = registry.query(model='arthronat', target='coco')
plan = registry.resolve(model='arthronat', cardinality='one', target='isir')
plan = registry.resolve(source='flatbug', target='coco')
```

`query` lists candidates; `resolve` raises `SelectionError` with `.candidates`
when a source format or input cardinality must be selected. Repeated identical
formats are deduplicated, preserving their architecture associations. Distinct
formats remain alternatives; asset names never determine formats. `model_fields`
filters exact card values. `registry.formats` includes unsupported formats too.

`ready` means an adapter path exists, not that the call is configured or the
predictions are valid. `unsupported` means a necessary mapping is absent.
`needs_context` means ISIR input cardinality is unspecified. Missing API
arguments and invalid predictions are diagnosed by the adapters when called.

For routine integration, use [Converter](../../../examples/conversion/README.md),
which executes the plan and manages intermediate containers. Descriptor entry
points now use the uniform `(data, *, context, options, source)` wrapper API;
importers return `ConversionBatch`, exporters accept it. Direct adapter functions
remain available.

Plans contain detached model/format records, entry-point strings, explicit
collection operations and metadata fingerprints. They do not execute the plan.
`collect` wraps one image for a collection exporter; `mode='each'` applies an
exporter separately to every ISIR record. Actual container preparation belongs
to the caller: COCO uses `Batch(images, metadata)`, not a plain list. Preserve
its dataset metadata and consult the adapter API for categories and ID mappings.
For YOLO TXT, explicitly supply the format profile and producer options.

The [adapter documentation](../formats/adapters/README.md) owns API requirements;
the registry does not duplicate them in schemas. A snapshot fingerprint covers
metadata read, not installed implementation code.

## Extending the database

- Add a model card referring to existing formats; no registry edits.
- Add a format descriptor; no central catalogue update.
- Implement conversion and add its entry-point mapping in that descriptor.

See [the mapping syntax](../../../static/formats/README.md#adapter-bindings).

```bash
uv run --locked --project src/probe python examples/registry/resolve.py --model arthronat --query
uv run --locked --project src/probe python examples/registry/resolve.py --model arthronat --cardinality one --target coco
```
