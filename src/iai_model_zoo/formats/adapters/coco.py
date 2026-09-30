"""COCO dataset JSON <-> a batch of per-image ISIR records.

Prediction-only COCO lists are not dataset JSON and need image/category context.
"""

from copy import deepcopy
from dataclasses import dataclass, field

from ..schema import FormatError, Primitive, cast
from ._common import (
    checked_ir,
    extras,
    flip_polygon,
    ir_to_xywh,
    record,
    schema,
    xywh_to_ir,
)


@dataclass
class Batch:
    """Keep dataset-level metadata once, separate from per-image ISIR records."""

    images: list[dict]
    metadata: dict = field(default_factory=dict)


def _index(rows, label):
    result = {}
    for row in rows:
        identifier = row["id"]
        if identifier in result:
            raise FormatError(f"coco.{label}: duplicate id {identifier!r}")
        result[identifier] = row
    return result


def _polygons(segmentation, height):
    result = []
    for polygon in segmentation:
        if len(polygon) % 2:
            raise FormatError(
                "coco.segmentation: polygon coordinate count must be even"
            )
        result.append(flip_polygon(zip(polygon[::2], polygon[1::2]), height))
    return result


def to_ir(data, *, metadata=None):
    """metadata may be Metadata or a callable receiving each COCO image record."""
    data = schema("coco").cast(data)
    images = _index(data["images"], "images")
    categories = _index(data["categories"], "categories")
    _index(data["annotations"], "annotations")
    grouped = {identifier: [] for identifier in images}
    for annotation in data["annotations"]:
        image_id = annotation["image_id"]
        if image_id not in images:
            raise FormatError(
                f"coco.annotation {annotation['id']}: unknown image_id {image_id!r}"
            )
        if annotation["category_id"] not in categories:
            raise FormatError(
                f"coco.annotation {annotation['id']}: unknown category_id"
            )
        if "bbox" not in annotation:
            raise FormatError(
                f"coco.annotation {annotation['id']}: this adapter requires bbox; segmentation-only annotations need an explicit bbox derivation"
            )
        image = images[image_id]
        height = image["height"]
        instance = {
            "id": annotation["id"],
            "bbox": xywh_to_ir(annotation["bbox"], height),
            "category_id": annotation["category_id"],
        }
        native = {
            k: deepcopy(v)
            for k, v in annotation.items()
            if k
            not in ("id", "image_id", "bbox", "category_id", "area", "score", "conf")
        }
        if "area" in annotation:
            instance["area"] = annotation["area"]
        score_keys = [k for k in ("score", "conf") if k in annotation]
        if score_keys:
            scores = [cast(Primitive("float"), annotation[k]) for k in score_keys]
            if any(v != scores[0] for v in scores):
                raise FormatError(
                    f"coco.annotation {annotation['id']}: conflicting score/conf"
                )
            instance["confidence"] = scores[0]
        segmentation = annotation.get("segmentation")
        if isinstance(segmentation, list):
            instance["polygons"] = _polygons(segmentation, height)
            native.pop("segmentation")
        elif isinstance(segmentation, dict):
            if segmentation["size"] != [height, image["width"]]:
                raise FormatError(
                    "coco.segmentation: RLE size differs from image dimensions"
                )
        instance["extra_information"] = {
            "coco": {"fields": native, "score_keys": score_keys}
        }
        grouped[image_id].append(instance)
    records = []
    for image in images.values():
        info = {k: image[k] for k in ("id", "width", "height", "file_name")}
        native = {k: deepcopy(v) for k, v in image.items() if k not in info}
        supplied = metadata(deepcopy(image)) if callable(metadata) else metadata
        records.append(record(info, grouped[image["id"]], supplied, {"coco": native}))
    return Batch(
        records,
        {k: deepcopy(v) for k, v in data.items() if k not in ("images", "annotations")},
    )


def from_ir(batch, *, image_ids=None, annotation_ids=None):
    """Export a Batch. Optional ID mappings avoid guessing new COCO IDs.

    image_ids maps IR image IDs to integers; annotation_ids maps
    (IR image ID, IR instance ID) pairs to globally unique integer IDs.
    Batch.metadata supplies categories and any dataset info/licenses.
    """
    # Validate and normalize even caller-constructed batch metadata once.
    result = schema("coco").cast(
        {
            **deepcopy(batch.metadata),
            "images": [],
            "annotations": [],
            "categories": batch.metadata.get("categories", []),
        }
    )
    categories = _index(result.get("categories", []), "categories")
    images, annotations = [], []
    for value in batch.images:
        value = checked_ir(value)
        info = value["image"]
        source_id = info["id"]
        image_id = (image_ids or {}).get(source_id, source_id)
        image_id = cast(
            Primitive("integer"),
            image_id,
            "coco.image.id (supply image_ids for nonnumeric IDs)",
        )
        if "file_name" not in info:
            raise FormatError("image.file_name is required for COCO export")
        image = extras(value, "coco")
        image.update(
            id=image_id,
            width=info["width"],
            height=info["height"],
            file_name=info["file_name"],
        )
        images.append(image)
        for instance in value["instances"]:
            native = extras(instance, "coco")
            annotation = native.get("fields", {})
            identifier = (annotation_ids or {}).get(
                (source_id, instance["id"]), instance["id"]
            )
            identifier = cast(
                Primitive("integer"),
                identifier,
                "coco.annotation.id (supply annotation_ids for nonnumeric IDs)",
            )
            category = cast(
                Primitive("integer"),
                instance.get("category_id"),
                "instance.category_id",
            )
            if category not in categories:
                raise FormatError(
                    f"category_id {category!r} is missing from Batch.metadata.categories"
                )
            annotation.update(
                id=identifier,
                image_id=image_id,
                category_id=category,
                bbox=ir_to_xywh(instance["bbox"], info["height"]),
            )
            if "area" in instance:
                annotation["area"] = instance["area"]
            if "polygons" in instance:
                annotation["segmentation"] = [
                    [
                        coordinate
                        for point in flip_polygon(polygon, info["height"])
                        for coordinate in point
                    ]
                    for polygon in instance["polygons"]
                ]
            elif isinstance(annotation.get("segmentation"), dict):
                if annotation["segmentation"]["size"] != [
                    info["height"],
                    info["width"],
                ]:
                    raise FormatError(
                        "retained COCO RLE dimensions no longer match the IR image"
                    )
            if "confidence" in instance:
                for key in native.get("score_keys") or ["score"]:
                    annotation[key] = instance["confidence"]
            annotations.append(annotation)
    _index(images, "images")
    _index(annotations, "annotations")
    result.update(images=images, annotations=annotations)
    result.setdefault("categories", [])
    return schema("coco").cast(result)
