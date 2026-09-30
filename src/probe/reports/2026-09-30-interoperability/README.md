# Conversion interoperability checks

These checks reuse retained author outputs; they do **not** rerun inference or
measure detection accuracy. The executable cases are in
[`test_interoperability.py`](../../../../scripts/tests/test_interoperability.py).
Category names supplied by tests are illustrative context, not verified taxonomy.

```bash
uv run --locked --project src/probe python -m unittest discover -s scripts/tests -p test_interoperability.py -v
```

| Input/evidence | Conversion exercised | Result |
| --- | --- | --- |
| Flatbug N and M_v2 retained JSON, populated and blank | Flatbug → ISIR → COCO → ISIR → Flatbug | 12 and 11 detections retained; boxes, scores, classes and areas agree. Scale needs an explicit fallback after COCO export. |
| ArthroNat retained tensor values reconstructed as decoded Results projections | Results collection → ISIR / COCO | Two images, including one empty; one detection. Geometry and confidence preserved. |
| BioMoth retained author CSV | CSV → ISIR → COCO | 32 detections; explicitly completed empty image retained via manifest. Calibrated cm² measurements are not incorrectly exported as pixel area. |
| Stark YOLOv5n and YOLOv7-tiny retained TXT | TXT → ISIR → COCO | 1 and 13 detections; normalized coordinates correctly converted using the respective image dimensions. |
| Seeded synthetic TXT, 40 images / 115 detections | TXT → ISIR → COCO → ISIR | Geometry agrees to nine decimal places; confidence, image identity and empty images preserved. Dataset-wide annotation IDs supplied explicitly. |
| Empty collections | ISIR, Results, TXT and JSON → COCO | Empty dataset containers remain valid. |
| Deliberate incompatibilities | AMI boxes → COCO; box-only TXT → Flatbug; Mothbot lookup | Clear rejection of missing category IDs with the fallback explicitly disabled, missing polygons, and missing adapter respectively. |

## Issues found and fixed

The Results batch adapter accepted ordered image contexts, while the conversion
facade assumed a mapping during metadata application. Conversely, passing a
mapping fed its keys to the Results adapter as if they were contexts. Both paths
failed. The facade now handles ordered lists/tuples; the Results wrapper matches
mapping entries by exact source path. Tests reverse manifest order to catch
accidental positional associations and reject missing paths or duplicate IDs.

Context validation now rejects malformed context objects directly, including
empty dictionaries, rather than replacing them with defaults or leaking attribute
errors. Per-image metadata lookup is indexed once by ID rather than rescanning
the entire manifest for every image.

## Integration effort and remaining limits

- Flatbug and Results to COCO require one call plus explicit category vocabulary
  and suitable image IDs. Results supports both ordered contexts and path maps.
- TXT additionally needs dimensions and producer settings (`save_conf`, and any
  nondefault tracking/coordinate layout). These cannot be reliably inferred.
- CSV batches need a source-keyed manifest. Missing rows do not establish an empty
  processed image; `include_empty=True` is an explicit caller assertion.
- Dataset-wide annotation IDs remain the largest routine burden. Importers often
  number detections from zero per image, so multi-image COCO export needs an
  explicit `(image_id, instance_id) -> integer` mapping. No automatic allocation
  policy was added in this work.
- Structural conversion is not lossless metadata conversion. Flatbug scales and
  BioMoth calibrated measurements do not have equivalent standard COCO fields.
  Preserve intermediate records as sidecars when those values matter.
- An importer alone does not guarantee every exporter can accept its records.
  Missing classes, contours or compatible geometry remain real incompatibilities.

The complete suite passed with 77 tests; all 26 descriptors validated. These
results establish the tested paths, not universal compatibility across models.

Follow-up: COCO export now supports an explicit `fallback_category` for
class-agnostic detections. AMI boxes can therefore be exported without a classifier;
existing classifications remain unchanged. Integration tests cover mixed classified
and unclassified detections, empty images, category conflicts, and input preservation.

The generic `object` category is now the default COCO export convention for
uncategorized detections. Explicit vocabulary is needed only for existing class
IDs; callers may customize or disable the fallback. ISIR classification remains
optional.
