from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.formats import FormatError  # noqa: E402
from iai_model_zoo.formats.adapters import Metadata, coco, flatbug  # noqa: E402


def flatbug_sample():
    return {
        "boxes": [[10, 20, 30, 50]],
        "contours": [[[10, 30, 30], [20, 20, 50]]],
        "confs": [0.9],
        "classes": [1],
        "scales": [0.5],
        "areas": [300.0],
        "image_path": "insect.jpg",
        "image_width": 100,
        "image_height": 80,
        "mask_width": 100,
        "mask_height": 80,
        "identifier": ["run-id"],
        "native_extra": {"a": [1]},
    }


def coco_sample():
    return {
        "images": [
            {
                "id": 5,
                "width": 100,
                "height": 80,
                "file_name": "insect.jpg",
                "camera": "test",
            },
            {"id": 6, "width": 50, "height": 40, "file_name": "empty.jpg"},
        ],
        "annotations": [
            {
                "id": 42,
                "image_id": 5,
                "category_id": 7,
                "bbox": [10, 20, 20, 30],
                "segmentation": [[10, 20, 30, 20, 30, 50]],
                "area": 300,
                "iscrowd": 0,
                "score": 0.9,
                "native_extra": {"test": 1},
            }
        ],
        "categories": [{"id": 7, "name": "beetle"}],
        "native_dataset": {"key": ["value"]},
    }


