# Format inspection examples

For ordinary COCO conversion, start with [the integration example](../conversion/README.md).
These lower-level examples help inspect formats and adapter behavior:

- `to_isir.py`: convert the small format fixtures to the intermediate representation.
  Run `python3 examples/formats/to_isir.py --help` for supported formats.
- `predict_ultralytics.py`: an optional CPU inference helper for compatible local
  horizontal-detection checkpoints. It rejects segmentation, oriented-box and
  classification models.

The site's [format pages](../../content/formats/_index.md) retain readable examples,
interpretation notes and schema links. Their values live in
`data/format_examples.json`; tests validate them and execute the conversion examples.
Illustrative values and tensor projections are labelled as such, not presented
as observed author JSON exports.

Run the optional inference helper with a compatible local checkpoint and image:

```bash
uv run --locked --project src/probe/environments/modern \
  python examples/formats/predict_ultralytics.py \
  --weights /path/to/detector.pt --image /path/to/frame.jpg \
  --model-name "my detector" --imgsz 640 --conf 0.25 --iou 0.7 > prediction.isir.json
```

The helper runs on CPU and records these settings. It does not reproduce
specialized author preprocessing or downstream stages.
