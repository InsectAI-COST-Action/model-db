"""One image + local horizontal-detection checkpoint -> one ISIR JSON record.

Run in src/probe/environments/modern's locked uv environment. This is a minimal
inference route, not a replacement for specialized preprocessing/classification.
"""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--model-name", required=True, help="Explicit registry/user model identity")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.7)
    args = parser.parse_args()
    for path in (args.weights, args.image):
        if not path.is_file():
            parser.error(f"Local file does not exist: {path}")
    from iai_model_zoo.formats.adapters import ImageContext, Metadata, ultralytics

    # Route any library notices to stderr so stdout remains a single JSON record.
    from contextlib import redirect_stdout
    with redirect_stdout(sys.stderr):
        from ultralytics import YOLO
        import torch

        torch.set_num_threads(2)
        model = YOLO(str(args.weights))
        if model.task != "detect":
            parser.error("This example supports horizontal detection only, not OBB/segmentation/classification")
        result = model.predict(str(args.image), device="cpu", imgsz=args.imgsz,
                               conf=args.conf, iou=args.iou, verbose=False)[0]
    height, width = result.orig_shape
    context = ImageContext(
        id=str(args.image), width=width, height=height, file_name=str(args.image),
        metadata=Metadata(model={"name": args.model_name}, inference={"config": {
            "device": "cpu", "imgsz": args.imgsz, "conf": args.conf, "iou": args.iou,
        }}),
    )
    print(json.dumps(ultralytics.to_ir(result, image=context), indent=2))


if __name__ == "__main__":
    main()
