"""Source-contract fixtures; not evidence of executing author checkpoints."""
from copy import deepcopy
import csv
from io import StringIO
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from iai_model_zoo.formats import Converter, ConversionContext, ConversionError
from iai_model_zoo.formats.adapters import ImageContext
from iai_model_zoo.formats.adapters._common import schema


class AdditionalImportTests(unittest.TestCase):
    def setUp(self):
        self.c = Converter.open(ROOT)
        self.image = ImageContext(1,200,100,'a.jpg')

    def test_grounding_pixels_normalized_empty_and_phrases(self):
        for normalized, box in [(False,[10,20,50,60]),(True,[.05,.2,.25,.6])]:
            source=[dict(boxes=[box],scores=[.8],labels=['bee butterfly']),dict(boxes=[],scores=[],labels=[])]
            saved=deepcopy(source)
            ctx=ConversionContext(images=[self.image,ImageContext(2,200,100,'b.jpg')])
            ir=self.c.convert(source,model='grounding-dino',cardinality='collection',context=ctx,import_options={'normalized':normalized})
            self.assertEqual(ir[0]['instances'][0]['bbox'],[30,60,40,40])
            self.assertEqual(ir[0]['instances'][0]['extra_information']['grounding_dino']['phrase'],'bee butterfly')
            self.assertNotIn('category_id',ir[0]['instances'][0])
            out=self.c.convert(source,model='grounding-dino',target='coco',cardinality='collection',context=ctx,import_options={'normalized':normalized})
            self.assertEqual(out['annotations'][0]['bbox'],[10,20,40,40])
            self.assertEqual(out['categories'],[{'id':1,'name':'object'}])
            self.assertEqual(len(out['images']),2)
            self.assertEqual(source,saved)

    def test_grounding_rejects_ambiguous_or_malformed_inputs(self):
        data=[dict(boxes=[[1,2,3,4]],scores=[.8],labels=['insect'])]
        for images, options in [([self.image],{}), ({'a':self.image},{'normalized':False}), ([],{'normalized':False})]:
            with self.subTest(images=images,options=options), self.assertRaises(ConversionError):
                self.c.convert(data,source='grounding-dino-hf-results',cardinality='collection',context=ConversionContext(images=images),import_options=options)
        data[0]['labels']=[]
        with self.assertRaisesRegex(ConversionError,'equal lengths'):
            self.c.convert(data,source='grounding-dino-hf-results',cardinality='collection',context=ConversionContext(images=[self.image]),import_options={'normalized':False})

    def row(self):
        return dict(year='2025',trap='test',date='20250101',time='120000',detectConf=85,detectId=1,
                    x1=10,y1=20,x2=50,y2=60,fileName='a.jpg',orderLabel='test-order',orderId=0,
                    orderConf=91.2,aboveTH='True',key=42,speciesLabel='test-species',speciesId=3,speciesConf=75.5)

    def test_mcc_csv_geometry_metadata_and_empty(self):
        stream=StringIO();writer=csv.DictWriter(stream,fieldnames=schema('mcc24-csv').notes['header']);writer.writeheader();writer.writerow(self.row())
        ctx=ConversionContext(images={'a.jpg':self.image,'empty':ImageContext(2,200,100,'empty.jpg')})
        ir=self.c.convert(stream.getvalue(),model='bjerge-2025-moths-yolov5-resnet50',cardinality='collection',context=ctx,import_options={'include_empty':True})
        self.assertEqual(ir[0]['instances'][0]['confidence'],.85)
        self.assertEqual(ir[0]['instances'][0]['extra_information']['mcc24']['speciesConf'],75.5)
        self.assertNotIn('category_id',ir[0]['instances'][0])
        out=self.c.convert(stream.getvalue(),source='mcc24-csv',target='coco',cardinality='collection',context=ctx,import_options={'include_empty':True})
        self.assertEqual(out['annotations'][0]['bbox'],[10,20,40,40])
        self.assertEqual(out['annotations'][0]['id'],42)
        self.assertEqual(len(out['images']),2)

    def test_mcc_rejects_bad_boxes_scores_and_csv(self):
        for change in ({'y1':100,'y2':60},{'detectConf':101},{'fileName':'unknown'}):
            row={**self.row(),**change}
            with self.subTest(change=change),self.assertRaises(ConversionError):
                self.c.convert([row],source='mcc24-csv',cardinality='collection',context=ConversionContext(images={'a.jpg':self.image}))
