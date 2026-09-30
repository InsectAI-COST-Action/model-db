import json
from pathlib import Path
import tempfile
import unittest
import sys
import os
import zipfile

from probe.runner import ROOT, digest, fetch, run_job, unpack, execute


class RunnerTests(unittest.TestCase):
    def test_download_hash_failure_never_populates_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.write_bytes(b"checkpoint")
            resource = {
                "url": source.as_uri(),
                "filename": "model.pt",
                "sha256": "0" * 64,
            }
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                fetch(resource, root / "cache")
            self.assertFalse(list((root / "cache").rglob("*.partial")))
            resource["sha256"] = digest(source)
            cached = fetch(resource, root / "cache")
            self.assertEqual(cached.read_bytes(), b"checkpoint")
            cached.write_bytes(b"corrupted")
            self.assertEqual(
                fetch(resource, root / "cache").read_bytes(), b"checkpoint"
            )

    def test_archive_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with zipfile.ZipFile(root / "bad.zip", "w") as z:
                z.writestr("../escape", "bad")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                unpack(root / "bad.zip", root / "out")
            self.assertFalse((root / "escape").exists())

    def test_blocked_run_is_not_an_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = run_job(
                {
                    "id": "unavailable",
                    "model": "model",
                    "scope": "full workflow",
                    "author_sources": ["https://example.org/source"],
                    "blocked": "Missing weights",
                },
                {},
                root,
                root / "cache",
                1,
            )
            self.assertEqual(report["status"], "blocked")
            self.assertNotIn("observation", report)
            self.assertEqual(
                json.loads((root / "unavailable/report.json").read_text()), report
            )

    def test_timeout_terminates_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(TimeoutError, "terminated"):
                execute(
                    [sys.executable, "-c", "import time; time.sleep(10)"],
                    root,
                    dict(os.environ),
                    root / "log",
                    0.05,
                )

    def test_inventory_covers_every_detection_card(self):
        import tomllib

        jobs = json.loads((ROOT / "models.json").read_text())
        cards = []
        for card in (ROOT.parents[1] / "content/models").glob("*/index.md"):
            metadata = tomllib.loads(card.read_text().split("+++")[1])
            if metadata.get("category") == "detection":
                cards.append(card.parent.name)
        self.assertLessEqual(set(cards), {j["model"] for j in jobs})
        self.assertEqual(len(jobs), len({j["id"] for j in jobs}))

    def test_resources_are_pinned(self):
        resources = json.loads((ROOT / "resources.json").read_text())
        for key, value in resources.items():
            with self.subTest(resource=key):
                self.assertRegex(value["sha256"], r"^[0-9a-f]{64}$")
                self.assertNotIn("error", value)
                self.assertGreater(value["bytes"], 0)


if __name__ == "__main__":
    unittest.main()
