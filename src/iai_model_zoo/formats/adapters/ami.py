"""AMI postprocessed box lists -> one ISIR record or a per-image collection."""

from ._common import record, schema
from ._inputs import collection, xyxy_to_ir


def to_ir(boxes, *, image):
    info = image.image()
    boxes = schema("ami-detector-boxes").cast(boxes)
    instances = [dict(id=i, bbox=xyxy_to_ir(box, info)) for i, box in enumerate(boxes)]
    return record(info, instances, image.metadata)


def to_ir_many(inputs, *, images, include_empty=False):
    """inputs maps explicit image keys to per-image box lists, including []."""
    return collection(inputs, images, lambda data, ctx: to_ir(data, image=ctx),
                      include_empty=include_empty)
