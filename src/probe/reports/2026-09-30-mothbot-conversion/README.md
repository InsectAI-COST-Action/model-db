# Mothbot conversion evidence

| Route | Input | Check |
| --- | --- | --- |
| Native JSON | Retained author-writer outputs from the [native probe](../2026-09-30-format-expansion/mothbot/report.json) | Oriented corners and confidence survive conversion |
| Direct OBB Results | MBD-1-1 CPU inference; 15 specimen detections and a blank control | ISIR corners and COCO segmentation match Results polygons |

The direct route excludes the author writer, thumbnails, GUI and identification.
These checks establish conversion behavior, not accuracy or pipeline equivalence.

`report.json` records input hashes, runtime versions and prediction settings.
`*-results.json` contains Results property projections used by
[test_mothbot_conversion.py](../../../../scripts/tests/test_mothbot_conversion.py),
not an author JSON export.

Reproduce from the repository root after preparing the cached weights and image
identified by the report. The script verifies their hashes and performs no downloads:

```bash
uv run --locked --project src/probe/environments/modern python src/probe/reports/2026-09-30-mothbot-conversion/probe.py
uv run --locked --project src/probe python -m unittest discover -s scripts/tests -p test_mothbot_conversion.py -v
```

See the [adapter reference](../../../iai_model_zoo/formats/adapters/README.md#mothbot-native-json-and-direct-obb-results)
for usage and geometry preservation limits.
