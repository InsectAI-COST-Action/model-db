"""Keep human-facing examples and runnable conversions consistent with schemas."""

import csv
from io import StringIO
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.formats import Schema  # noqa: E402


class FormatExampleTests(unittest.TestCase):
    def test_hugo_generates_format_pages_from_descriptors(self):
        hugo = ROOT / "bin/hugo"
        if not hugo.is_file():
            hugo = shutil.which("hugo")
        if not hugo:
            self.skipTest("Hugo is required to check generated format pages")
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "public"
            result = subprocess.run(
                [str(hugo), "--destination", str(destination),
                 "--cacheDir", str(Path(directory) / "cache"),
                 "--baseURL", "https://example.org/model-db/"],
                cwd=ROOT, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            index = (destination / "formats/index.html").read_text()
            for descriptor in (ROOT / "static/formats").glob("*.json"):
                with self.subTest(format=descriptor.stem):
                    page = destination / "formats" / descriptor.stem / "index.html"
                    html = page.read_text()
                    self.assertIn(f"<h1>{descriptor.stem}</h1>", html)
                    self.assertIn(f'href="/model-db/formats/{descriptor.stem}/"', index)
                    self.assertIn(f'href="/model-db/formats/{descriptor.name}"', html)
                    self.assertIn("<h2>Example</h2>", html)
                    self.assertEqual(
                        (destination / "formats" / descriptor.name).read_bytes(),
                        descriptor.read_bytes(),
                    )
            self.assertFalse(list((destination / "formats/detection").rglob("*.html")))

    def test_all_descriptors_have_a_valid_example(self):
        examples = json.loads((ROOT / "data/format_examples.json").read_text())
        paths = list((ROOT / "static/formats").glob("*.json"))
        self.assertEqual(set(examples), {p.stem for p in paths})
        for path in paths:
            with self.subTest(format=path.stem):
                example = examples[path.stem]
                schema = Schema.load(path)
                expected = schema.cast(example["value"])
                kind = example["representation"]
                if kind == "csv":
                    if "header" in example:
                        reader = csv.DictReader(StringIO(example["display"]))
                        decoded = list(reader)
                        self.assertEqual(reader.fieldnames, example["header"])
                    else:
                        decoded = list(csv.reader(StringIO(example["display"])))
                elif kind == "text":
                    decoded = [line.split() for line in example["display"].splitlines()]
                else:
                    decoded = json.loads(example["display"])
                self.assertEqual(schema.cast(decoded), expected)

    def test_runnable_examples_agree_on_geometry_and_image_boundaries(self):
        module = runpy.run_path(str(ROOT / "examples/formats/to_isir.py"))
        isir = Schema.load(ROOT / "static/formats/isir.json")
        for slug in module["SUPPORTED"]:
            with self.subTest(format=slug):
                value = module["convert_example"](slug)
                batch = value if isinstance(value, list) else [value]
                self.assertEqual(len(batch), 2 if slug == "coco" else 1)
                for record in batch:
                    isir.cast(record)
                self.assertEqual(len(batch[0]["instances"]), 1)
                self.assertEqual(batch[0]["instances"][0]["bbox"], [30, 60, 40, 40])
                if slug != "ami-detector-boxes":
                    self.assertEqual(batch[0]["instances"][0]["confidence"], .8)
                if slug == "coco":
                    self.assertEqual(batch[1]["instances"], [])
                if slug == "biomoth-csv":
                    self.assertNotIn("area", batch[0]["instances"][0])


if __name__ == "__main__":
    unittest.main()