class AdapterTests(unittest.TestCase):
    def test_flatbug_geometry_metadata_and_roundtrip(self):
        data = flatbug_sample()
        before = deepcopy(data)
        metadata = Metadata(
            model={"name": "Flatbug M_v2"},
            inference={
                "timestamp": "2026-09-30T12:00:00.000Z",
                "config": {"threshold": 0.1},
            },
            context={"group_name": "trap-1"},
        )
        ir = flatbug.to_ir(data, image_id="image-1", metadata=metadata)
        self.assertEqual(ir["ir_name"], "ISIR")
        self.assertEqual(ir["ir_id"], 1)
        self.assertEqual(ir["image"]["id"], "image-1")
        self.assertEqual(ir["instances"][0]["bbox"], [20.0, 45.0, 20.0, 30.0])
        self.assertEqual(
            ir["instances"][0]["polygons"], [[[10.0, 60.0], [30.0, 60.0], [30.0, 30.0]]]
        )
        self.assertEqual(ir["model"]["name"], "Flatbug M_v2")
        self.assertNotIn("timestamp", ir["context"])
        self.assertEqual(flatbug.from_ir(ir), data)
        ir["model"]["name"] = "edited"
        ir["extra_information"]["flatbug"]["native_extra"]["a"].append(2)
        self.assertEqual(metadata.model["name"], "Flatbug M_v2")
        self.assertEqual(data, before)

    def test_empty_outputs_and_no_invented_metadata(self):
        data = flatbug_sample()
        for name in ("boxes", "contours", "confs", "classes", "scales", "areas"):
            data[name] = []
        data.pop("identifier")
        ir = flatbug.to_ir(data)
        for key in ("model", "inference", "context"):
            self.assertNotIn(key, ir)
        self.assertEqual(ir["image"]["id"], data["image_path"])
        self.assertEqual(flatbug.from_ir(ir), data)
        batch = coco.to_ir({"images": [], "annotations": [], "categories": []})
        self.assertEqual(
            coco.from_ir(batch), {"images": [], "annotations": [], "categories": []}
        )

    def test_flatbug_rejects_misalignment_and_bad_geometry(self):
        for edit in (
            lambda d: d["confs"].clear(),
            lambda d: d["contours"][0][0].append(99),
            lambda d: d["boxes"][0].__setitem__(2, 0),
            lambda d: d.__setitem__("image_width", 0),
        ):
            data = flatbug_sample()
            edit(data)
            with self.assertRaises(FormatError):
                flatbug.to_ir(data)

    def test_mask_grid_area_remains_explicit(self):
        data = flatbug_sample()
        data["mask_width"] = 50
        data["mask_height"] = 40
        ir = flatbug.to_ir(data)
        self.assertNotIn("area", ir["instances"][0])
        self.assertEqual(
            ir["instances"][0]["extra_information"]["flatbug"]["mask_area"], 300
        )
        self.assertEqual(flatbug.from_ir(ir), data)

    def test_coco_roundtrip_retains_dataset_empty_images_and_extensions(self):
        data = coco_sample()
        before = deepcopy(data)
        batch = coco.to_ir(
            data,
            metadata=lambda image: Metadata(context={"group_name": str(image["id"])}),
        )
        self.assertEqual(len(batch.images), 2)
        self.assertEqual(batch.images[1]["instances"], [])
        self.assertEqual(
            batch.images[0]["instances"][0]["bbox"], [20.0, 45.0, 20.0, 30.0]
        )
        self.assertEqual(batch.images[1]["context"]["group_name"], "6")
        self.assertEqual(coco.from_ir(batch), data)
        batch.metadata["native_dataset"]["key"].append("new")
        self.assertEqual(data, before)

    def test_ir_edits_drive_export_and_nonzero_angle_rejected(self):
        batch = coco.to_ir(coco_sample())
        item = batch.images[0]["instances"][0]
        item["bbox"] = [40.0, 60.0, 10.0, 20.0]
        item["confidence"] = 0.5
        output = coco.from_ir(batch)["annotations"][0]
        self.assertEqual(output["bbox"], [35.0, 10.0, 10.0, 20.0])
        self.assertEqual(output["score"], 0.5)
        item["angle"] = 0.2
        with self.assertRaisesRegex(FormatError, "axis-aligned"):
            coco.from_ir(batch)
        item["angle"] = 0
        batch.images[0]["ir_id"] = 2
        with self.assertRaises(FormatError):
            coco.from_ir(batch)

    def test_rle_roundtrip_and_no_implicit_polygon_conversion(self):
        for counts in ("encoded-counts", [100, 20, 7880]):
            data = coco_sample()
            data["annotations"][0]["segmentation"] = {
                "size": [80, 100],
                "counts": counts,
            }
            data["annotations"][0]["iscrowd"] = 1
            batch = coco.to_ir(data)
            self.assertNotIn("polygons", batch.images[0]["instances"][0])
            self.assertEqual(coco.from_ir(batch), data)
            with self.assertRaisesRegex(FormatError, "polygons"):
                flatbug.from_ir(batch.images[0], scale=1)
            batch.images[0]["image"]["height"] = 90
            with self.assertRaisesRegex(FormatError, "RLE dimensions"):
                coco.from_ir(batch)

    def test_coco_references_duplicate_ids_and_malformed_polygons(self):
        edits = [
            lambda d: d["annotations"][0].__setitem__("image_id", 99),
            lambda d: d["annotations"][0].__setitem__("category_id", 99),
            lambda d: d["annotations"].append(deepcopy(d["annotations"][0])),
            lambda d: d["images"].append(deepcopy(d["images"][0])),
            lambda d: d["annotations"][0]["segmentation"][0].append(1),
            lambda d: d["annotations"][0].pop("bbox"),
            lambda d: d["annotations"][0].__setitem__("conf", 0.1),
        ]
        for edit in edits:
            data = coco_sample()
            edit(data)
            with self.assertRaises(FormatError):
                coco.to_ir(data)

    def test_cross_format_requires_explicit_identity_and_missing_values(self):
        ir = flatbug.to_ir(flatbug_sample())
        batch = coco.Batch([ir], {"categories": [{"id": 1, "name": "insect"}]})
        with self.assertRaisesRegex(FormatError, "image_ids"):
            coco.from_ir(batch)
        converted = coco.from_ir(batch, image_ids={"insect.jpg": 5})
        self.assertEqual(converted["annotations"][0]["bbox"], [10.0, 20.0, 20.0, 30.0])
        returned = coco.to_ir(converted).images[0]
        with self.assertRaisesRegex(FormatError, "scale"):
            flatbug.from_ir(returned)
        native = flatbug.from_ir(returned, scale=0.5)
        for key in ("boxes", "contours", "confs", "classes", "scales", "areas"):
            self.assertEqual(native[key], flatbug_sample()[key])
        returned["instances"][0].pop("confidence")
        with self.assertRaisesRegex(FormatError, "confidence"):
            flatbug.from_ir(returned, scale=0.5)
        self.assertEqual(
            flatbug.from_ir(returned, scale=0.5, confidence=0.25)["confs"], [0.25]
        )

    def test_multipart_polygons_are_preserved_but_not_collapsed(self):
        data = coco_sample()
        data["annotations"][0]["segmentation"].append([1, 2, 3, 4, 5, 6])
        batch = coco.to_ir(data)
        self.assertEqual(coco.from_ir(batch), data)
        with self.assertRaisesRegex(FormatError, "exactly one contour"):
            flatbug.from_ir(batch.images[0], scale=1)

    def test_real_probe_files_roundtrip(self):
        count = 0
        reports = ROOT / "src/probe/reports/2026-09-30"
        for directory in reports.glob("flatbug-*/samples/predictions"):
            for path in directory.rglob("metadata_*.json"):
                data = json.loads(path.read_text())
                with self.subTest(path=path):
                    self.assertEqual(flatbug.from_ir(flatbug.to_ir(data)), data)
                count += 1
            path = directory / "coco_instances.json"
            data = json.loads(path.read_text())
            with self.subTest(path=path):
                self.assertEqual(coco.from_ir(coco.to_ir(data)), data)
            count += 1
        self.assertEqual(count, 6)


if __name__ == "__main__":
    unittest.main()
