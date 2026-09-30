"""Conversion of existing predictions; no model loading or inference."""
from copy import deepcopy
from dataclasses import dataclass, field
from importlib import import_module
from inspect import signature

from .schema import FormatError


class ConversionError(FormatError):
    """A conversion could not be configured or its data was invalid."""


@dataclass
class ConversionContext:
    """Explicit caller facts. None means preserve native data, not invent it.

    image is an ImageContext; images maps source keys to ImageContext objects.
    metadata is Metadata, applied after import; per-image metadata takes precedence.
    categories overrides dataset categories; dataset_metadata merges other fields.
    ID mappings are passed to exporters, never generated implicitly.
    """
    image: object = None
    images: object = None
    metadata: object = None
    categories: list | None = None
    dataset_metadata: dict = field(default_factory=dict)
    image_ids: dict | None = None
    annotation_ids: dict | None = None


@dataclass
class ConversionBatch:
    """Internal transport: separate ISIR images and dataset metadata."""
    images: list[dict]
    metadata: dict = field(default_factory=dict)


def invoke(function, data, options, **context):
    """Bind API arguments before calling; leave prediction errors to the adapter."""
    kwargs = {k: v for k, v in context.items() if v is not None}
    overlap = kwargs.keys() & options.keys()
    if overlap:
        raise ConversionError(f'Supply {sorted(overlap)} through context only')
    kwargs.update(options)
    try:
        signature(function).bind(data, **kwargs)
    except TypeError as error:
        raise ConversionError(str(error)) from error
    return function(data, **kwargs)


class Converter:
    """Execute descriptor-selected output adapters from a trusted local snapshot."""
    def __init__(self, registry):
        self.registry = registry

    @classmethod
    def open(cls, snapshot_path):
        from iai_model_zoo.registry import Registry
        return cls(Registry.open(snapshot_path))

    def convert(self, predictions, *, model=None, source=None, target='isir',
                cardinality='one', context=None, import_options=None, export_options=None):
        """Convert one image by default; use cardinality='collection' for batches.

        ISIR output is a dict for one input image and a list for collection input.
        Exporters own target containers (e.g. COCO always returns a dataset dict).
        """
        from .adapters._common import checked_ir
        if model is None and source is None:
            raise ConversionError('Specify model or source')
        context = context or ConversionContext()
        if not isinstance(context, ConversionContext):
            raise ConversionError('context must be ConversionContext')
        for options in (import_options, export_options):
            if options is not None and not isinstance(options, dict):
                raise ConversionError('Adapter options must be dictionaries')
        if context.image is not None and context.images is not None:
            raise ConversionError('Supply image or images, not both')
        plan = self.registry.resolve(model=model, source=source, target=target, cardinality=cardinality)
        if plan['status'] != 'ready':
            raise ConversionError('; '.join(plan['reasons']))
        incoming = next((s for s in plan['steps'] if s.get('direction') == 'import'), None)
        outgoing = next((s for s in plan['steps'] if s.get('direction') == 'export'), None)

        def call(step, data, options):
            reference = step['implementation']
            try:
                module, name = reference.split(':')
                function = getattr(import_module(module), name)
                return function(data, context=context, options=options or {}, source=plan['source'])
            except (ImportError, AttributeError, FormatError, TypeError, ValueError) as error:
                raise ConversionError(f"{step['direction']} {plan['source']} -> {target}: {error}") from error

        if incoming:
            batch = call(incoming, predictions, import_options)
        else:
            if import_options:
                raise ConversionError('ISIR identity does not accept import options')
            batch = ConversionBatch([predictions] if cardinality == 'one' else list(predictions))
        if not isinstance(batch, ConversionBatch):
            raise ConversionError('Importer must return ConversionBatch')
        batch = deepcopy(batch)
        if cardinality == 'one' and len(batch.images) != 1:
            raise ConversionError('Single-image importer must return exactly one image')
        seen = set()
        for i, record in enumerate(batch.images):
            record = checked_ir(record)
            # Explicit shared metadata overrides native values; explicit per-image
            # metadata (already applied by the importer) overrides shared values.
            per_image = None
            if context.image is not None:
                per_image = context.image.metadata
            elif context.images is not None:
                matches = [c for c in context.images.values() if c.id == record['image']['id']]
                per_image = matches[0].metadata if matches else None
            if context.metadata is not None:
                record = context.metadata.apply(record)
            if per_image is not None:
                record = per_image.apply(record)
            identity = record['image']['id']
            if identity in seen:
                raise ConversionError(f'Duplicate ISIR image ID: {identity!r}')
            seen.add(identity)
            batch.images[i] = record
        batch.metadata.update(deepcopy(context.dataset_metadata))
        if context.categories is not None:
            batch.metadata['categories'] = deepcopy(context.categories)
        if outgoing:
            if outgoing['mode'] == 'each':
                return [call(outgoing, ConversionBatch([r], batch.metadata), export_options) for r in batch.images]
            return call(outgoing, batch, export_options)
        if export_options:
            raise ConversionError('ISIR output does not accept export options')
        return batch.images[0] if cardinality == 'one' else batch.images
