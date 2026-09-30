"""Import semantics: image boundaries, explicit layouts and preserved evidence."""

from copy import deepcopy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.formats import FormatError  # noqa: E402
from iai_model_zoo.formats.adapters import (  # noqa: E402
    ImageContext, Metadata, ami, biomoth, ultralytics, yolo_txt,
)


class DetectionImportTests(unittest.TestCase):
    def setUp(self):
        self.image = ImageContext("capture", 200, 100, "site/frame.jpg",
                                  Metadata(model={"name": "known model"}))

    def test_ami_geometry_missing_metadata_and_copying(self):
        boxes = [[10, 20, 50, 60]]
        ir = ami.to_ir(boxes, image=self.image)
        self.assertEqual(ir["instances"], [dict(id=0, bbox=[30, 60, 40, 40])])
        self.assertEqual(ir["model"], {"name": "known model"})
        self.assertNotIn("inference", ir)
        ir["model"]["name"] = "edited"
        self.assertEqual(self.image.metadata.model["name"], "known model")
        self.assertEqual(boxes, [[10, 20, 50, 60]])
        with self.assertRaises(FormatError):
            ami.to_ir([[50, 20, 10, 60]], image=self.image)
        with self.assertRaises(FormatError):
            ami.to_ir([[10.5, 20, 50, 60]], image=self.image)

    def test_manifest_identity_unknown_images_and_explicit_empty_policy(self):
        images = {"a": self.image, "b": ImageContext("empty", 10, 20)}
        inputs = {"a": [[10, 20, 50, 60]]}
        self.assertEqual(len(ami.to_ir_many(inputs, images=images)), 1)
        batch = ami.to_ir_many(inputs, images=images, include_empty=True)
        self.assertEqual([r["image"]["id"] for r in batch], ["capture", "empty"])
        self.assertEqual(batch[1]["instances"], [])
        self.assertEqual(len(ami.to_ir_many({"b": []}, images=images)), 1)
        with self.assertRaisesRegex(FormatError, "missing from manifest"):
            ami.to_ir_many({"unknown": []}, images=images)
        with self.assertRaisesRegex(FormatError, "duplicate"):
            ami.to_ir_many({}, images={"a": self.image, "b": self.image})
        with self.assertRaises(FormatError):
            ami.to_ir([], image=ImageContext("bad", 0, 100))

    def test_all_detection_txt_profiles_and_corner_variant(self):
        for profile in yolo_txt.PROFILES:
            ir = yolo_txt.to_ir("2 .25 .3 .2 .4 .8\n", image=self.image,
                                profile=profile, save_conf=True)
            self.assertEqual(ir["instances"][0], dict(
                id=0, bbox=[50, 70, 40, 40], category_id=2, confidence=.8))
        ir = yolo_txt.to_ir("2 .15 .1 .35 .5", image=self.image,
                            profile="yolov5-detect-txt", save_conf=False, save_format=1)
        self.assertEqual(ir["instances"][0]["bbox"], [50, 70, 40, 40])
        self.assertNotIn("confidence", ir["instances"][0])

    def test_txt_tracking_layout_is_never_guessed_from_integer_sixth_column(self):
        args = dict(image=self.image, profile="ultralytics-detect-txt")
        text = "0 .25 .3 .2 .4 1"
        tracked = yolo_txt.to_ir(text, save_conf=False, tracking=True, **args)["instances"][0]
        self.assertNotIn("confidence", tracked)
        self.assertEqual(tracked["extra_information"]["ultralytics-detect-txt"]["track_id"], 1)
        scored = yolo_txt.to_ir(text, save_conf=True, **args)["instances"][0]
        self.assertEqual(scored["confidence"], 1)
        with self.assertRaises(FormatError):
            yolo_txt.to_ir(text, save_conf=False, **args)
        for text in ["0 0 0 1 1 nan", "0 0 0 -1 1 .8", "0.5 0 0 1 1 .8"]:
            with self.assertRaises(FormatError):
                yolo_txt.to_ir(text, save_conf=True, **args)
        with self.assertRaises(FormatError):
            yolo_txt.to_ir("", image=self.image, profile="yolov7-detect-txt",
                           save_conf=False, tracking=True)

    def test_txt_collection_keeps_explicit_empty_images(self):
        records = yolo_txt.to_ir_many({"a": "", "b": "0 .5 .5 .2 .2"},
            images={"a": self.image, "b": ImageContext("second", 100, 50)},
            profile="yolov5-detect-txt", save_conf=False)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["instances"], [])
        self.assertEqual(records[1]["instances"][0]["bbox"], [50, 25, 20, 10])

    def test_ultralytics_json_modes_native_extras_and_empty_image(self):
        data = [dict(name="insect", **{"class": 3}, confidence=.8, track_id=7,
                     box=dict(x1=.05, y1=.2, x2=.25, y2=.6), custom="retained")]
        saved = deepcopy(data)
        ir = ultralytics.json_to_ir(data, image=self.image, normalized=True)
        self.assertEqual(ir["instances"][0]["bbox"], [30, 60, 40, 40])
        self.assertEqual(ir["instances"][0]["extra_information"]["ultralytics"],
                         dict(name="insect", track_id=7, custom="retained"))
        self.assertEqual(data, saved)
        data[0]["box"] = dict(x1=10, y1=20, x2=50, y2=60)
        pixels = ultralytics.json_to_ir(json.dumps(data), image=self.image, normalized=False)
        self.assertEqual(pixels["instances"], ir["instances"])
        self.assertEqual(saved[0]["box"]["x1"], .05)
        self.assertEqual(ultralytics.json_to_ir("[]", image=self.image,
                                              normalized=False)["instances"], [])
        batch = ultralytics.json_to_ir_many({"a": []}, images={"a": self.image}, normalized=False)
        self.assertEqual(len(batch), 1)
        data[0]["segments"] = {"x": [], "y": []}
        with self.assertRaises(FormatError):
            ultralytics.json_to_ir(data, image=self.image, normalized=False)

    def test_results_projection_dimensions_tracking_and_batches(self):
        source = dict(orig_shape=[100, 200], path="source.jpg", names={3: "insect"},
                      boxes=dict(data=[[10, 20, 50, 60, 7, .8, 3]]))
        ir = ultralytics.to_ir(source, image=self.image)
        self.assertEqual(ir["instances"][0]["bbox"], [30, 60, 40, 40])
        self.assertEqual(ir["instances"][0]["extra_information"]["ultralytics"]["track_id"], 7)
        self.assertEqual(ir["extra_information"]["ultralytics"]["names"], {3: "insect"})
        with self.assertRaisesRegex(FormatError, "dimensions"):
            ultralytics.to_ir(source, image=ImageContext("x", 100, 200))
        with self.assertRaisesRegex(FormatError, "duplicate"):
            ultralytics.to_ir_many([source, source])
        batch = ultralytics.to_ir_many(iter([source, source]), images=[
            self.image, ImageContext("other", 200, 100)])
        self.assertEqual(len(batch), 2)
        with self.assertRaisesRegex(FormatError, "different lengths"):
            ultralytics.to_ir_many([source], images=[])
        source["masks"] = {}
        with self.assertRaises(FormatError):
            ultralytics.to_ir(source)

    def test_native_results_projection_without_model_dependencies(self):
        class Tensor:
            def detach(self): return self
            def cpu(self): return self
            def tolist(self): return [[10, 20, 50, 60, .8, 0]]
        result = SimpleNamespace(orig_shape=(100, 200), path="source.jpg",
                                 names={0: "insect"}, boxes=SimpleNamespace(data=Tensor()))
        ir = ultralytics.to_ir(result)
        self.assertEqual(ir["image"]["id"], "source.jpg")
        self.assertEqual(ir["instances"][0]["category_id"], 0)
        self.assertEqual(ir["instances"][0]["bbox"], [30, 60, 40, 40])

    def test_biomoth_real_csv_measurements_and_empty_manifest_images(self):
        path = ROOT / "src/probe/reports/2026-09-30-format-expansion/biomoth/artifacts/predictions_2023.csv"
        # Dimensions are explicit fixture context, not inferred from detections.
        images = {"inputs/specimen.jpg": ImageContext("specimen", 1940, 1933),
                  "inputs/blank.png": ImageContext("blank", 640, 640)}
        batch = biomoth.to_ir(path.read_text(), images=images, include_empty=True)
        self.assertEqual([len(r["instances"]) for r in batch], [32, 0])
        instance = batch[0]["instances"][0]
        self.assertEqual(batch[0]["image"]["file_name"], "inputs/specimen.jpg")
        self.assertNotIn("area", instance)
        native = instance["extra_information"]["biomoth"]
        self.assertEqual(native["size"], 3.027573)
        self.assertEqual(native["year"], 2023)
        self.assertEqual(instance["category_id"], 0)
        self.assertAlmostEqual(instance["bbox"][0], 1138.37955)
        self.assertAlmostEqual(instance["bbox"][1], 1807.204035)
        self.assertEqual(len(biomoth.to_ir(path.read_text(), images=images)), 1)
        with self.assertRaises(FormatError):
            biomoth.to_ir(path.read_text(), images={})
        with self.assertRaisesRegex(FormatError, "row length"):
            biomoth.to_ir(path.read_text().splitlines()[0] + "\na,b\n", images=images)
        with self.assertRaises(FormatError):
            biomoth.to_ir("fileName,confidence\na.jpg,.9\n", images={})

    def test_biomoth_groups_full_paths_not_basenames(self):
        template = {name: "0" for name in biomoth.schema("biomoth-csv").notes["header"]}
        template.update(fileName="same.jpg", site="a", X_Max="20", Y_Max="10")
        rows = [{**template, "filePath": f"{site}/same.jpg"} for site in ["a", "b"]]
        images = {f"{site}/same.jpg": ImageContext(site, 100, 100) for site in ["a", "b"]}
        batch = biomoth.to_ir(rows, images=images)
        self.assertEqual([r["image"]["id"] for r in batch], ["a", "b"])
        self.assertEqual([len(r["instances"]) for r in batch], [1, 1])

    def test_retained_txt_and_results_observations(self):
        root = ROOT / "src/probe/reports/2026-09-30"
        path = next((root / "stark-yolov5_s/samples").rglob("*.txt"))
        ir = yolo_txt.to_ir(path.read_text(), image=ImageContext("specimen", 1940, 1933),
                            profile="yolov5-detect-txt", save_conf=True)
        self.assertGreater(len(ir["instances"]), 0)
        receipt = json.loads((root / "arthronat/report.json").read_text())
        for result in receipt["observation"]["results"]:
            # Receipt stores the observed tensors, not the complete Results object.
            projection = dict(orig_shape=result["orig_shape"], path=result["image"],
                              names={}, boxes=dict(data=result["boxes"]))
            ir = ultralytics.to_ir(projection)
            self.assertEqual(len(ir["instances"]), result["boxes_shape"][0])


if __name__ == "__main__":
    unittest.main()
