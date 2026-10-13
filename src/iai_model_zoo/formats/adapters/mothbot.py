"""Mothbot detection JSON and Ultralytics OBB outputs -> polygon-preserving ISIR."""
from collections.abc import Mapping
from copy import deepcopy
import math

from ..schema import FormatError
from ._common import record, schema, flip_polygon
from ._inputs import ImageContext, xyxy_to_ir
from .ultralytics import _list


def _instance(points, confidence, identity, image, native):
    # Ordered convex quadrilateral: reject crossed/degenerate outlines instead
    # of silently making their envelope appear to be a valid oriented detection.
    crosses = []
    for i in range(4):
        a,b,c = points[i],points[(i+1)%4],points[(i+2)%4]
        crosses.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
    if not (all(v > 0 for v in crosses) or all(v < 0 for v in crosses)):
        raise FormatError('mothbot: corners must form a nondegenerate convex quadrilateral')
    if not 0 <= confidence <= 1:
        raise FormatError('mothbot: detection confidence must be in [0,1]')
    p0,p1,p2,p3 = points
    dx,dy = p1[0]-p0[0],p1[1]-p0[1]
    ex,ey = p2[0]-p1[0],p2[1]-p1[1]
    width,height = math.hypot(dx,dy),math.hypot(ex,ey)
    tolerance = max(width,height,1) * 1e-4
    if (abs(dx*ex+dy*ey) > width*height*1e-4
        or abs(p0[0]+p2[0]-p1[0]-p3[0]) > tolerance
        or abs(p0[1]+p2[1]-p1[1]-p3[1]) > tolerance):
        raise FormatError('mothbot: corners do not describe a rectangle')
    cx,cy = sum(p[0] for p in points)/4,sum(p[1] for p in points)/4
    return dict(id=identity, bbox=[cx,image['height']-cy,width,height],
                angle=math.atan2(-dy,dx),
                polygons=[flip_polygon(points,image['height'])], confidence=confidence,
                extra_information=native)



def to_ir(data, *, image=None):
    data = schema('mothbot-detection-json').cast(data)
    if image is None:
        if not data['imagePath']:
            raise FormatError('mothbot: supply image context when imagePath is empty')
        image = ImageContext(data['imagePath'],data['imageWidth'],data['imageHeight'],data['imagePath'])
    info = image.image()
    if (info['width'],info['height']) != (data['imageWidth'],data['imageHeight']):
        raise FormatError('mothbot: dimensions disagree with image context')
    info.setdefault('file_name',data['imagePath'])
    instances = [_instance(s['points'],s['confidence_detection'],i,info,{'mothbot':deepcopy(s)})
                 for i,s in enumerate(data['shapes'])]
    return record(info,instances,image.metadata,{'mothbot':{k:v for k,v in data.items() if k!='shapes'}})


def obb_to_ir(result, *, image=None):
    if isinstance(result, Mapping):
        data = deepcopy(dict(result))
    else:
        if getattr(result,'obb',None) is None:
            raise FormatError('mothbot: Results.obb is required, including empty detections')
        obb=result.obb
        data=dict(orig_shape=_list(result.orig_shape),path=result.path,names=deepcopy(result.names),
                  obb=dict(xyxyxyxy=_list(obb.xyxyxyxy),conf=_list(obb.conf),cls=_list(obb.cls),
                           data=_list(obb.data)))
    data=schema('ultralytics-obb-results').cast(data)
    height,width=data['orig_shape']
    if image is None:
        if not data['path']:
            raise FormatError('mothbot: supply image context when Results.path is empty')
        image=ImageContext(data['path'],width,height,data['path'])
    info=image.image()
    if (info['height'],info['width']) != (height,width):
        raise FormatError('mothbot: dimensions disagree with image context')
    info.setdefault('file_name',data['path'])
    obb=data['obb']
    if len({len(obb[k]) for k in ('xyxyxyxy','conf','cls')}) != 1:
        raise FormatError('mothbot: OBB corners, scores and classes have different lengths')
    instances=[_instance(points,score,i,info,{'ultralytics_obb':{'class_id':cls}})
               for i,(points,score,cls) in enumerate(zip(obb['xyxyxyxy'],obb['conf'],obb['cls']))]
    return record(info,instances,image.metadata,{'ultralytics_obb':data})


def _many(data, images, convert, path_key):
    values = list(data)
    if isinstance(images, Mapping):
        contexts=[]
        for value in values:
            key=value.get(path_key) if isinstance(value,Mapping) else getattr(value,path_key,None)
            if key not in images:
                raise FormatError(f'mothbot: source path {key!r} missing from image manifest')
            contexts.append(images[key])
    elif images is None:
        contexts=[None]*len(values)
    else:
        contexts=list(images)
    if len(contexts)!=len(values):
        raise FormatError('mothbot: outputs and image contexts have different lengths')
    output=[convert(value,image=context) for value,context in zip(values,contexts)]
    ids=[v['image']['id'] for v in output]
    if len(ids)!=len(set(ids)):
        raise FormatError('mothbot: duplicate image IDs; supply distinct image contexts')
    return output


def import_one(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    return ConversionBatch([invoke(to_ir,data,options,image=context.image)])


def import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch
    if options:
        raise FormatError('mothbot: collection importer has no producer options')
    return ConversionBatch(_many(data,context.images,to_ir,'imagePath'))


def obb_import_one(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    return ConversionBatch([invoke(obb_to_ir,data,options,image=context.image)])


def obb_import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch
    if options:
        raise FormatError('mothbot: OBB collection importer has no producer options')
    return ConversionBatch(_many(data,context.images,obb_to_ir,'path'))
