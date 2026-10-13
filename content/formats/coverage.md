+++
title = "Conversion support"
+++

An importer converts the named output to ISIR; COCO export additionally requires
valid image IDs, context and any existing class vocabulary. The evidence column
distinguishes contract tests from conversion of retained inference outputs.

| Model | Native output → ISIR | Conversion evidence |
| --- | --- | --- |
| AMI | Supported: box lists | Contract fixtures |
| ArthroNat | Supported: Ultralytics Results | Retained real tensor values |
| BioMoth | Supported: CSV | Retained real CSV |
| Flatbug | Supported: JSON | Retained real N and M_v2 outputs |
| Stark et al. (2023) | Supported: YOLOv5/v7 TXT | Retained real TXT |
| Ștefan et al. (2025), deprecated | Supported: YOLOv5/v7 TXT | Shared tested adapters; not included in the latest real-output conversion audit |
| Grounding DINO | Supported: pinned HF postprocessor | Contract fixtures; no new checkpoint run |
| Bjerge et al. (2025) | Supported: MCC24 CSV | Contract fixtures; full author inference remains unverified |
| InsectDCT | Not yet: author CSV tables | Retained outputs available for developing an importer |
| Insect Detect | Not yet: tracking CSV | Source-inspected contract |
| Mothbot | Supported: native oriented-box JSON | Retained real writer outputs, 15 detections and blank control |
| POLLINATOR | Not yet: annotated frame folders | Native export omits machine-readable detections |
| Ultra-lightweight CNNs | Not applicable to instance detection: presence score | No instance geometry |
| Bjerge et al. (2023) | Unresolved native format | Historical exporter pairing unresolved |
| SAM 3 | Unassigned native format | No registered native contract |


Mothbot also supports direct Ultralytics OBB Results through
`source="ultralytics-obb-results"`, verified with MBD-1-1 on a specimen and blank
control. This bypasses the author JSON writer and downstream pipeline; it is
separate from native-output support above.

Select `source` for the format your inference route actually returns. Using both
`model` and `source` requires that format to be declared on the model card.

[Conversion guide](../single-image/) ·
[Executable interoperability checks](https://github.com/InsectAI-COST-Action/model-db/blob/main/scripts/tests/test_interoperability.py) ·
[Mothbot evidence](https://github.com/InsectAI-COST-Action/model-db/blob/main/src/probe/reports/2026-09-30-mothbot-conversion/README.md)
