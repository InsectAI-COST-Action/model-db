+++
title = "Conversion coverage: native and alternative routes"
+++

Coverage review: **30 September 2026**. Support means a conversion adapter exists;
it does not mean every checkpoint or inference implementation has been tested.
[Use the conversion API](../single-image/) to export to COCO.

## Native outputs

**8 of 15 detection model entries (53%)** have importers for their advertised
output formats; excluding the deprecated entry, **7 of 14 (50%)**.

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
| Mothbot | Not yet: oriented-box JSON | Geometry needs explicit handling |
| POLLINATOR | Not yet: annotated frame folders | Native export omits machine-readable detections |
| Ultra-lightweight CNNs | Not applicable to instance detection: presence score | No instance geometry |
| Bjerge et al. (2023) | Unresolved native format | Historical exporter pairing unresolved |
| SAM 3 | Unassigned native format | No registered native contract |

All supported imports can supply detections for COCO; class-agnostic inputs use
the default `object` category. Valid image context, IDs and any retained class
vocabulary are still required. Grounding DINO phrases and MCC24 classification
scores remain metadata, separate from detection confidence.

## Alternative routes — counted separately

An application can expose a supported native representation earlier in its
pipeline, or translate its own detection objects to ISIR. This may make COCO
export possible even when the advertised output has no importer. It does **not**
change the native coverage figure above.

| Route | Current compatibility | Evidence and limits |
| --- | --- | --- |
| ArthroNat direct Ultralytics prediction | Existing Results importer | Already the advertised interface; no additional coverage to count |
| InsectDCT plain detector in `insect-model-zoo` | Earlier Results can use the existing importer; final application objects need its ISIR bridge | Source-inspected route, not end-to-end tested here. Different preprocessing, classifier stages and checkpoint versions may apply |
| Grounding DINO in `insect-model-zoo` | Application `Detection` → ISIR bridge | Custom per-word scoring and NMS differ from the pinned HF output; do not use the new native importer on those objects |
| Mothbot/SAM 3 application detection objects | Potential application ISIR bridge preserving polygons | Needs validation of geometry and metadata; native import remains unsupported |
| POLLINATOR detector output before frame rendering | Existing TXT importer if the actual output matches its contract | Proposed extraction route; not verified here |
| BioMoth/AMI single-image wrappers | Existing importers if the wrappers preserve the documented outputs | No extra model coverage; source-specific preprocessing must be preserved |

**No additional model entry is newly verified end-to-end through an alternative
route by this review.** Application bridge availability, source inspection and
real conversion tests are different evidence levels. The external interface was
reviewed at `insect-model-zoo` commit `bbe79be`; no changes or inference runs were
performed there.

## Use the actual route's output format

When the output differs from the model card, select its format explicitly and
supply model provenance as metadata:

```python
from iai_model_zoo.formats import ConversionContext
from iai_model_zoo.formats.adapters import Metadata

output = converter.convert(
    predictions,
    source="ultralytics-detect-results",  # what this route actually returns
    target="coco",
    context=ConversionContext(
        image=image_context,
        categories=categories,
        metadata=Metadata(model={"name": "my detector and checkpoint"}),
    ),
)
```

If the application already emits valid ISIR, use `source="isir"`. Text labels in
`category_id` need an explicit integer vocabulary for COCO, or can be retained
as metadata with `category_id` omitted for class-agnostic export. Supplying both
`model` and `source` filters the card's declared formats; it does not override
them. Inference implementation remains the application's responsibility.

[Interoperability tests and results](https://github.com/InsectAI-COST-Action/model-db/blob/main/src/probe/reports/2026-09-30-interoperability/README.md) ·
[Alternative inference investigations](https://github.com/InsectAI-COST-Action/model-db/blob/main/src/probe/inference-routes.md) ·
[External application families](https://github.com/InsectAI-COST-Action/insect-model-zoo/tree/bbe79be/zoo/families)
