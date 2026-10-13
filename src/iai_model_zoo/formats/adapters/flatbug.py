"""Flatbug per-image JSON <-> ISIR; coordinates are original-image pixels."""

from copy import deepcopy

from ..schema import FormatError
from ._common import (
    checked_ir,
    extras,
    flip_polygon,
    ir_to_xywh,
    record,
    require,
    schema,
    xywh_to_ir,
)

COLUMNS = ("boxes", "contours", "confs", "classes", "scales", "areas")


def to_ir(data, *, image_id=None, metadata=None):
    data = schema("flatbug").cast(data)
    count = len(data["boxes"])
    for name in COLUMNS:
        if len(data[name]) != count:
            raise FormatError(
                f"flatbug.{name}: length must equal boxes length ({count})"
            )
    if data["mask_width"] <= 0 or data["mask_height"] <= 0:
        raise FormatError("flatbug: mask dimensions must be positive")
    height = data["image_height"]
    instances = []
    for i in range(count):
        x1, y1, x2, y2 = data["boxes"][i]
        xs, ys = data["contours"][i]
        if len(xs) != len(ys):
            raise FormatError(
                f"flatbug.contours[{i}]: x/y arrays have different lengths"
            )
        instances.append(
            {
                "id": i,
                "bbox": xywh_to_ir([x1, y1, x2 - x1, y2 - y1], height),
                "confidence": data["confs"][i],
                "category_id": data["classes"][i],
                "polygons": [flip_polygon(zip(xs, ys), height)],
                "area": data["areas"][i],
                "extra_information": {"flatbug": {"scale": data["scales"][i]}},
            }
        )
    if (data["mask_width"], data["mask_height"]) != (data["image_width"], height):
        # In the non-polygon path, Flatbug areas count mask-grid pixels.
        # Contours are already mapped to image coordinates by the author code.
        for instance in instances:
            native = instance["extra_information"]["flatbug"]
            native["mask_area"] = instance.pop("area")
            if native["mask_area"] < 0:
                raise FormatError("flatbug.areas: negative mask-grid area")
    # identifier is a run identifier (possibly a list), not a unique image ID.
    image = {
        "id": data["image_path"] if image_id is None else image_id,
        "width": data["image_width"],
        "height": height,
        "file_name": data["image_path"],
    }
    retained = {
        k: deepcopy(v)
        for k, v in data.items()
        if k not in (*COLUMNS, "image_path", "image_width", "image_height")
    }
    return record(image, instances, metadata, {"flatbug": retained})


def from_ir(value, *, scale=None, confidence=None, image_path=None):
    """Export without inventing contours, areas, classes or confidence.

    scale/confidence are explicit fallbacks for foreign IR records. Metadata
    without a Flatbug field remains in the IR; save that record as a sidecar.
    """
    value = checked_ir(value)
    image = value["image"]
    height = image["height"]
    result = extras(value, "flatbug")
    result.update({name: [] for name in COLUMNS})
    path = image_path if image_path is not None else image.get("file_name")
    if path is None:
        raise FormatError(
            "image.file_name or explicit image_path is required for Flatbug"
        )
    result.update(image_path=path, image_width=image["width"], image_height=height)
    result.setdefault("mask_width", image["width"])
    result.setdefault("mask_height", height)
    if result["mask_width"] <= 0 or result["mask_height"] <= 0:
        raise FormatError("flatbug: mask dimensions must be positive")
    for instance in value["instances"]:
        polygons = require(instance, "polygons")
        if len(polygons) != 1:
            raise FormatError(
                f"instance {instance['id']!r}: Flatbug requires exactly one contour; multipart/RLE conversion is not implicit"
            )
        x, y, w, h = ir_to_xywh(instance["bbox"], height, instance.get("angle", 0))
        polygon = flip_polygon(polygons[0], height)
        result["boxes"].append([x, y, x + w, y + h])
        result["contours"].append([[p[0] for p in polygon], [p[1] for p in polygon]])
        result["confs"].append(require(instance, "confidence", confidence))
        result["classes"].append(require(instance, "category_id"))
        native = extras(instance, "flatbug")
        if (result["mask_width"], result["mask_height"]) != (image["width"], height):
            if "mask_area" not in native:
                raise FormatError(
                    "Flatbug mask-grid area is required when mask and image dimensions differ"
                )
            result["areas"].append(native["mask_area"])
        else:
            result["areas"].append(require(instance, "area"))
        if "scale" not in native and scale is None:
            raise FormatError(
                f"instance {instance['id']!r}: supply scale for export to Flatbug"
            )
        result["scales"].append(native.get("scale", scale))
    return schema("flatbug").cast(result)


# Uniform conversion interface; direct APIs above remain supported.

def import_one(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(to_ir, data, options, image_id=context.image.id if context.image else None)
    if context.image is not None:
        image = context.image.image()
        if any(image[key] != result['image'][key] for key in ('width', 'height')):
            raise FormatError('Flatbug dimensions disagree with image context')
        result['image'].update(image)
    return ConversionBatch([result])

def export_one(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(from_ir, data.images[0], options)
    return result
