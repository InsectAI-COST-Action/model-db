"""Pinned HF grounded postprocessor results -> per-image ISIR records."""
from collections.abc import Mapping
from copy import deepcopy

from ..schema import FormatError
from ._common import record, schema
from ._inputs import xyxy_to_ir
from .ultralytics import _list


def to_ir_many(results, *, images, normalized):
    """images is ordered like results; normalization must be explicit.

    Prompt phrases remain native metadata, not numeric category predictions.
    This is the documented HF postprocessor, not arbitrary raw Grounding DINO.
    """
    if type(normalized) is not bool:
        raise FormatError('grounding-dino: normalized must be an explicit boolean')
    if isinstance(images, Mapping):
        raise FormatError('grounding-dino: supply ordered image contexts; results contain no image keys')
    contexts = list(images)
    projected = []
    for result in results:
        if not isinstance(result, Mapping) or not {'boxes', 'scores', 'labels'} <= result.keys():
            raise FormatError('grounding-dino: each result needs boxes, scores and labels')
        projected.append({**deepcopy({k: v for k, v in result.items() if k not in ('boxes', 'scores')}),
                          'boxes': _list(result['boxes']), 'scores': _list(result['scores'])})
    projected = schema('grounding-dino-hf-results').cast(projected)
    if len(projected) != len(contexts):
        raise FormatError('grounding-dino: results and image contexts have different lengths')
    output, identities = [], set()
    for result, image in zip(projected, contexts):
        info = image.image()
        if info['id'] in identities:
            raise FormatError('grounding-dino: duplicate image ID')
        identities.add(info['id'])
        if len({len(result[k]) for k in ('boxes', 'scores', 'labels')}) != 1:
            raise FormatError('grounding-dino: boxes, scores and labels must have equal lengths')
        instances = []
        for i, (box, score, phrase) in enumerate(zip(result['boxes'], result['scores'], result['labels'])):
            if not 0 <= score <= 1:
                raise FormatError('grounding-dino: confidence must lie between zero and one')
            instances.append(dict(id=i, bbox=xyxy_to_ir(box, info, normalized=normalized),
                                  confidence=score, extra_information={'grounding_dino': {'phrase': phrase}}))
        output.append(record(info, instances, image.metadata,
                             {'grounding_dino': {'normalized': normalized,
                              **{k: v for k, v in result.items() if k not in ('boxes','scores','labels')}}}))
    return output


def import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    return ConversionBatch(invoke(to_ir_many, data, options, images=context.images))
