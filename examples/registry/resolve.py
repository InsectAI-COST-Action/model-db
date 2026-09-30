"""Inspect database-defined conversion plans; never run model code."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.registry import Registry, RegistryError, SelectionError  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--snapshot", type=Path, default=ROOT)
parser.add_argument("--model", required=True)
parser.add_argument("--source")
parser.add_argument("--cardinality", choices=["one", "collection"])
parser.add_argument("--target", default="isir")
parser.add_argument("--query", action="store_true", help="List all candidates instead of selecting a default")
args = parser.parse_args()
try:
    registry = Registry.open(args.snapshot)
    kwargs = dict(model=args.model, source=args.source, cardinality=args.cardinality,
                  target=args.target)
    result = registry.query(**kwargs) if args.query else registry.resolve(**kwargs)
    print(json.dumps(result, indent=2))
except SelectionError as error:
    print(json.dumps(dict(error=str(error), candidates=error.candidates), indent=2))
    sys.exit(2)
except RegistryError as error:
    parser.error(str(error))
