from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional

# Bounding box represented as [x, y, width, height]
Box = tuple[float, float, float, float]

# COCO segmentation: RLE (dict with counts/size) or Polygon (list of coordinate lists)
RLE = dict[str, Any]
Polygon = list[float]
Segmentation = RLE | list[Polygon]


@dataclass
class Info:
    year: int
    version: str
    description: str
    contributor: str
    url: str
    date_created: datetime


@dataclass
class Image:
    id: int
    width: int
    height: int
    file_name: str
    license: int
    flickr_url: str
    coco_url: str
    date_captured: datetime


@dataclass
class License:
    id: int
    name: str
    url: str


@dataclass
class Category:
    id: int
    name: str
    supercategory: str | None = None


@dataclass
class Annotation:
    id: int
    image_id: int
    category_id: int
    segmentation: Segmentation | None = None
    area: Optional[float] = None
    bbox: Optional[Box] = None
    iscrowd: Optional[Literal[0, 1]] = None


@dataclass
class COCODataset:
    info: Info
    images: list[Image] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)
    licenses: list[License] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)