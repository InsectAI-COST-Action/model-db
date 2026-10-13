"""BioMoth batch measurement CSV -> a collection of single-image ISIR records."""

import csv
from copy import deepcopy
from io import StringIO

from ..schema import FormatError
from ._common import record, schema
from ._inputs import collection, xyxy_to_ir


def to_ir(data, *, images, include_empty=False):
    """Accept CSV text or decoded row mappings; group by exact filePath.

    images maps filePath to ImageContext (never basenames). include_empty=True
    asserts that manifest images without rows are known completed empty results.
    """
    if isinstance(data, str):
        reader = csv.DictReader(StringIO(data))
        if reader.fieldnames != schema("biomoth-csv").notes["header"]:
            raise FormatError("biomoth: CSV header does not match the author profile")
        data = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in data):
            raise FormatError("biomoth: CSV row length does not match the header")
    rows = schema("biomoth-csv").cast(data)
    grouped = {}
    for row in rows:
        grouped.setdefault(row["filePath"], []).append(row)

    def convert(rows, context):
        info = context.image()
        if rows and "file_name" not in info:
            info["file_name"] = rows[0]["filePath"]
        instances = []
        for i, row in enumerate(rows):
            instances.append(dict(
                id=i,
                bbox=xyxy_to_ir([row[k] for k in ("X_Min", "Y_Min", "X_Max", "Y_Max")], info),
                category_id=row["class"], confidence=row["confidence"],
                # Preserve measurements in native units; size is cm², not ISIR area.
                extra_information={"biomoth": deepcopy(row)},
            ))
        return record(info, instances, context.metadata)

    return collection(grouped, images, convert, include_empty=include_empty)


# Uniform conversion interface; direct APIs above remain supported.

def import_collection(data, *, context, options, source):
    from ..conversion import ConversionBatch, invoke
    result = invoke(to_ir, data, options, images=context.images)
    return ConversionBatch(result)
