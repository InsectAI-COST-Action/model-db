"""End-to-end conversions of existing outputs, without model runtimes."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from iai_model_zoo.formats import Converter, ConversionContext, ConversionError
from iai_model_zoo.formats.adapters import ImageContext, Metadata
from test_adapters import flatbug_sample, coco_sample


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.converter = Converter.open(ROOT)

    def test_all_registered_wrappers_share_the_interface(self):
        from importlib import import_module
        from inspect import signature
        for descriptor in self.converter.registry.formats.values():
            for reference in descriptor['notes'].get('adapters', {}).values():
                module, name = reference.split(':')
                function = getattr(import_module(module), name)
                signature(function).bind(None, context=ConversionContext(), options={}, source='test')

    def test_model_lookup_and_coco_export(self):
        raw = {'orig_shape': [80, 100], 'path': 'a.jpg', 'names': {0: 'bug'},
               'boxes': {'data': [[10, 20, 30, 50, .9, 0]]}}
        before = deepcopy(raw)
        context = ConversionContext(image=ImageContext(1, 100, 80, 'a.jpg'),
                                    categories=[{'id': 0, 'name': 'bug'}])
        out = self.converter.convert(raw, model='arthronat', target='coco', context=context)
        self.assertEqual(out['images'][0]['id'], 1)
        self.assertEqual(out['annotations'][0]['bbox'], [10., 20., 20., 30.])
        self.assertEqual(raw, before)

    def test_coco_roundtrip_retains_dataset_and_empty_images(self):
        raw = coco_sample()
        out = self.converter.convert(raw, source='coco', target='coco', cardinality='collection')
        self.assertEqual(out, raw)
        self.assertIsNot(out, raw)

    def test_flatbug_roundtrip_and_ids(self):
        raw = flatbug_sample()
        ir = self.converter.convert(raw, source='flatbug')
        out = self.converter.convert(ir, source='isir', target='flatbug')
        self.assertEqual(out, raw)
        ctx = ConversionContext(categories=[{'id': 1, 'name': 'bug'}], image_ids={ir['image']['id']: 8})
        coco = self.converter.convert(ir, source='isir', target='coco', context=ctx)
        self.assertEqual(coco['annotations'][0]['image_id'], 8)

    def test_txt_collection_and_global_annotation_ids(self):
        images = {'a': ImageContext(1, 100, 80, 'a.jpg'), 'b': ImageContext(2, 100, 80, 'b.jpg')}
        ctx = ConversionContext(images=images, categories=[{'id': 0, 'name': 'bug'}],
                                annotation_ids={(1, 0): 10, (2, 0): 11})
        raw = {'a': '0 .5 .5 .2 .2', 'b': '0 .5 .5 .2 .2'}
        out = self.converter.convert(raw, source='yolov5-detect-txt', target='coco',
                    cardinality='collection', context=ctx, import_options={'save_conf': False})
        self.assertEqual([a['id'] for a in out['annotations']], [10, 11])
        self.assertEqual(len(out['images']), 2)
        ctx.annotation_ids = None
        with self.assertRaisesRegex(ConversionError, 'duplicate'):
            self.converter.convert(raw, source='yolov5-detect-txt', target='coco',
                    cardinality='collection', context=ctx, import_options={'save_conf': False})

    def test_missing_context_and_options(self):
        with self.assertRaisesRegex(ConversionError, 'image'):
            self.converter.convert([], source='ami-detector-boxes')
        ctx = ConversionContext(image=ImageContext(1, 100, 80))
        with self.assertRaisesRegex(ConversionError, 'save_conf'):
            self.converter.convert('', source='yolov5-detect-txt', context=ctx)
        with self.assertRaisesRegex(ConversionError, 'No importer'):
            self.converter.convert({}, source='mothbot-detection-json')

    def test_metadata_precedence_and_collection_shape(self):
        ctx = ConversionContext(image=ImageContext(1, 100, 80, metadata=Metadata(model={'name': 'per-image'})),
                                metadata=Metadata(model={'name': 'shared'}))
        ir = self.converter.convert([], source='ami-detector-boxes', context=ctx)
        self.assertEqual(ir['model']['name'], 'per-image')
        out = self.converter.convert([ir], source='isir', cardinality='collection')
        self.assertIsInstance(out, list)
        self.assertEqual(len(out), 1)
        with self.assertRaisesRegex(ConversionError, 'Duplicate ISIR'):
            self.converter.convert([ir, ir], source='isir', cardinality='collection')

    def test_collection_export_maps_per_image(self):
        ir = self.converter.convert(flatbug_sample(), source='flatbug')
        second = deepcopy(ir); second['image']['id'] = 'second'
        out = self.converter.convert([ir, second], source='isir', target='flatbug', cardinality='collection')
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]['boxes'], out[1]['boxes'])


if __name__ == '__main__':
    unittest.main()
