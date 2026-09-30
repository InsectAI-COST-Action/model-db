"""Shared ISIR validation, metadata injection, and coordinate transforms."""

import math
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from ..schema import FormatError, Schema


@lru_cache(maxsize=None)
def schema(name):
    root = Path(__file__).resolve().parents[4]
    return Schema.load(root / "static" / "formats" / "detection" / f"{name}.json")


@dataclass(frozen=True)
class Metadata:
    """Known metadata supplied by the model registry, inference runner or caller.

    None means unknown/omitted. No clock reads, random UUIDs or model-name guesses.
    Inference time and capture/context time are intentionally separate.
    """

    model: dict | None = None
    inference: dict | None = None
    context: dict | None = None

    def apply(self, record):
        result = deepcopy(record)
        for key in ("model", "inference", "context"):
            value = getattr(self, key)
            if value is not None:
                result[key] = deepcopy(value)
        return checked_ir(result)


def checked_ir(record):
    result = schema("isir").cast(record)
    image = result["image"]
    if image["width"] <= 0 or image["height"] <= 0:
        raise FormatError("image: width and height must be positive")
    seen = set()
    for i, instance in enumerate(result["instances"]):
        if instance["id"] in seen:
            raise FormatError(f"instances[{i}].id: duplicate ID")
        seen.add(instance["id"])
        if instance["bbox"][2] < 0 or instance["bbox"][3] < 0:
            raise FormatError(f"instances[{i}].bbox: negative width/height")
        if instance.get("area", 0) < 0:
            raise FormatError(f"instances[{i}].area: negative area")
    return result


def record(image, instances, metadata=None, extra=None):
    value = {"ir_name": "ISIR", "ir_id": 1, "image": image, "instances": instances}
    if extra:
        value["extra_information"] = extra
    return (metadata or Metadata()).apply(value)


def extras(value, format_name):
    return deepcopy(value.get("extra_information", {}).get(format_name, {}))


def xywh_to_ir(box, height):
    x, y, w, h = box
    return [x + w / 2, height - y - h / 2, w, h]


def ir_to_xywh(box, height, angle=0):
    x, y, w, h = box
    cosine, sine = abs(math.cos(angle)), abs(math.sin(angle))
    w, h = w * cosine + h * sine, w * sine + h * cosine
    return [x - w / 2, height - y - h / 2, w, h]


def box_polygon(box, angle):
    """Four corners, counterclockwise in ISIR's bottom-left coordinate system."""
    x,y,w,h = box
    cosine,sine = math.cos(angle),math.sin(angle)
    return [[x+dx*cosine-dy*sine, y+dx*sine+dy*cosine]
            for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]


def flip_polygon(points, height):
    # Image-edge coordinates: flip about H, not H-1. This is its own inverse.
    return [[x, height - y] for x, y in points]


def require(instance, name, default=None):
    if name in instance:
        return instance[name]
    if default is not None:
        return default
    raise FormatError(
        f"instance {instance['id']!r}: {name} is required by the destination"
    )
