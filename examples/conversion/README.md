# Standardized outputs from your own predictor

[The abstract pipeline example](pipeline.py) accepts a `predict(inputs)` callable
from your application. Your application loads the model and runs inference;
`Converter` converts the returned output to ISIR, COCO, or another supported
target. The example's main block uses a saved-output stand-in and runs without
model dependencies:

```bash
uv run --locked --project src/probe python examples/conversion/pipeline.py
```

The same integration function works with any model whose actual output has a
registered importer. For unsupported formats, add an adapter and its descriptor
mapping. When a card lists different formats, pass `source` matching the output
of your chosen inference implementation. The converter does not inspect tensors
to guess which producer settings or format were used.

Ordinary callers need only:

```python
from iai_model_zoo.formats import Converter, ConversionContext
from iai_model_zoo.formats.adapters import ImageContext, Metadata

converter = Converter.open('/path/to/model-db')  # reuse for multiple calls
predictions = your_predictor(image)              # your inference implementation
output = converter.convert(
    predictions,
    model=model_name,                            # or source=format_name
    target='coco',
    context=ConversionContext(
        image=ImageContext(image_id, width, height, file_name),
        categories=categories,
        metadata=Metadata(model={'name': display_name}),
    ),
)
```

Single-image input is the default. Set `cardinality='collection'` for multi-image
inputs; provide `images={source_key: ImageContext(...)}` when the importer needs a
manifest. Ultralytics Results also accepts an ordered list of image contexts
matching the result order; a mapping instead matches exact result paths,
independently of mapping order. Repeated paths, such as video frames, need an
ordered list with distinct image IDs. ISIR returns one dict for one image or a list for a collection. COCO
returns a dataset dict. Exporting a collection to Flatbug returns a list of
per-image documents. Collection shape is explicit even for one or zero images.

`import_options` and `export_options` hold producer/export settings, for example
`import_options={'save_conf': False}` for YOLO TXT. The wrapper supplies its
profile from the resolved source format. Missing mandatory arguments and invalid
predictions produce conversion errors identifying the import or export stage.
Existing direct adapter functions remain available.

Context supplies facts, not guesses. Shared `metadata` replaces supplied ISIR
metadata sections after import; per-image `ImageContext.metadata` takes
precedence. Absent metadata preserves native information. `dataset_metadata`
merges into retained dataset metadata and explicit `categories` overrides its
category list. Model selection alone does not inject model metadata.

Class-agnostic detectors such as AMI export to COCO directly:

```python
output = converter.convert(
    boxes,
    model="ami-insect-detector",
    target="coco",
    context=ConversionContext(
        image=ImageContext(1, width, height, file_name),
    ),
)
```

Detections without `category_id` receive a generic `object` category automatically.
This is a COCO serialization convention, not a classification prediction. The
exporter reuses an existing `object` category or chooses an unused category ID,
and only adds the category when needed. Existing category IDs remain unchanged
and must still have vocabulary entries. Scores are not invented.

Customize this with `export_options={"fallback_category": {"id": 9, "name": "object"}}`,
or disable it with `export_options={"fallback_category": None}`. Conflicting
explicit category definitions are rejected. ISIR itself permits detections without
classification; the fallback is applied only on COCO export.

COCO IDs must be unique integers across the dataset. Preserve valid native IDs,
or supply `image_ids={original_id: integer}` and
`annotation_ids={(original_image_id, original_instance_id): integer}` in context.
IDs are not automatically allocated. Use dataset-wide mappings when combining
images or separately converted batches. Category IDs must agree with the supplied
vocabulary; they are never silently remapped.

A COCO-to-COCO conversion retains dataset metadata internally. Returning only
ISIR image records does not expose dataset metadata: retain it in the application
and supply it through context if exporting in a later, separate call. Keep ISIR
sidecars when a target cannot represent all your metadata.

Only use snapshots whose adapter references you trust: conversion imports and
executes their callables. `Registry.query()` remains a metadata-only discovery
API and does not import implementations. Neither API executes models.
