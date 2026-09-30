"""Explicit image context and small helpers for import-only adapters."""

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass

from ..schema import FormatError
from ._common import Metadata, checked_ir, xywh_to_ir


@dataclass(frozen=True)
class ImageContext:
    """Image identity/dimensions and optional known per-image metadata.

    Manifest keys identify source outputs; id identifies the image in ISIR.
    No filesystem access, image probing, or metadata inference is performed.
    """

    id: int | str
    width: int
    height: int
    file_name: str | None = None
    metadata: Metadata | None = None

    def image(self):
        value = dict(id=self.id, width=self.width, height=self.height)
        if self.file_name is not None:
            value["file_name"] = self.file_name
        return checked_ir(dict(ir_name="ISIR", ir_id=1, image=value, instances=[]))["image"]


def xyxy_to_ir(box, image, *, normalized=False):
    x1, y1, x2, y2 = box
    if normalized:
        x1, x2 = x1 * image["width"], x2 * image["width"]
        y1, y2 = y1 * image["height"], y2 * image["height"]
    return xywh_to_ir([x1, y1, x2 - x1, y2 - y1], image["height"])


def manifest_images(images):
    if not isinstance(images, Mapping):
        raise FormatError("images: expected a mapping of source keys to ImageContext")
    seen = set()
    for context in images.values():
        identity = context.image()["id"]
        if identity in seen:
            raise FormatError(f"images: duplicate ISIR image ID {identity!r}")
        seen.add(identity)


def collection(inputs, images, convert, *, include_empty=False):
    """Manifest order; absent inputs become empty only by explicit caller choice."""
    manifest_images(images)
    if not isinstance(inputs, Mapping):
        raise FormatError("inputs: expected a mapping keyed like the image manifest")
    unknown = inputs.keys() - images.keys()
    if unknown:
        raise FormatError(f"inputs: image keys missing from manifest: {list(unknown)!r}")
    return [
        convert(deepcopy(inputs[key]) if key in inputs else [], context)
        for key, context in images.items()
        if key in inputs or include_empty
    ]
