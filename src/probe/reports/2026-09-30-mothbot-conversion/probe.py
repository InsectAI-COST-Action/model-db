"""Local cached MBD-1-1 -> native Results -> ISIR/COCO; no downloads."""
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'src'))
from iai_model_zoo.formats import Converter, ConversionContext
from iai_model_zoo.formats.adapters import ImageContext
import numpy as np
import cv2
import torch
import ultralytics
from ultralytics import YOLO

torch.set_num_threads(2)
weights=ROOT/'src/probe/.cache/aa7e881e532d49be305d275766cd73fda0d75a8853d7bf822fc2c8a1e873e44a/MBD-1-1.pt'
image=ROOT/'src/probe/.cache/0646bc669e2f9c0d2f86d502bf0caec50732b63c9ad8819c389f86a0c1750627/image.jpg'
assert hashlib.sha256(weights.read_bytes()).hexdigest()==weights.parent.name
assert hashlib.sha256(image.read_bytes()).hexdigest()==image.parent.name
model=YOLO(str(weights)); converter=Converter.open(ROOT)
records=[]
for i,(name,pixels) in enumerate([('specimen',cv2.imread(str(image))),('blank',np.full((640,640,3),255,np.uint8))],1):
    start=time.monotonic()
    result=model.predict(pixels,device='cpu',verbose=False,imgsz=1600,max_det=10000,conf=.25,iou=.7)[0]
    context=ConversionContext(image=ImageContext(i,pixels.shape[1],pixels.shape[0],name+'.jpg'))
    ir=converter.convert(result,source='ultralytics-obb-results',context=context)
    coco=converter.convert(result,source='ultralytics-obb-results',target='coco',context=context)
    assert len(ir['instances'])==len(result.obb.conf)==len(coco['annotations'])
    for annotation,corners in zip(coco['annotations'],result.obb.xyxyxyxy.tolist()):
        expected=[v for p in corners for v in p]
        assert max(abs(a-b) for a,b in zip(annotation['segmentation'][0],expected))<1e-6
    projection=dict(orig_shape=list(result.orig_shape),path=result.path,names=result.names,
                    obb=dict(xyxyxyxy=result.obb.xyxyxyxy.tolist(),conf=result.obb.conf.tolist(),cls=result.obb.cls.tolist(),data=result.obb.data.tolist()))
    Path(__file__).with_name(name+'-results.json').write_text(json.dumps(projection,indent=2)+'\n')
    records.append(dict(image=name,detections=len(ir['instances']),seconds=time.monotonic()-start))
report=dict(weights_sha256=weights.parent.name,image_sha256=image.parent.name,ultralytics=ultralytics.__version__,torch=torch.__version__,settings=dict(device='cpu',imgsz=1600,max_det=10000,conf=.25,iou=.7),results=records,scope='Direct OBB inference and conversion; excludes author writer, thumbnails, classification and UI; not an accuracy benchmark.')
Path(__file__).with_name('report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
