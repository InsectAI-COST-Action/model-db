# Mothbot conversion: native and direct inference routes

Both routes preserve the **oriented** ISIR box: center, width, height, and angle
in radians counterclockwise in bottom-left coordinates. Four corners are retained
as a polygon. COCO gets an axis-aligned envelope and polygon segmentation. No
classification or polygon area is invented. Native angle conventions remain
recorded as metadata; they are not copied blindly into the ISIR angle field.

| Route | Evidence | Conversion result |
| --- | --- | --- |
| Native Mothbot `_save_result` JSON | Retained real author-writer output from the earlier probe: 15 specimen detections, zero blank detections | Reconstructed oriented corners match the original vertices; COCO preserves polygons and confidence |
| Direct Ultralytics OBB Results | New cached MBD-1-1 CPU inference, Ultralytics 8.4.90: 15 specimen detections, zero blank detections | Actual Results objects converted to ISIR/COCO; exported corners checked against Results properties |

The direct route bypasses the author JSON writer, thumbnails, GUI and downstream
identification. This checks conversion and one checkpoint, not model accuracy,
all Mothbot variants, or equivalence of entire inference pipelines.

From the repository root, with the existing cached weights/image:

```bash
uv run --locked --project src/probe/environments/modern python src/probe/reports/2026-09-30-mothbot-conversion/probe.py
uv run --locked --project src/probe python -m unittest discover -s scripts/tests -p test_mothbot_conversion.py -v
```

`probe.py` verifies cached input SHA-256 hashes, performs no downloads and writes
`report.json` plus property projections in `*-results.json`. These projections
are probe artifacts, not an author JSON export. The report records runtime
versions and explicit prediction settings; the existing modern environment lock
pins dependencies. Timing includes conversion and is not a benchmark.

## Use

```python
context = ConversionContext(image=ImageContext(1, width, height, file_name))
native_coco = converter.convert(native_json, model="mothbot", target="coco", context=context)
direct_coco = converter.convert(obb_result, source="ultralytics-obb-results", target="coco", context=context)
```

For batches, set `cardinality="collection"` and provide image contexts and
annotation ID mappings as needed. Native format assignment on the model card
stays unchanged; alternative-route support is reported separately.
