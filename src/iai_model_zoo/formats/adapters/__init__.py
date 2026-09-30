"""Explicit, dependency-free adapters for decoded model-output dictionaries."""

from . import coco, flatbug
from ._common import Metadata

__all__ = ["Metadata", "coco", "flatbug"]
