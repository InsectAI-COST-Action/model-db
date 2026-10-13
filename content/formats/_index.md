+++
title = "Output formats and examples"
+++

Convert existing model predictions to a standard format such as **COCO** using
one Python call. Your application runs the model; the conversion module looks
up its output adapter and handles the conversion.

[How to convert predictions to COCO](single-image/) ·
[Runnable pipeline example](https://github.com/InsectAI-COST-Action/model-db/blob/main/examples/conversion/pipeline.py)

[Conversion support](coverage/) lists importers and their evidence.

## Understand the source format

A model architecture does not uniquely determine its output format. A wrapper
might return boxes, write measurement tables, or save annotated photographs.
The examples below show the actual documented interfaces, including units and
fields that need external context. Their small values are illustrative unless
explicitly labelled as a retained source example.

For the same box in a **200 × 100** image:

| Representation | Values | Meaning |
| --- | --- | --- |
| Pixel corners | `[10,20,50,60]` | Top-left and bottom-right corners |
| COCO box | `[10,20,40,40]` | Top-left position, width, height |
| YOLO normalized box | `[0.15,0.4,0.2,0.4]` | Center and size, divided by image dimensions |
| ISIR box | `[30,60,40,40]` | Pixel center and size, **bottom-left** origin |

Each page links to its machine-readable descriptor and explains its coordinates,
required context and limitations. Examples are illustrative unless labelled as
retained outputs; tensor projections are not author JSON exports.
