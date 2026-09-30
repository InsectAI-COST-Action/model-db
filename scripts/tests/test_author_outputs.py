"""Validate profiles against retained outputs from real author checkpoints."""

import csv
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.formats import Schema  # noqa: E402

REPORTS = ROOT / "src/probe/reports/2026-09-30-format-expansion"
FORMATS = ROOT / "static/formats/detection"


class AuthorOutputTests(unittest.TestCase):
    def test_biomoth_csv_casts_real_cells_and_preserves_column_order(self):
        schema = Schema.load(FORMATS / "biomoth-csv.json")
        with (REPORTS / "biomoth/artifacts/predictions_2023.csv").open() as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            self.assertEqual(reader.fieldnames, schema.notes["header"])
        decoded = schema.cast(rows)
        self.assertEqual(len(decoded), 32)
        self.assertEqual({row["class"] for row in decoded}, {0})
        self.assertEqual({row["fileName"] for row in decoded}, {"specimen.jpg"})
        # Writer emits a decimal class cell despite the integer-valued vocabulary.
        self.assertEqual(rows[0]["class"], "0.0")
        self.assertIs(type(decoded[0]["class"]), int)
        self.assertIs(type(decoded[0]["X_Min"]), float)

    def test_mothbot_populated_and_empty_author_json(self):
        schema = Schema.load(FORMATS / "mothbot-detection-json.json")
        for name, count in [("specimen", 15), ("blank", 0)]:
            with self.subTest(image=name):
                data = json.loads((REPORTS / f"mothbot/artifacts/{name}_botdetection.json").read_text())
                self.assertEqual(schema.cast(data), data)
                self.assertEqual(len(data["shapes"]), count)
                for shape in data["shapes"]:
                    self.assertEqual(shape["score"], shape["confidence_detection"])
                    self.assertEqual(shape["difficult"], "false")
                    self.assertEqual(len(shape["points"]), 4)
                    self.assertNotIn("blur_score", shape)

    def test_mothbot_metadata_defaults_do_not_constrain_string_contents(self):
        schema = Schema.load(FORMATS / "mothbot-detection-json.json")
        data = json.loads((REPORTS / "mothbot/artifacts/specimen_botdetection.json").read_text())
        # Initialization defaults must not reject subsequently populated metadata.
        data["description"] = "Light-trap image"
        data["shapes"][0].update(
            description="Reviewed detection",
            label="Lepidoptera",
            difficult="true",
            identifier_bot="classifier-name",
            identifier_human="reviewer-name",
        )
        self.assertEqual(schema.cast(data), data)

    def test_retained_artifacts_match_runtime_receipts(self):
        for name in ["biomoth", "mothbot"]:
            report = json.loads((REPORTS / name / "report.json").read_text())
            self.assertEqual(report["status"], "observed")
            by_path = {entry["path"]: entry for entry in report["artifacts"]}
            for path in (REPORTS / name / "artifacts").iterdir():
                with self.subTest(probe=name, artifact=path.name):
                    entry = by_path[str(path.relative_to(REPORTS / name))]
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])
                    self.assertEqual(path.stat().st_size, entry["bytes"])


if __name__ == "__main__":
    unittest.main()
