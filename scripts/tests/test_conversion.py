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
            self.converter.convert({}, source='insect-detect-csv')

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

    def test_class_agnostic_ami_to_coco(self):
        context = ConversionContext(image=ImageContext(1, 200, 100, 'frame.jpg'))
        fallback = {'id': 1, 'name': 'object'}
        output = self.converter.convert([[10, 20, 50, 60]], model='ami-insect-detector',
                    target='coco', context=context, export_options={'fallback_category': fallback})
        self.assertEqual(output['categories'], [fallback])
        self.assertEqual(output['annotations'][0]['category_id'], 1)
        self.assertEqual(output['annotations'][0]['bbox'], [10, 20, 40, 40])
        self.assertNotIn('score', output['annotations'][0])
        self.assertEqual(context.categories, None)
        empty = self.converter.convert([], model='ami-insect-detector', target='coco',
                    context=context, export_options={'fallback_category': fallback})
        self.assertEqual(empty['annotations'], [])

    def test_default_object_category_and_collision_handling(self):
        context = ConversionContext(image=ImageContext(1, 20, 20, 'a.jpg'))
        out = self.converter.convert([[1, 2, 3, 4]], model='ami-insect-detector',
                                     target='coco', context=context)
        self.assertEqual(out['categories'], [{'id': 1, 'name': 'object'}])
        self.assertEqual(out['annotations'][0]['category_id'], 1)
        context.categories = [{'id': 1, 'name': 'beetle'}]
        out = self.converter.convert([[1, 2, 3, 4]], source='ami-detector-boxes',
                                     target='coco', context=context)
        self.assertEqual(out['annotations'][0]['category_id'], 2)
        context.categories.append({'id': 5, 'name': 'object'})
        out = self.converter.convert([[1, 2, 3, 4]], source='ami-detector-boxes',
                                     target='coco', context=context)
        self.assertEqual(out['annotations'][0]['category_id'], 5)
        self.assertEqual(len(out['categories']), 2)
        with self.assertRaisesRegex(ConversionError, 'category_id'):
            self.converter.convert([[1, 2, 3, 4]], source='ami-detector-boxes',
                target='coco', context=context, export_options={'fallback_category': None})
        empty = self.converter.convert([], source='ami-detector-boxes', target='coco',
                context=ConversionContext(image=ImageContext(1, 20, 20, 'a.jpg')))
        self.assertEqual(empty['categories'], [])

    def test_fallback_preserves_existing_categories_and_rejects_conflicts(self):
        ir = self.converter.convert([[1, 2, 3, 4], [5, 6, 7, 8]], source='ami-detector-boxes',
                    context=ConversionContext(image=ImageContext(1, 20, 20, 'a.jpg')))
        ir['instances'][0]['category_id'] = 0
        original = deepcopy(ir)
        context = ConversionContext(categories=[{'id': 0, 'name': 'beetle'}])
        output = self.converter.convert(ir, source='isir', target='coco', context=context,
                    export_options={'fallback_category': {'id': 1, 'name': 'object'}})
        self.assertEqual([a['category_id'] for a in output['annotations']], [0, 1])
        self.assertEqual(ir, original)
        self.assertEqual(context.categories, [{'id': 0, 'name': 'beetle'}])
        with self.assertRaisesRegex(ConversionError, 'conflicts'):
            self.converter.convert(ir, source='isir', target='coco', context=context,
                    export_options={'fallback_category': {'id': 0, 'name': 'object'}})
        same = self.converter.convert(ir, source='isir', target='coco', context=context,
                    export_options={'fallback_category': {'id': 0, 'name': 'beetle'}})
        self.assertEqual(len(same['categories']), 1)
        with self.assertRaisesRegex(ConversionError, 'category_id'):
            self.converter.convert(ir, source='isir', target='coco',
                    export_options={'fallback_category': {'id': 1, 'name': 'object'}})
        for invalid in ({'id': 1}, {'id': 1.5, 'name': 'object'}):
            with self.subTest(invalid=invalid), self.assertRaises(ConversionError):
                self.converter.convert(ir, source='isir', target='coco', context=context,
                            export_options={'fallback_category': invalid})

    def test_collection_export_maps_per_image(self):
        ir = self.converter.convert(flatbug_sample(), source='flatbug')
        second = deepcopy(ir); second['image']['id'] = 'second'
        out = self.converter.convert([ir, second], source='isir', target='flatbug', cardinality='collection')
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]['boxes'], out[1]['boxes'])


if __name__ == '__main__':
    unittest.main()
