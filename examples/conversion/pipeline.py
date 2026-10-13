"""Model-independent integration boundary, with a runnable saved-output demo.

Run: uv run --locked --project src/probe python examples/conversion/pipeline.py
The application owns predict(), including preprocessing and model inference.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from iai_model_zoo.formats import Converter, ConversionContext
from iai_model_zoo.formats.adapters import ImageContext, Metadata


def standardized_prediction(predict, inputs, *, converter, model, context,
                            target='coco', source=None, cardinality='one',
                            import_options=None, export_options=None):
    """Works with any model whose actual output format has a registered adapter.

    predict is supplied by the consuming repository; no inference implementation
    is selected or provided by the conversion module. For multiple model formats,
    source identifies the format returned by this particular prediction route.
    """
    predictions = predict(inputs)
    return converter.convert(
        predictions, model=model, source=source, target=target,
        cardinality=cardinality, context=context,
        import_options=import_options, export_options=export_options,
    )


if __name__ == '__main__':
    # A decoded Ultralytics output, standing in for the application's predictor.
    # No model, image download, or runtime is needed to run this example.
    saved_output = {
        'orig_shape': [80, 100], 'path': 'example.jpg',
        'names': {0: 'arthropod'},
        'boxes': {'data': [[10, 20, 30, 50, 0.9, 0]]},
    }
    output = standardized_prediction(
        lambda inputs: saved_output,
        'example.jpg',
        converter=Converter.open(ROOT),
        model='arthronat',
        context=ConversionContext(
            image=ImageContext(id=1, width=100, height=80, file_name='example.jpg'),
            categories=[{'id': 0, 'name': 'arthropod'}],
            metadata=Metadata(model={'name': 'ArthroNat'}),
        ),
    )
    print(json.dumps(output, indent=2))
