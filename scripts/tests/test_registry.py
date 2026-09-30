"""Metadata-only resolution and extension tests."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from iai_model_zoo.registry import Registry, RegistryError, SelectionError


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / 'static/formats/detection', self.root / 'static/formats/detection')
        for path in (ROOT / 'content/models').glob('*/index.md'):
            target = self.root / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(path, target)

    def descriptor(self, name, edit):
        path = self.root / 'static/formats/detection' / (name + '.json')
        data = json.loads(path.read_text())
        edit(data)
        path.write_text(json.dumps(data))

    def card(self, name, formats):
        path = self.root / 'content/models' / name / 'index.md'
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text('+++\narchitecture = ' + json.dumps(['test'] * len(formats)) + '\noutput_format = ' + json.dumps(formats) + '\n+++\n')

    def test_representative_plans(self):
        r = Registry.open(self.root)
        p = r.resolve(model='arthronat', cardinality='one')
        self.assertEqual(p['status'], 'ready')
        self.assertTrue(p['steps'][0]['implementation'].endswith('ultralytics:import_one'))
        p = r.resolve(source='flatbug', target='coco')
        self.assertEqual([s['operation'] for s in p['steps']], ['adapter', 'collect', 'adapter'])
        self.assertEqual(p['output_cardinality'], 'collection')
        p = r.resolve(source='coco', target='flatbug')
        self.assertEqual(p['steps'][-1]['mode'], 'each')
        self.assertEqual(p['output_cardinality'], 'collection')
        p = r.resolve(source='isir', cardinality='one')
        self.assertEqual(p['steps'][0]['operation'], 'identity')
        self.assertEqual(r.resolve(source='isir')['status'], 'needs_context')

    def test_metadata_only_extensions(self):
        self.card('new-model', ['flatbug'])
        r = Registry.open(self.root)
        self.assertEqual(r.resolve(model='new-model')['source'], 'flatbug')
        source = self.root / 'static/formats/detection/flatbug.json'
        new = source.with_name('new-format.json')
        shutil.copy(source, new)
        self.descriptor('new-format', lambda d: d['notes']['adapters'].update(import_one='uninstalled.extension:convert'))
        self.card('new-model', ['new-format'])
        changed = Registry.open(self.root)
        p = changed.resolve(model='new-model')
        self.assertEqual(p['steps'][0]['implementation'], 'uninstalled.extension:convert')
        self.assertNotEqual(r.fingerprint, changed.fingerprint)
        self.descriptor('new-format', lambda d: d['notes'].pop('adapters'))
        self.assertEqual(Registry.open(self.root).resolve(model='new-model')['status'], 'unsupported')

    def test_ambiguity_and_repeated_formats(self):
        self.card('repeat', ['flatbug', 'flatbug'])
        self.card('different', ['flatbug', 'coco'])
        r = Registry.open(self.root)
        self.assertEqual(len(r.query(model='repeat')), 1)
        self.assertEqual(len(r.resolve(model='repeat')['architectures']), 2)
        with self.assertRaises(SelectionError): r.resolve(model='different')
        self.assertEqual(r.resolve(model='different', source='flatbug')['source'], 'flatbug')
        with self.assertRaises(SelectionError): r.resolve(model='arthronat')
        self.assertEqual(r.resolve(model='arthronat', cardinality='collection')['output_cardinality'], 'collection')

    def test_api_requirements_stay_with_adapters(self):
        r = Registry.open(self.root)
        p = r.resolve(source='yolov5-detect-txt', cardinality='one')
        self.assertEqual(p['status'], 'ready')
        self.assertIn('caller supplies API arguments', p['readiness_scope'])
        self.assertNotIn('options', p)

    def test_gaps_invalid_metadata_and_snapshot(self):
        self.card('gap', [])
        r = Registry.open(self.root)
        self.assertEqual(r.resolve(model='gap')['status'], 'unsupported')
        self.assertEqual(r.resolve(source='insect-detect-csv')['status'], 'unsupported')
        self.assertEqual(r.fingerprint, Registry.open(self.root).fingerprint)
        p = r.resolve(source='flatbug'); p['steps'].clear()
        self.assertTrue(r.resolve(source='flatbug')['steps'])
        json.dumps(r.query())
        self.card('gap', ['missing'])
        with self.assertRaises(RegistryError): Registry.open(self.root)

    def test_binding_validation(self):
        for binding in ({'import_one': 'exec(code)'}, {'guess': 'module:call'}, {'import_one': {}}):
            with self.subTest(binding=binding):
                path = self.root / 'static/formats/detection/flatbug.json'
                original = path.read_text()
                self.descriptor('flatbug', lambda d: d['notes'].update(adapters=binding))
                with self.assertRaises(RegistryError): Registry.open(self.root)
                path.write_text(original)

    def test_no_implementation_imports_or_network(self):
        code = '''import sys, socket
sys.path.insert(0, sys.argv[1])
def blocked(*a, **kw): raise AssertionError('network')
socket.socket = blocked
from iai_model_zoo.registry import Registry
Registry.open(sys.argv[2]).query()
assert not any(n.startswith(('iai_model_zoo.formats.adapters', 'torch', 'ultralytics')) for n in sys.modules)
'''
        subprocess.run([sys.executable, '-c', code, str(ROOT / 'src'), str(self.root)], check=True)

    def test_snapshot_escape(self):
        path = self.root / 'static/formats/detection/escape.json'
        path.symlink_to(ROOT / 'static/formats/detection/flatbug.json')
        with self.assertRaises(RegistryError): Registry.open(self.root)


if __name__ == '__main__':
    unittest.main()
