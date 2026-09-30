"""Cross-format stress tests: retained real outputs plus deterministic controls."""
import csv
from copy import deepcopy
import json
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from iai_model_zoo.formats import Converter, ConversionContext, ConversionError
from iai_model_zoo.formats.adapters import ImageContext, Metadata

REPORTS = ROOT / 'src/probe/reports/2026-09-30'


class InteroperabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converter = Converter.open(ROOT)

    def test_real_flatbug_variants_via_coco_geometry_and_scores(self):
        for variant in ('flatbug-N', 'flatbug-M_v2'):
            for image in ('specimen', 'blank'):
                with self.subTest(variant=variant, image=image):
                    path = next((REPORTS / variant).glob(f'samples/predictions/{image}/metadata*'))
                    raw = json.loads(path.read_text())
                    saved = deepcopy(raw)
                    ctx = ConversionContext(image=ImageContext(1, raw['image_width'], raw['image_height'], raw['image_path']),
                                            categories=[{'id': 1, 'name': 'specimen'}])
                    coco = self.converter.convert(raw, model='flatbug', target='coco', context=ctx)
                    back = self.converter.convert(coco, source='coco', target='flatbug', cardinality='collection',
                                                  export_options={'scale': 1.0})[0]
                    self.assertEqual(len(coco['annotations']), len(raw['boxes']))
                    for actual, expected in zip(back['boxes'], raw['boxes']):
                        for a, b in zip(actual, expected): self.assertAlmostEqual(a, b, places=8)
                    self.assertEqual(back['confs'], raw['confs'])
                    self.assertEqual(back['classes'], raw['classes'])
                    self.assertEqual(back['areas'], raw['areas'])
                    # Flatbug scale is not representable in COCO: explicit fallback,
                    # not a claim that this is a lossless native-metadata round trip.
                    self.assertEqual(back['scales'], [1.0] * len(raw['boxes']))
                    self.assertEqual(raw, saved)

    def test_real_arthronat_collection_context(self):
        rows = json.loads((REPORTS / 'arthronat/report.json').read_text())['observation']['results']
        # Reconstruct the supported decoded projection from retained tensor values;
        # names is external test vocabulary, not retained author metadata.
        predictions = [dict(path=r['image'], orig_shape=r['orig_shape'], names={0: 'test class'},
                            boxes={'data': r['boxes']}) for r in rows]
        images = [ImageContext(i, r['orig_shape'][1], r['orig_shape'][0], r['image'],
                               Metadata(model={'name': f'capture-{i}'})) for i, r in enumerate(rows, 1)]
        for supplied in (images, {r['image']: im for r, im in reversed(list(zip(rows, images)))}):
            with self.subTest(container=type(supplied).__name__):
                ctx = ConversionContext(images=supplied, categories=[{'id': 0, 'name': 'test class'}])
                ir = self.converter.convert(iter(predictions), model='arthronat', cardinality='collection', context=ctx)
                self.assertEqual([r['model']['name'] for r in ir], ['capture-1', 'capture-2'])
                output = self.converter.convert(iter(predictions), model='arthronat', target='coco', cardinality='collection', context=ctx)
                self.assertEqual(len(output['images']), 2)
                self.assertEqual(len(output['annotations']), 1)
                x1, y1, x2, y2, confidence, cls = rows[1]['boxes'][0]
                for actual, expected in zip(output['annotations'][0]['bbox'], [x1, y1, x2-x1, y2-y1]):
                    self.assertAlmostEqual(actual, expected, places=8)
                self.assertEqual(output['annotations'][0]['score'], confidence)

    def test_real_biomoth_csv_with_explicit_empty_manifest(self):
        path = ROOT / 'src/probe/reports/2026-09-30-format-expansion/biomoth/artifacts/predictions_2023.csv'
        rows = list(csv.DictReader(path.read_text().splitlines()))
        key = rows[0]['filePath']
        ctx = ConversionContext(images={key: ImageContext(1, 1940, 1933, 'specimen.jpg'),
                                        'known-empty': ImageContext(2, 640, 640, 'blank.png')},
                                categories=[{'id': 0, 'name': 'test class'}])
        output = self.converter.convert(path.read_text(), model='biomoth', target='coco', cardinality='collection',
                                        context=ctx, import_options={'include_empty': True})
        self.assertEqual(len(output['images']), 2)
        self.assertEqual(len(output['annotations']), 32)
        for annotation, row in zip(output['annotations'], rows):
            x1,y1,x2,y2 = [float(row[k]) for k in ('X_Min','Y_Min','X_Max','Y_Max')]
            for a,b in zip(annotation['bbox'], [x1,y1,x2-x1,y2-y1]): self.assertAlmostEqual(a,b,places=8)
            self.assertNotIn('area', annotation)  # calibrated cm² is not pixel area

    def test_retained_yolo_profiles(self):
        for variant, profile in [('stark-yolov5_n','yolov5-detect-txt'), ('stark-yolov7_tiny','yolov7-detect-txt')]:
            path = next((REPORTS / variant).glob('samples/predictions/result/labels/*.txt'))
            rows = [list(map(float, line.split())) for line in path.read_text().splitlines()]
            # specimen is the BumblebeeSedum image; specimen_extra is the Flatbug fixture.
            width, height = (2285, 1275) if path.stem == 'specimen' else (1940, 1933)
            context = ConversionContext(image=ImageContext(1, width, height, path.stem + '.jpg'),
                                        categories=[{'id': int(c), 'name': f'test class {int(c)}'} for c in sorted({r[0] for r in rows})])
            coco = self.converter.convert(path.read_text(), source=profile, target='coco', context=context,
                                          import_options={'save_conf': True})
            self.assertEqual(len(coco['annotations']), len(rows))
            for a,r in zip(coco['annotations'], rows):
                expected=[(r[1]-r[3]/2)*width,(r[2]-r[4]/2)*height,r[3]*width,r[4]*height]
                for x,y in zip(a['bbox'],expected): self.assertAlmostEqual(x,y,places=8)

    def test_randomized_txt_coco_ir_geometry(self):
        rng = random.Random(481)
        images, raw, maps = {}, {}, {}
        for i in range(40):
            w,h=rng.randint(1,4000),rng.randint(1,4000)
            images[str(i)] = ImageContext(i,w,h,f'{i}.jpg')
            rows=[]
            for j in range(i % 7):
                x,y,bw,bh=[rng.random() for _ in range(4)]
                rows.append(f'0 {x} {y} {bw} {bh} {rng.random()}')
                maps[i,j]=len(maps)
            raw[str(i)]='\n'.join(rows)
        ctx=ConversionContext(images=images,categories=[{'id':0,'name':'test'}],annotation_ids=maps)
        ir=self.converter.convert(raw,source='yolov5-detect-txt',cardinality='collection',context=ctx,import_options={'save_conf':True})
        coco=self.converter.convert(raw,source='yolov5-detect-txt',target='coco',cardinality='collection',context=ctx,import_options={'save_conf':True})
        back=self.converter.convert(coco,source='coco',cardinality='collection')
        self.assertEqual(len(back),40)
        for a,b in zip(ir,back):
            self.assertEqual(a['image'],b['image'])
            for x,y in zip(a['instances'],b['instances']):
                for v,w in zip(x['bbox'],y['bbox']): self.assertAlmostEqual(v,w,places=9)
                self.assertEqual(x['confidence'],y['confidence'])

    def test_expected_semantic_failures(self):
        ctx=ConversionContext(image=ImageContext(1,200,100,'a.jpg'),categories=[{'id':0,'name':'test'}])
        with self.assertRaisesRegex(ConversionError,'category_id'):
            self.converter.convert([[1,2,3,4]],source='ami-detector-boxes',target='coco',context=ctx,export_options={'fallback_category': None})
        with self.assertRaisesRegex(ConversionError,'polygons'):
            self.converter.convert('0 .5 .5 .2 .2 .8',source='yolov5-detect-txt',target='flatbug',context=ctx,import_options={'save_conf':True})
        with self.assertRaisesRegex(ConversionError,'No importer'):
            self.converter.convert({},model='insect-detect-platform',target='coco')

    def test_invalid_context_has_consistent_error(self):
        for ctx in ({}, ConversionContext(image='not an ImageContext')):
            with self.subTest(context=ctx), self.assertRaisesRegex(ConversionError, 'context'):
                self.converter.convert([],source='ami-detector-boxes',context=ctx)

    def test_unknown_results_path_and_duplicate_context_ids(self):
        raw = [{'orig_shape': [10, 10], 'path': 'unknown', 'names': {}, 'boxes': {'data': []}}]
        with self.assertRaisesRegex(ConversionError, 'missing from manifest'):
            self.converter.convert(raw, model='arthronat', cardinality='collection',
                context=ConversionContext(images={'known': ImageContext(1, 10, 10)}))
        with self.assertRaisesRegex(ConversionError, 'Duplicate image context ID'):
            self.converter.convert(raw, model='arthronat', cardinality='collection',
                context=ConversionContext(images=[ImageContext(1, 10, 10), ImageContext(1, 10, 10)]))

    def test_empty_collections_preserve_shape(self):
        for source, data, ctx, options in [
            ('isir', [], ConversionContext(), {}),
            ('ultralytics-detect-results', iter([]), ConversionContext(images=[]), {}),
            ('yolov5-detect-txt', {}, ConversionContext(images={}), {'save_conf': False}),
            ('ultralytics-detect-json', {}, ConversionContext(images={}), {'normalized': False}),
        ]:
            with self.subTest(source=source):
                out = self.converter.convert(data, source=source, target='coco', cardinality='collection', context=ctx, import_options=options)
                self.assertEqual(out['images'], [])
                self.assertEqual(out['annotations'], [])
