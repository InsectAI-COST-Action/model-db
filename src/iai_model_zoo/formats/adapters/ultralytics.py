"""Ultralytics horizontal detection Results / JSON -> ISIR.

No Ultralytics, Torch or NumPy import is needed. Native Results are projected
through their public attributes; callers may also supply decoded projections.
"""

from collections.abc import Mapping
from copy import deepcopy
from itertools import zip_longest
import json

from ..schema import FormatError
from ._common import record, schema
from ._inputs import ImageContext, collection, xyxy_to_ir


def _list(value):
    # Tensor -> CPU -> plain values; ndarray -> plain values. Duck typing avoids
    # importing model runtimes into applications that only consume saved data.
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    return value.tolist() if hasattr(value, "tolist") else value


def _projection(result):
    if isinstance(result, Mapping):
        data = deepcopy(dict(result))
    else:
        for name in ("masks", "obb", "probs", "keypoints"):
            if getattr(result, name, None) is not None:
                raise FormatError(f"ultralytics: detection adapter does not support {name}")
        if getattr(result, "boxes", None) is None:
            raise FormatError("ultralytics: Results.boxes is required, including empty detections")
        data = dict(orig_shape=_list(result.orig_shape), path=result.path,
                    names=deepcopy(result.names), boxes=dict(data=_list(result.boxes.data)))
    for name in ("masks", "obb", "probs", "keypoints"):
        if data.get(name) is not None:
            raise FormatError(f"ultralytics: detection adapter does not support {name}")
    return schema("ultralytics-detect-results").cast(data)


def to_ir(result, *, image=None):
    """One Results object or decoded projection -> one ISIR record.

    Without image context, the source path is the image ID. Supply ImageContext
    to override identity and attach metadata; its dimensions must match Results.
    """
    data = _projection(result)
    height, width = data["orig_shape"]
    if image is None:
        if not data["path"]:
            raise FormatError("ultralytics: supply image context when source path is empty")
        image = ImageContext(id=data["path"], width=width, height=height,
                             file_name=data["path"])
    info = image.image()
    if (info["height"], info["width"]) != (height, width):
        raise FormatError("ultralytics: image dimensions disagree with orig_shape")
    if "file_name" not in info:
        info["file_name"] = data["path"]
    rows = data["boxes"]["data"]
    if len({len(row) for row in rows}) > 1:
        raise FormatError("ultralytics: mixed tracked and untracked box rows")
    instances = []
    for i, row in enumerate(rows):
        instance = dict(id=i, bbox=xyxy_to_ir(row[:4], info),
                        confidence=row[-2], category_id=row[-1])
        if len(row) == 7:
            instance["extra_information"] = {"ultralytics": {"track_id": row[4]}}
        instances.append(instance)
    native = {key: deepcopy(value) for key, value in data.items() if key != "boxes"}
    native["box_fields"] = {key: deepcopy(value) for key, value in data["boxes"].items() if key != "data"}
    return record(info, instances, image.metadata, {"ultralytics": native})


def to_ir_many(results, *, images=None):
    """A list/generator of Results -> list of per-image ISIR records.

    Optional image contexts must match results one-for-one, in source order.
    Repeated paths (e.g. video frames) require caller-supplied unique image IDs.
    """
    if images is None:
        converted = [to_ir(result) for result in results]
    else:
        missing = object()
        converted = []
        for result, context in zip_longest(results, images, fillvalue=missing):
            if result is missing or context is missing:
                raise FormatError("ultralytics: image contexts and results have different lengths")
            if context is None:
                raise FormatError("ultralytics: supply an ImageContext for each result")
            converted.append(to_ir(result, image=context))
    ids = [item["image"]["id"] for item in converted]
    if len(set(ids)) != len(ids):
        raise FormatError("ultralytics: duplicate image IDs; supply distinct per-image contexts")
    return converted


def json_to_ir(data, *, image, normalized):
    """One Results.to_json output (text or decoded list) -> one ISIR record.

    normalized must explicitly match the producer's normalize option. Empty []
    is one image with no detections, not a zero-image batch.
    """
    if type(normalized) is not bool:
        raise FormatError("normalized must be an explicit boolean")
    if isinstance(data, str):
        data = json.loads(data)
    data = schema("ultralytics-detect-json").cast(data)
    info = image.image()
    instances = []
    for i, source in enumerate(data):
        if "segments" in source or "keypoints" in source:
            raise FormatError("ultralytics: detection JSON adapter does not support segmentation or pose")
        if set(source["box"]) != {"x1", "y1", "x2", "y2"}:
            raise FormatError("ultralytics: expected horizontal xyxy box")
        instances.append(dict(
            id=i,
            bbox=xyxy_to_ir([source["box"][k] for k in ("x1", "y1", "x2", "y2")],
                           info, normalized=normalized),
            confidence=source["confidence"], category_id=source["class"],
            extra_information={"ultralytics": {
                key: deepcopy(value) for key, value in source.items()
                if key not in ("box", "confidence", "class")
            }},
        ))
    return record(info, instances, image.metadata,
                  {"ultralytics": {"normalized": normalized}})


def json_to_ir_many(inputs, *, images, normalized, include_empty=False):
    """Map explicit image keys to per-image JSON strings or decoded lists."""
    return collection(inputs, images, lambda data, ctx: json_to_ir(
        data, image=ctx, normalized=normalized,
    ), include_empty=include_empty)


# Uniform conversion interface; direct APIs above remain supported.

def import_one(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(to_ir, data, options, image=context.image)
    return ConversionBatch([result])

def import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    images = context.images
    if isinstance(images, Mapping):
        # Match exact source paths, never dictionary iteration order.
        data = list(data)
        contexts = []
        for result in data:
            path = result.get('path') if isinstance(result, Mapping) else getattr(result, 'path', None)
            if path not in images:
                raise FormatError(f'ultralytics: image path {path!r} missing from manifest')
            contexts.append(images[path])
        images = contexts
    result = invoke(to_ir_many, data, options, images=images)
    return ConversionBatch(result)

def json_import_one(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(json_to_ir, data, options, image=context.image)
    return ConversionBatch([result])

def json_import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(json_to_ir_many, data, options, images=context.images)
    return ConversionBatch(result)
