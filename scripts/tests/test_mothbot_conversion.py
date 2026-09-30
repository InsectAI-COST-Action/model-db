"""Native Mothbot and alternative OBB conversion, preserving actual orientation."""
import json
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from iai_model_zoo.formats import Converter, ConversionContext, ConversionError
from iai_model_zoo.formats.adapters import ImageContext
from iai_model_zoo.formats.adapters._common import box_polygon, flip_polygon


class MothbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.c=Converter.open(ROOT)

    def check_corners(self, instance, expected, height):
        corners=flip_polygon(box_polygon(instance['bbox'],instance['angle']),height)
        # Equivalent ordered rectangle representations may reverse corner order.
        for point in expected:
            self.assertLess(min(math.dist(point,p) for p in corners),.01)

    def test_native_real_outputs_preserve_obb(self):
        base=ROOT/'src/probe/reports/2026-09-30-format-expansion/mothbot/artifacts'
        for name,count in [('specimen',15),('blank',0)]:
            data=json.loads((base/f'{name}_botdetection.json').read_text())
            ctx=ConversionContext(image=ImageContext(1,data['imageWidth'],data['imageHeight'],data['imagePath']))
            ir=self.c.convert(data,model='mothbot',context=ctx)
            self.assertEqual(len(ir['instances']),count)
            out=self.c.convert(data,model='mothbot',target='coco',context=ctx)
            for instance,shape,annotation in zip(ir['instances'],data['shapes'],out['annotations']):
                self.check_corners(instance,shape['points'],data['imageHeight'])
                self.assertEqual(instance['extra_information']['mothbot']['direction'],shape['direction'])
                for actual,expected in zip(annotation['segmentation'][0],[c for p in shape['points'] for c in p]):
                    self.assertAlmostEqual(actual,expected,places=8)
                xs,ys=zip(*shape['points'])
                for a,b in zip(annotation['bbox'],[min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]):
                    self.assertAlmostEqual(a,b,places=3)
                self.assertEqual(annotation['score'],shape['confidence_detection'])

    def test_alternative_projection_and_angle_only_export(self):
        for angle in [0,.2,-.7,math.pi/2,math.pi]:
            box=[60,40,30,10];corners=flip_polygon(box_polygon(box,angle),100)
            data=dict(orig_shape=[100,200],path='a.jpg',names={'0':'object'},
                      obb=dict(xyxyxyxy=[corners],conf=[.8],cls=[0]))
            ctx=ConversionContext(image=ImageContext(1,200,100,'a.jpg'))
            ir=self.c.convert(data,source='ultralytics-obb-results',context=ctx)
            self.check_corners(ir['instances'][0],corners,100)
            ir['instances'][0].pop('polygons')
            out=self.c.convert(ir,source='isir',target='coco')
            self.assertEqual(len(out['annotations'][0]['segmentation'][0]),8)
            self.assertEqual(out['categories'],[{'id':1,'name':'object'}])

    def test_native_collections_and_bad_geometry(self):
        base=ROOT/'src/probe/reports/2026-09-30-format-expansion/mothbot/artifacts'
        data=[json.loads((base/f'{n}_botdetection.json').read_text()) for n in ['blank','specimen']]
        ctx=ConversionContext(images={d['imagePath']:ImageContext(i,d['imageWidth'],d['imageHeight'],d['imagePath']) for i,d in enumerate(data)})
        out=self.c.convert(data,model='mothbot',target='coco',cardinality='collection',context=ctx)
        self.assertEqual(len(out['images']),2)
        self.assertEqual(len(out['annotations']),15)
        data[1]['shapes'][0]['points']=[[0,0],[1,1],[0,1],[1,0]]
        with self.assertRaisesRegex(ConversionError,'quadrilateral'):
            self.c.convert(data[1],model='mothbot')

    def test_retained_direct_checkpoint_projections(self):
        root=ROOT/'src/probe/reports/2026-09-30-mothbot-conversion'
        for name,count in [('specimen',15),('blank',0)]:
            data=json.loads((root/f'{name}-results.json').read_text())
            height,width=data['orig_shape']
            context=ConversionContext(image=ImageContext(1,width,height,name+'.jpg'))
            ir=self.c.convert(data,source='ultralytics-obb-results',context=context)
            self.assertEqual(len(ir['instances']),count)
            for instance,points in zip(ir['instances'],data['obb']['xyxyxyxy']):
                self.check_corners(instance,points,height)
