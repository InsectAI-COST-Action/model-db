"""Read-only discovery of model formats and descriptor-local ISIR adapters.

No adapter or model implementation is imported here. Python 3.11+ is required.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re



class RegistryError(ValueError):
    """Invalid snapshot or unknown query identifier."""


class SelectionError(RegistryError):
    """Selection is ambiguous; candidates identifies the available choices."""

    def __init__(self, message, candidates):
        super().__init__(message)
        self.candidates = candidates


_MISSING = object()


def validate_bindings(document):
    """Validate a small direction/cardinality -> callable mapping."""
    bindings = document.get('notes', {}).get('adapters', {})
    if not isinstance(bindings, dict):
        raise RegistryError('notes.adapters must be an object')
    for name, reference in bindings.items():
        if name not in ('import_one', 'import_collection', 'export_one', 'export_collection'):
            raise RegistryError(f'Unknown adapter operation: {name}')
        if not isinstance(reference, str) or not re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*', reference):
            raise RegistryError(f'{name}: expected module:function')
    return bindings


class Registry:
    """A local metadata snapshot. No inference or adapter execution occurs here."""

    @classmethod
    def open(cls, snapshot_path):
        import tomllib

        self = cls()
        root = Path(snapshot_path).resolve()
        self._files, self._models, self._formats = {}, {}, {}

        def read(path):
            resolved = path.resolve()
            if not resolved.is_relative_to(root):
                raise RegistryError(f'Snapshot path escapes root: {path}')
            data = resolved.read_bytes()
            self._files[str(path.relative_to(root))] = hashlib.sha256(data).hexdigest()
            return data.decode('utf-8')

        try:
            for path in sorted((root / 'static/formats/detection').glob('*.json')):
                document = json.loads(read(path))
                if not isinstance(document, dict) or not isinstance(document.get('notes'), dict):
                    raise RegistryError(f'{path}: invalid format descriptor')
                try:
                    validate_bindings(document)
                except RegistryError as error:
                    raise RegistryError(f'{path}: {error}') from error
                self._formats[path.stem] = document
            if 'isir' not in self._formats:
                raise RegistryError('Snapshot needs static/formats/detection/isir.json')
            for path in sorted((root / 'content/models').glob('*/index.md')):
                parts = re.split(r'^\+\+\+\s*$', read(path), flags=re.MULTILINE)
                if len(parts) < 3:
                    raise RegistryError(f'{path}: missing TOML frontmatter')
                card = json.loads(json.dumps(tomllib.loads(parts[1]), default=lambda v: v.isoformat()))
                formats = card.get('output_format', [])
                if not isinstance(formats, list) or not all(isinstance(f, str) for f in formats):
                    raise RegistryError(f'{path}: output_format must be a string list')
                if formats and len(formats) != len(card.get('architecture', [])):
                    raise RegistryError(f'{path}: output_format must align with architecture')
                for fmt in formats:
                    if fmt != 'other' and fmt not in self._formats:
                        raise RegistryError(f'{path}: unknown output_format {fmt!r}')
                self._models[path.parent.name] = card
        except (OSError, TypeError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
            raise RegistryError(f'Invalid snapshot: {error}') from error
        self._fingerprint = hashlib.sha256(json.dumps(self._files, sort_keys=True).encode()).hexdigest()
        return self

    @property
    def fingerprint(self):
        return self._fingerprint

    @property
    def formats(self):
        return deepcopy(self._formats)

    def _bindings(self, fmt, direction, cardinality=None):
        return [(key, reference) for key, reference in sorted(self._formats.get(fmt, {}).get('notes', {}).get('adapters', {}).items())
                if key.startswith(direction + '_') and (cardinality is None or key == direction + '_' + cardinality)]

    def query(self, *, model=None, source=None, target='isir', cardinality=None,
              model_fields=None, status=None):
        """List adapter paths. API arguments and prediction checks belong to adapters."""
        for value, table, label in ((model, self._models, 'model'), (source, self._formats, 'source'), (target, self._formats, 'target')):
            if value is not None and value not in table:
                raise RegistryError(f'Unknown {label}: {value}')
        if cardinality not in (None, 'one', 'collection') or status not in (None, 'ready', 'needs_context', 'unsupported'):
            raise RegistryError('Invalid cardinality or status')
        if model_fields is not None and not isinstance(model_fields, dict):
            raise RegistryError('model_fields must be an object')
        cards = [(model, self._models[model])] if model else ([(None, {})] if source else sorted(self._models.items()))
        results = []
        for identifier, card in cards:
            if any(card.get(k, _MISSING) != v for k, v in (model_fields or {}).items()):
                continue
            formats = list(dict.fromkeys(card.get('output_format', []))) if identifier else [source]
            for fmt in formats or [None]:
                if source and source != fmt:
                    continue
                imports = [(None, None)] if fmt == 'isir' else self._bindings(fmt, 'import', cardinality) or [(None, None)]
                exports = [(None, None)] if target == 'isir' else self._bindings(target, 'export') or [(None, None)]
                for in_name, incoming in imports:
                    for out_name, outgoing in exports:
                        plan = self._plan(identifier, card, fmt, target, cardinality, in_name, incoming, out_name, outgoing)
                        if status is None or plan['status'] == status:
                            results.append(plan)
        return deepcopy(results)

    def _plan(self, model, card, source, target, cardinality, in_name, incoming, out_name, outgoing):
        steps, reasons = [], []
        state = 'ready'
        current = in_name.split('_', 1)[1] if incoming else cardinality
        if source != 'isir' and incoming is None:
            reasons.append('No importer for the declared output format' if source not in (None, 'other') else 'Model output format is unspecified')
            state = 'unsupported'
        if target != 'isir' and outgoing is None:
            reasons.append('No exporter for the target format')
            state = 'unsupported'
        if source == 'isir' and current is None:
            reasons.append('Specify ISIR input cardinality')
            if state != 'unsupported':
                state = 'needs_context'
        if incoming:
            steps.append(dict(operation='adapter', direction='import', implementation=incoming,
                              cardinality=current, mode='direct'))
        if outgoing:
            expected = out_name.split('_', 1)[1]
            mode = 'direct'
            if current == 'one' and expected == 'collection':
                steps.append(dict(operation='collect', input='one', output='collection'))
                current = 'collection'
            elif current == 'collection' and expected == 'one':
                mode = 'each'
            steps.append(dict(operation='adapter', direction='export', implementation=outgoing,
                              cardinality=expected, mode=mode))
        if source == target == 'isir':
            steps.append(dict(operation='identity', cardinality=current))
        return dict(model=model, source=source, target=target, status=state,
                    architectures=[a for a, f in zip(card.get('architecture', []), card.get('output_format', [])) if f == source],
                    model_record=card, source_record=self._formats.get(source), target_record=self._formats[target],
                    steps=steps, output_cardinality=current, reasons=reasons,
                    snapshot=self.fingerprint, fingerprint_files=self._files,
                    readiness_scope='adapter path only; caller supplies API arguments and adapters validate predictions')

    def resolve(self, **kwargs):
        candidates = self.query(**kwargs)
        if len(candidates) != 1:
            raise SelectionError('Select a source format and input cardinality to identify one conversion', candidates)
        return candidates[0]
