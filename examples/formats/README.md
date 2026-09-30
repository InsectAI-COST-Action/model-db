# Human-readable format examples

Browse **Formats** in the site's navigation or click a model's output-format
link. The pages are under `content/formats/`; curated values and display text
live in `data/format_examples.json`. All 26 descriptors have an example.
Examples are illustrative unless explicitly identified as retained schema
examples. Python/tensor projections are not presented as author JSON exports.

Run conversion examples without model dependencies:

```bash
python3 examples/formats/to_isir.py yolov5-detect-txt
python3 examples/formats/to_isir.py biomoth-csv
python3 examples/formats/to_isir.py coco
```

`--help` lists all supported conversions. Each source image becomes one ISIR
record. COCO demonstrates an explicitly empty second image. Conversion does not
unify unrelated class vocabularies or invent missing metadata.

`predict_ultralytics.py` is a minimal single-image CPU path for compatible local
horizontal-detection checkpoints; run it in the locked
`src/probe/environments/modern` environment. See
[the single-image guide](../../content/formats/single-image.md) for its command,
settings and limitations, and proposals for other author pipelines.

The standard format tests validate every example against its schema, check CSV
and TXT displays, and execute the conversion examples. This does not establish
prediction equivalence for proposed alternative inference workflows.
