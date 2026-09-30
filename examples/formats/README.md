# Format inspection examples

For ordinary COCO conversion, start with [the integration example](../conversion/README.md).
These lower-level examples help inspect formats and adapter behavior:

- `to_isir.py`: convert the small format fixtures to the intermediate representation.
  Run `python3 examples/formats/to_isir.py --help` for supported formats.
- `predict_ultralytics.py`: an optional CPU inference helper for compatible local
  detection checkpoints. Its command and evidence limits are in the
  [probe notes](../../src/probe/inference-routes.md).

The site's [format pages](../../content/formats/_index.md) retain readable examples,
interpretation notes and schema links. Their values live in
`data/format_examples.json`; tests validate them and execute the conversion examples.
Illustrative values and tensor projections are labelled as such, not presented
as observed author JSON exports.
