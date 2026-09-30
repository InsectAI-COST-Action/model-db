+++
title = "Output formats and examples"
+++

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

ISIR describes **one image**. Batch inputs become a collection of ISIR records,
including known empty images. A CSV without detections cannot tell us whether an
image was processed; preserve the input manifest and run completion information.
Class IDs also require the correct model vocabulary.

Start with [single-image inference and runnable conversion examples](single-image/).
Each format page links back to its machine-readable schema. Schemas document
an interface; source inspection and successful inference are different evidence
levels, identified in their notes and model cards.

Examples cover both files and Python/tensor interfaces. A readable JSON
projection of a tensor is explicitly labelled; it is not an invented author
export format. JSON arrays in a schema describe types, whereas arrays in these
examples contain actual example values.
