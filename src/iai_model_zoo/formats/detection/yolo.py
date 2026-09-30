"""Types for serialized Ultralytics horizontal detection/segmentation JSON.

These describe parsed JSON dictionaries, not the native Results tensor object.
See static/formats/detection/ultralytics-*-json.json for source revisions and
normalization settings. Text exports are positional rows, not these dictionaries.
"""

from typing import TypedDict


class Box(TypedDict):
    x1: float
    y1: float
    x2: float
    y2: float


# Functional syntax preserves the producer's literal "class" key.
_DetectionRequired = TypedDict(
    "_DetectionRequired",
    {
        "name": str,
        "class": int,
        "confidence": float,
        "box": Box,
    },
)


class Detection(_DetectionRequired, total=False):
    track_id: int


class Segments(TypedDict):
    x: list[float]
    y: list[float]


class Segmentation(Detection):
    segments: Segments


DetectionJSON = list[Detection]
SegmentationJSON = list[Segmentation]
