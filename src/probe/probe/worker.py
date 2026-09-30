"""One model environment per process. Never imported by the coordinator."""

from __future__ import annotations

import ast
from datetime import datetime
import importlib.metadata
import json
from pathlib import Path
import runpy
import shutil
import os
import csv
import zipfile
import subprocess
import sys


def main():
    request = json.loads(Path(sys.argv[1]).read_text())
    paths = {k: Path(v) for k, v in request["paths"].items()}
    out = Path(request["output"])
    out.mkdir(parents=True)
    import cv2
    import numpy as np
    import torch

    torch.set_num_threads(2)
    images = out / "inputs"
    images.mkdir()
    shutil.copyfile(paths["image"], images / "specimen.jpg")
    if "image_extra" in paths:
        shutil.copyfile(paths["image_extra"], images / "specimen_extra.jpg")
    cv2.imwrite(str(images / "blank.png"), np.full((640, 640, 3), 255, dtype=np.uint8))
    observation = {
        "status": "observed",
        "inference": "real checkpoint, CPU",
        "packages": {
            d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
        },
        "entrypoint": request["entrypoint"],
        "settings": request.get("settings", {}),
    }
    adapter = request["adapter"]
    if adapter == "ultralytics":
        from ultralytics import YOLO

        model = YOLO(str(paths["weights"]))
        results = model.predict(source=str(images), device="cpu")
        rows = []
        for r in results:
            rows.append(
                {
                    "image": Path(r.path).name,
                    "type": type(r).__module__ + "." + type(r).__qualname__,
                    "boxes_shape": list(r.boxes.data.shape),
                    "boxes_dtype": str(r.boxes.data.dtype),
                    "boxes": r.boxes.data.cpu().tolist(),
                    "orig_shape": list(r.orig_shape),
                    "has_masks": r.masks is not None,
                }
            )
        (out / "python-results.json").write_text(json.dumps(rows, indent=2) + "\n")
        observation.update(
            representation="ultralytics-detect-results",
            results=rows,
            note="Observed Python return object; this evidence JSON is written by the probe, not by the author API.",
        )
        if not any(r["boxes_shape"][0] for r in rows):
            observation["status"] = "inconclusive"
    elif adapter == "legacy-txt":
        source = paths["source"]
        sys.path.insert(0, str(source))
        # The authors use unpinned upstream CLI repositories; this probe pins the source.
        sys.argv = [
            str(source / "detect.py"),
            "--weights",
            str(paths["weights"]),
            "--source",
            str(images),
            "--img-size",
            "640",
            "--device",
            "cpu",
            "--conf-thres",
            str(request["settings"]["confidence"]),
            "--iou-thres",
            str(request["settings"]["iou"]),
            "--save-txt",
            "--save-conf",
            "--nosave",
            "--project",
            str(out / "predictions"),
            "--name",
            "result",
        ]
        if request["variant"].startswith("yolov5"):
            sys.argv += ["--max-det", "300"]
        observation["author_command"] = sys.argv.copy()
        runpy.run_path(str(source / "detect.py"), run_name="__main__")
        labels = []
        for p in sorted((out / "predictions").rglob("*.txt")):
            lines = [
                list(map(float, line.split()))
                for line in p.read_text().splitlines()
                if line.strip()
            ]
            if any(len(row) != 6 for row in lines):
                raise ValueError("Expected six author-selected text columns")
            labels.append(
                {
                    "file": str(p.relative_to(out)),
                    "rows": len(lines),
                    "sample": lines[:3],
                }
            )
        observation.update(
            representation=request["format"],
            files=labels,
            columns=["class", "center_x", "center_y", "width", "height", "confidence"],
        )
        if not any(f["rows"] for f in labels):
            observation["status"] = "inconclusive"
    elif adapter == "pollinator":
        # Pin the dependency the author otherwise fetches from mutable torch.hub HEAD.
        hub_load = torch.hub.load
        native = []

        def load(repo, name, *args, **kwargs):
            model = hub_load(
                str(paths["source"]), name, *args, source="local", **kwargs
            )

            class Capture:
                def __call__(self, image):
                    result = model(image)
                    native.append(
                        {
                            "type": type(result).__name__,
                            "shape": list(result.xyxy[0].shape),
                        }
                    )
                    return result

            return Capture()

        torch.hub.load = load
        image = cv2.imread(str(images / "specimen.jpg"))
        height, width = image.shape[:2]
        video = out / "fixture.avi"
        writer = cv2.VideoWriter(
            str(video), cv2.VideoWriter_fourcc(*"MJPG"), 2, (width, height)
        )
        if not writer.isOpened():
            raise RuntimeError("MJPG fixture writer unavailable")
        writer.write(image)
        writer.write(np.full_like(image, 255))
        writer.release()
        sys.argv = [
            str(paths["author_script"]),
            "--video",
            str(video),
            "--model",
            str(paths["weights"]),
            "--frame-interval",
            "0.5",
            "--output-dir",
            str(out / "predictions"),
            "--no-display",
        ]
        observation["author_command"] = sys.argv.copy()
        try:
            runpy.run_path(str(paths["author_script"]), run_name="__main__")
        finally:
            torch.hub.load = hub_load
        files = [
            str(p.relative_to(out))
            for p in sorted((out / "predictions").rglob("*.jpg"))
        ]
        if len(files) != 2 or len(native) != 2:
            raise RuntimeError("Author script did not process both video frames")
        observation.update(
            representation="pollinator-frame-folders",
            files=files,
            internal_results=native,
            branches_exercised=sorted({Path(f).parent.name for f in files}),
            note="Author script saves JPEG frames, annotated when detections pass its threshold. It does not export machine-readable boxes.",
        )
    elif adapter == "bjerge":
        source = paths["source"] / "yolov5"
        sys.path.insert(0, str(source))
        weight = out / "study.pt"
        with zipfile.ZipFile(paths["weights"]) as z:
            weight.write_bytes(z.read("YOLOv5models/insect1201-bestF1-1280v5s6.pt"))
        src = out / "2020" / "camera01" / "day01"
        src.mkdir(parents=True)
        for p in images.iterdir():
            target = src / p.name
            shutil.copyfile(p, target)
            os.utime(target, (1593604800, 1593604800))
        sys.argv = [
            str(source / "detectCSVNI2v2.py"),
            "--weights",
            str(weight),
            "--source",
            str(src) + "/",
            "--img-size",
            "1280",
            "--device",
            "cpu",
            "--save-txt",
            "--save-conf",
            "--nosave",
            "--project",
            str(out / "predictions"),
            "--name",
            str(out / "author-results"),
        ]
        observation["author_command"] = sys.argv.copy()
        runpy.run_path(str(source / "detectCSVNI2v2.py"), run_name="__main__")
        p = out / "author-results.csv"
        rows = list(csv.reader(p.open())) if p.exists() else []
        if any(len(row) != 11 for row in rows):
            raise ValueError("Unexpected CSV row width")
        observation.update(
            representation="insectsflowers-csv",
            rows=len(rows),
            sample=rows[:3],
            qualification="The provided author repository describes a later study; this verifies the supplied exporter/checkpoint combination, not its historical use in the 2023 paper.",
        )
        if not rows:
            observation["status"] = "inconclusive"
    elif adapter == "insectdct":
        source = out / "author-source"
        source.mkdir()
        for role, path in paths.items():
            if role.endswith(".py"):
                target = source / role
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        sys.path.insert(0, str(source))
        (out / "predictions").mkdir()
        models = out / "models_save"
        models.mkdir()
        with zipfile.ZipFile(paths["classifier"]) as z:
            for name in [
                "HierarchicalClassifier_CNB_V6.pth",
                "HierarchicalLabels3L_CNB_V6.pkl",
                "HierarchicalThresholds3S_CNB_V6.csv",
            ]:
                (models / name).write_bytes(z.read(name))
        sequence = out / "sequence"
        sequence.mkdir()
        for role, path in paths.items():
            if role.startswith("frame:"):
                shutil.copyfile(path, sequence / role.removeprefix("frame:"))
        sys.argv = [
            str(source / "pipeDetectAndClassifyInsectsTaxon.py"),
            "--device",
            "cpu",
            "--images",
            str(sequence) + "/",
            "--resultsDir",
            str(out / "predictions"),
            "--yoloWeights",
            str(paths["weights"]),
            "--moviePredict",
            "",
            "--hierachical",
            str(models / "HierarchicalClassifier_CNB_V6.pth"),
            "--labels",
            str(models / "HierarchicalLabels3L_CNB_V6.pkl"),
            "--thresholds",
            str(models / "HierarchicalThresholds3S_CNB_V6.csv"),
        ]
        observation["author_command"] = sys.argv.copy()
        runpy.run_path(
            str(source / "pipeDetectAndClassifyInsectsTaxon.py"), run_name="__main__"
        )
        files = []
        for p in (out / "predictions").glob("*.csv"):
            rows = list(csv.reader(p.open()))
            files.append(
                {
                    "file": str(p.relative_to(out)),
                    "header": rows[0] if rows else [],
                    "rows": len(rows) - 1,
                    "sample": rows[1:3],
                }
            )
        observation.update(representation="insectdct-csv", files=files)
        if not any(f["rows"] > 0 for f in files):
            observation["status"] = "inconclusive"
    elif adapter == "beetleflow":
        model_dir = out / "model"
        model_dir.mkdir()
        shutil.copyfile(paths["weights"], model_dir / "model.safetensors")
        shutil.copyfile(paths["config"], model_dir / "config.json")
        beetles = out / "batch" / "fixture" / "single_beetles"
        beetles.mkdir(parents=True)
        shutil.copyfile(paths["image"], beetles / "specimen.png")
        command = [
            sys.executable,
            str(paths["author_script"]),
            "--model",
            str(model_dir),
            "--input_dir",
            str(out / "batch"),
            "--output_dir",
            str(out / "predictions"),
            "--device",
            "cpu",
        ]
        observation["author_command"] = command
        subprocess.run(command, check=True)
        files = []
        for p in sorted((out / "predictions").rglob("*.png")):
            im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
            files.append(
                {
                    "file": str(p.relative_to(out)),
                    "shape": list(im.shape),
                    "dtype": str(im.dtype),
                    "colors_bgr": np.unique(im.reshape(-1, 3), axis=0).tolist()
                    if "predicted_masks/" in str(p)
                    else None,
                }
            )
        if len(files) != 2:
            raise RuntimeError("Author CLI did not emit both mask and overlay")
        observation.update(
            representation="beetleflow-color-mask",
            files=files,
            note="Author exporter writes a palette-colored image and additive overlay, not the internal integer class map. Output extension follows input; JPEG is lossy.",
        )
    elif adapter == "morpho":
        source = paths["source"]
        command = [
            sys.executable,
            str(source / "utils/ultimate_headless.py"),
            "--input",
            str(source / "img/test"),
            "--output",
            str(out / "predictions"),
            "--analysis-type",
            "both",
            "--workers",
            "1",
            "--chunk-size",
            "1",
            "--fail-on-error",
        ]
        observation["author_command"] = command
        subprocess.run(command, cwd=source, check=True)
        files = []
        for p in sorted((out / "predictions").rglob("*results_final.csv")):
            rows = list(csv.reader(p.open()))
            files.append(
                {
                    "file": str(p.relative_to(out)),
                    "columns": rows[0],
                    "rows": len(rows) - 1,
                    "sample": rows[1:2],
                }
            )
        if len(files) != 2:
            raise RuntimeError(
                "Expected both Rapid Scan and Detailed Analysis CSV outputs"
            )
        observation.update(representation="insectmorphoai-csv", files=files)
        if any(f["rows"] == 0 for f in files):
            observation["status"] = "inconclusive"
    elif adapter == "moths":
        source = paths["source"]
        weights = out / "insectMoths-bestF1-1280m6.pt"
        with zipfile.ZipFile(paths["weights"]) as z:
            weights.write_bytes(z.read(weights.name))
        sequence = out / "2024" / "trap01" / "night"
        sequence.mkdir(parents=True)
        shutil.copyfile(source / "InsectImage2.jpg", sequence / "20240501010000.jpg")
        command = [
            sys.executable,
            str(source / "detectClassifySpecies.py"),
            "--weights",
            str(weights),
            "--result",
            str(out / "predictions"),
            "--img",
            "1280",
            "--conf",
            "0.20",
            "--nosave",
            "--device",
            "cpu",
            "--source",
            str(sequence) + "/",
        ]
        observation["author_command"] = command
        subprocess.run(command, cwd=source, check=True)
        files = []
        for p in sorted(out.rglob("*.csv")):
            rows = list(csv.reader(p.open()))
            files.append(
                {
                    "file": str(p.relative_to(out)),
                    "columns": rows[0] if rows else [],
                    "rows": len(rows) - 1,
                    "sample": rows[1:2],
                }
            )
        observation.update(representation="mcc24-csv", files=files)
        if not any(f["rows"] > 0 for f in files):
            observation["status"] = "inconclusive"
    elif adapter == "biomoth":
        import pandas as pd
        from torchvision.ops import nms

        notebook = json.loads(paths["author_script"].read_text())
        code = "\n".join(
            "".join(cell["source"]) for cell in notebook["cells"]
            if cell["cell_type"] == "code"
        )
        # Execute original function bodies, excluding notebook-local paths and UI cells.
        definitions = ast.Module(
            body=[node for node in ast.parse(code).body if isinstance(node, ast.FunctionDef)],
            type_ignores=[],
        )
        namespace = dict(np=np, pd=pd, torch=torch, nms=nms, cv2=cv2, os=os,
                         IMG_SIZE=640, CONF_THRES=0.25, IOU_THRES=0.50,
                         DEVICE="cpu", IMAGE_FOLDER=str(out), LOCATIONS=["inputs"],
                         CSV=str(out / "predictions_2023.csv"),
                         model=torch.jit.load(str(paths["weights"]), map_location="cpu").eval())
        exec(compile(definitions, str(paths["author_script"]), "exec"), namespace)
        namespace["batch_process"]()
        with (out / "predictions_2023.csv").open() as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            header = reader.fieldnames
        observation.update(representation="biomoth-csv", header=header, rows=len(rows),
                           counts_by_image={p.name: sum(r["fileName"] == p.name for r in rows)
                                            for p in sorted(images.iterdir())},
                           settings=dict(img_size=640, confidence=0.25, iou=0.50),
                           note="Original batch_process and helpers; fixed author year/calibration preserved. Fixtures are not an accuracy or physical calibration test.")
        if not rows:
            observation["status"] = "inconclusive"
    elif adapter == "mothbot":
        from ultralytics import YOLO

        namespace = dict(np=np, cv2=cv2, os=os, json=json, datetime=datetime,
                         GEN_THUMBNAILS=True)
        for resource, name in [("common", "current_timestamp"), ("author_script", "_save_result")]:
            tree = ast.parse(paths[resource].read_text())
            definition = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            exec(compile(ast.Module(body=[definition], type_ignores=[]),
                         str(paths[resource]), "exec"), namespace)
        model = YOLO(str(paths["weights"]))
        records = []
        for p in sorted(images.iterdir()):
            result = model.predict(source=cv2.imread(str(p)), device="cpu", verbose=False,
                                   imgsz=1600, max_det=10000)[0]
            destination = out / (p.stem + "_botdetection.json")
            shapes, _ = namespace["_save_result"](result, str(p), str(destination), "MBD-1-1")
            records.append(dict(file=destination.name, instances=len(shapes)))
        observation.update(representation="mothbot-detection-json", files=records,
                           settings=dict(img_size=1600, max_det=10000, gen_thumbnails=True),
                           note="Original author JSON writer on real OBB predictions. Thumbnail filenames are recorded but thumbnails and optional blur enrichment are not produced; GUI/classification/tracking excluded.")
        if not any(r["instances"] for r in records):
            observation["status"] = "inconclusive"
    elif adapter == "flatbug":
        sys.argv = [
            "fb_predict",
            "-i",
            str(images),
            "-o",
            str(out / "predictions"),
            "-w",
            str(paths["weights"]),
            "-g",
            "cpu",
        ]
        observation["author_command"] = sys.argv.copy()
        ep = next(
            e
            for e in importlib.metadata.entry_points(group="console_scripts")
            if e.name == "fb_predict"
        )
        ep.load()()
        records = []
        for p in sorted((out / "predictions").rglob("*.json")):
            value = json.loads(p.read_text())
            records.append(
                {
                    "file": str(p.relative_to(out)),
                    "keys": sorted(value) if isinstance(value, dict) else None,
                    "instances": len(value["boxes"])
                    if isinstance(value, dict) and "boxes" in value
                    else None,
                    "contour_shape": [
                        len(value["contours"][0]),
                        len(value["contours"][0][0]),
                    ]
                    if isinstance(value, dict) and value.get("contours")
                    else None,
                }
            )
        if not records:
            raise RuntimeError("No JSON output from author CLI")
        observation.update(
            representation="flatbug",
            files=records,
            note="Default author CLI emits per-image JSON plus compiled COCO and visual/crop artifacts.",
        )
        if not any(r["instances"] for r in records):
            observation["status"] = "inconclusive"
    else:
        raise ValueError("Unknown adapter " + adapter)
    (out / "observed.json").write_text(json.dumps(observation, indent=2) + "\n")


if __name__ == "__main__":
    main()
