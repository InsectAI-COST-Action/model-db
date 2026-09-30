+++
title = "Convert model outputs to COCO"
+++

Run inference in your own application, then pass the predictions to `Converter`.
It selects adapters using the model card's `output_format` and returns the target
format. It does not load models or run inference.

## Convert predictions

From a repository checkout with Python 3.11+ and `PYTHONPATH=src`:

```python
from iai_model_zoo.formats import Converter, ConversionContext
from iai_model_zoo.formats.adapters import ImageContext

converter = Converter.open("/path/to/model-db")

# predictions comes from your application's model inference.
output = converter.convert(
    predictions,
    model="arthronat",       # database model name
    target="coco",
    context=ConversionContext(
        image=ImageContext(1, width, height, file_name),
        categories=categories,  # [{"id": 0, "name": "..."}, ...]
    ),
)
```

`output` is a COCO dataset dictionary, ready for `json.dump`. Supply the actual
image dimensions, filename and class vocabulary from your application. Instead
of `model`, use `source="flatbug"` or another format identifier when you already
know the output format. If a model lists several formats, also specify `source`
to identify the one your inference code produces.

The same call supports other registered export targets, including `flatbug`.
Conversion cannot invent missing information: for example, Flatbug export needs
contours and areas. Existing class IDs need a matching category vocabulary for COCO.
An unsupported format needs an adapter before it can be converted.

Class-agnostic detections (for example, AMI boxes) automatically receive a generic
`object` category during COCO export. No classification is required. Existing
categories remain unchanged. Customize the category with
`export_options={"fallback_category": {"id": 9, "name": "object"}}`, or disable
the fallback with `export_options={"fallback_category": None}`.

## Multiple images and producer settings

Set `cardinality="collection"` for multi-image input. When the source omits image
information, supply `images={source_key: ImageContext(...)}` in the context.
COCO output keeps images separate and contains dataset-wide annotations.

Use `import_options` for producer settings. For example, YOLO TXT requires
`import_options={"save_conf": False}` when its rows contain no confidence column.
Use the settings that actually produced your outputs; conversion does not guess
them from the model architecture.

COCO image and annotation IDs must be unique integers. Valid source IDs are
preserved. When needed, supply `image_ids` and `annotation_ids` mappings through
`ConversionContext`; automatic ID allocation is not performed.

## Run an example without a model

```bash
uv run --locked --project src/probe python examples/conversion/pipeline.py
```

This prints COCO JSON from illustrative saved predictions. Replace the example's
predictor with your application's inference function. No model download is needed.

See the [abstract pipeline example](https://github.com/InsectAI-COST-Action/model-db/blob/main/examples/conversion/pipeline.py)
and [integration guide](https://github.com/InsectAI-COST-Action/model-db/blob/main/examples/conversion/README.md)
for context, metadata and ID-mapping examples. [Browse the format examples](../)
for source layouts, coordinate interpretation and machine-readable schemas.
ISIR is used internally; callers do not need to construct it for ordinary conversions.
