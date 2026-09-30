"""Per-image output of Flatbug's json_data serializer."""

from dataclasses import dataclass

@dataclass
class FlatbugResult:
    boxes: list[list[float]]
    contours: list[list[list[float]]]
    confs: list[float]
    classes: list[int]
    scales: list[float]
    areas: list[float]
    image_path: str
    image_width: int
    image_height: int
    mask_width: int
    mask_height: int
    identifier: None | str = None
