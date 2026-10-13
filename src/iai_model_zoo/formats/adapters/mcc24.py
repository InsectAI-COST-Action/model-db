"""MCC24 author CSV -> detections; classifier outputs remain native metadata."""
import csv
from copy import deepcopy
from io import StringIO

from ..schema import FormatError
from ._common import record, schema
from ._inputs import collection, xyxy_to_ir


def to_ir_many(data, *, images, include_empty=False):
    """Manifest keys are exact fileName values; detector confidence is percent."""
    descriptor = schema('mcc24-csv')
    if isinstance(data, str):
        reader = csv.DictReader(StringIO(data))
        if reader.fieldnames != descriptor.notes['header']:
            raise FormatError('mcc24: CSV header does not match the author profile')
        data = list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in data):
            raise FormatError('mcc24: CSV row length does not match the header')
    rows = descriptor.cast(data)
    grouped = {}
    for row in rows:
        grouped.setdefault(row['fileName'], []).append(row)

    def convert(rows, context):
        info = context.image()
        if rows and 'file_name' not in info:
            info['file_name'] = rows[0]['fileName']
        instances = []
        for row in rows:
            if not 0 <= row['detectConf'] <= 100:
                raise FormatError('mcc24: detectConf must lie between zero and 100')
            instances.append(dict(id=row['key'],
                bbox=xyxy_to_ir([row[k] for k in ('x1','y1','x2','y2')], info),
                confidence=row['detectConf'] / 100,
                extra_information={'mcc24': deepcopy(row)}))
        return record(info, instances, context.metadata)

    return collection(grouped, images, convert, include_empty=include_empty)


def import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    return ConversionBatch(invoke(to_ir_many, data, options, images=context.images))
