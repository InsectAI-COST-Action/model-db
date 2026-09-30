"""Convert a documented illustrative example to ISIR without model dependencies."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.formats.adapters import (  # noqa: E402
    ImageContext, ami, biomoth, coco, flatbug, ultralytics, yolo_txt,
)

SUPPORTED = sorted(yolo_txt.PROFILES | {
    "ami-detector-boxes", "biomoth-csv", "coco", "flatbug",
    "ultralytics-detect-results", "ultralytics-detect-json",
})


def convert_example(slug):
    entry = json.loads((ROOT / "data/format_examples.json").read_text())[slug]
    image = ImageContext("frame-1", 200, 100, "frame.jpg")
    if slug in yolo_txt.PROFILES:
        return yolo_txt.to_ir(entry["display"], image=image, profile=slug, save_conf=True)
    if slug == "ami-detector-boxes":
        return ami.to_ir(entry["value"], image=image)
    if slug == "biomoth-csv":
        return biomoth.to_ir(entry["display"], images={"site/frame.jpg": image})
    if slug == "ultralytics-detect-json":
        return ultralytics.json_to_ir(entry["value"], image=image, normalized=False)
    if slug == "ultralytics-detect-results":
        return ultralytics.to_ir(entry["value"], image=image)
    if slug == "flatbug":
        return flatbug.to_ir(entry["value"], image_id=image.id)
    if slug == "coco":
        return coco.to_ir(entry["value"]).images
    raise ValueError(f"No example converter for {slug}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("format", choices=SUPPORTED)
    args = parser.parse_args()
    print(json.dumps(convert_example(args.format), indent=2))
