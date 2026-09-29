"""Per-image output of Flatbug's json_data serializer."""

from dataclasses import dataclass
from typing import Any

Box = list[float]
Point = list[float]
Contour = list[Point]


@dataclass
class FlatbugResult:
    boxes: list[Box]
    contours: list[Contour]
    confs: list[float]
    classes: list[int]
    # The serializer passes these through without specifying their types.
    scales: Any
    areas: Any
    image_path: str
    image_width: int
    image_height: int
    mask_width: int
    mask_height: int
    identifier: None = None
