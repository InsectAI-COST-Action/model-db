+++
title = "Convert model outputs to COCO"
+++

Run inference in your application, then convert its predictions using Python 3.11+
and a repository checkout with `PYTHONPATH=src`:

```python
from iai_model_zoo.formats import Converter, ConversionContext
from iai_model_zoo.formats.adapters import ImageContext

converter = Converter.open("/path/to/model-db")
output = converter.convert(
    predictions,
    model="arthronat",
    target="coco",
    context=ConversionContext(
        image=ImageContext(1, width, height, file_name),
        categories=categories,  # [{"id": 0, "name": "..."}, ...]
    ),
)
```

`output` is a COCO dataset dictionary, ready for `json.dump`. Supply your image
information and class vocabulary. Use `source="flatbug"` or another format ID
instead of `model` when you know the output format directly.

Run the saved-output example without downloading a model:

```bash
uv run --locked --project src/probe python examples/conversion/pipeline.py
```

The [integration guide](https://github.com/InsectAI-COST-Action/model-db/blob/main/examples/conversion/README.md)
covers multiple images, producer settings, metadata and ID mappings.
See [supported conversions](../coverage/) and [format examples](../).
