"""Author YOLO detection text profiles -> ISIR; no layout autodetection."""

from ..schema import FormatError, Schema
from ._common import record
from ._inputs import collection, xyxy_to_ir

PROFILES = {
    "yolov5-detect-txt", "yolov7-detect-txt", "yolov7-segment-txt",
    "ultralytics-detect-txt",
}


def to_ir(data, *, image, profile, save_conf, tracking=False, save_format=0):
    """data is text or decoded rows; all columns are selected by producer options.

    save_format=1 is the YOLOv5 normalized-xyxy variant. All other supported
    profiles use normalized center/width/height. Tracking IDs are native extras.
    """
    if profile not in PROFILES:
        raise FormatError(f"Unsupported detection TXT profile {profile!r}")
    if type(save_conf) is not bool or type(tracking) is not bool:
        raise FormatError("save_conf and tracking must be explicit booleans")
    if tracking and profile != "ultralytics-detect-txt":
        raise FormatError("tracking is only supported by ultralytics-detect-txt")
    if type(save_format) is not int or save_format not in (0, 1):
        raise FormatError("save_format must be 0 or 1")
    if save_format and profile != "yolov5-detect-txt":
        raise FormatError("save_format=1 is only supported by yolov5-detect-txt")
    info = image.image()
    rows = [line.split() for line in data.splitlines() if line.strip()] if isinstance(data, str) else data
    # Specialize the schema to avoid guessing whether a sixth integer is a
    # confidence or tracking ID (both can be integer-valued on disk).
    columns = ["T[integer]"] + ["T[float]"] * 4
    if save_conf:
        columns.append("T[float]")
    if tracking:
        columns.append("T[integer]")
    rows = Schema.from_dict(dict(types={}, enums={}, structure=[columns], notes={})).cast(rows)
    instances = []
    for i, row in enumerate(rows):
        if save_format:
            box = xyxy_to_ir(row[1:5], info, normalized=True)
        else:
            x, y, w, h = row[1:5]
            box = [x * info["width"], (1 - y) * info["height"],
                   w * info["width"], h * info["height"]]
        instance = dict(id=i, bbox=box, category_id=row[0])
        if save_conf:
            instance["confidence"] = row[5]
        if tracking:
            instance["extra_information"] = {profile: {"track_id": row[-1]}}
        instances.append(instance)
    return record(info, instances, image.metadata, {profile: dict(
        save_conf=save_conf, tracking=tracking, save_format=save_format,
    )})


def to_ir_many(inputs, *, images, profile, save_conf, tracking=False,
               save_format=0, include_empty=False):
    """Map source keys to text/rows; no directory scanning or implicit file reads."""
    return collection(inputs, images, lambda data, ctx: to_ir(
        data, image=ctx, profile=profile, save_conf=save_conf,
        tracking=tracking, save_format=save_format,
    ), include_empty=include_empty)


# Uniform conversion interface; direct APIs above remain supported.

def import_one(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(to_ir, data, options, image=context.image, profile=source)
    return ConversionBatch([result])

def import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(to_ir_many, data, options, images=context.images, profile=source)
    return ConversionBatch(result)
