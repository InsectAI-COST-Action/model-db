"""Behavioral tests for compilation, casting, and conversion through a data IR."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from iai_model_zoo.formats.schema import (  # noqa: E402
    Array,
    Constrained,
    FormatError,
    Object,
    Primitive,
    Schema,
    Tuple,
    convert,
)


def descriptor(structure, types=None, enums=None):
    return {
        "types": types or {},
        "enums": enums or {},
        "structure": structure,
        "notes": {},
    }


class IRTests(unittest.TestCase):
    def test_library_injection_override_and_input_isolation(self):
        doc = descriptor("T[float_quad]")
        snapshot = deepcopy(doc)
        compiled = Schema.from_dict(doc)
        self.assertEqual(doc, snapshot)
        self.assertEqual(compiled.structure, Tuple((Primitive("float"),) * 4))
        self.assertEqual(compiled.cast(["1", 2, 3, 4]), [1.0, 2.0, 3.0, 4.0])
        local = Schema.from_dict(
            descriptor("T[float_quad]", {"float_quad": "T[string]"})
        )
        self.assertEqual(local.cast("local"), "local")
        with self.assertRaisesRegex(FormatError, "undefined type"):
            Schema.from_dict(doc, shared_types={})
        custom = Schema.from_dict(
            descriptor("T[count]"), shared_types={"count": "T[integer]"}
        )
        self.assertEqual(custom.cast("3.0"), 3)
        with self.assertRaisesRegex(FormatError, "reserved"):
            Schema.from_dict(doc, shared_types={"float": "T[string]"})

    def test_forward_references_and_cycles(self):
        schema = Schema.from_dict(
            descriptor("T[rows]", {"rows": ["T[row]"], "row": {"id": "T[integer]"}})
        )
        self.assertIsInstance(schema.structure, Array)
        self.assertIsInstance(schema.structure.item, Object)
        self.assertIs(schema.structure, schema.types["rows"])
        for types in ({"a": "T[b]", "b": "T[a]"}, {"a": ["T[a]"]}):
            with self.assertRaisesRegex(FormatError, "cyclic type definitions"):
                Schema.from_dict(descriptor("T[a]", types))

    def test_nested_cast_paths_missing_null_and_preserved_extras(self):
        schema = Schema.from_dict(
            descriptor(
                {
                    "rows": [{"id": "T[integer]", "label": "? : T[string]"}],
                    "nullable": "T[null] | T[integer]",
                }
            )
        )
        original = {
            "rows": [{"id": "3", "extra": [1]}],
            "nullable": None,
            "other": {"value": [2]},
        }
        result = schema.cast(original)
        self.assertEqual(result["rows"][0]["id"], 3)
        self.assertNotIn("label", result["rows"][0])
        result["other"]["value"].append(3)
        result["rows"][0]["extra"].append(2)
        self.assertEqual(original["other"]["value"], [2])
        self.assertEqual(original["rows"][0]["extra"], [1])
        with self.assertRaisesRegex(FormatError, r"\$\.rows\[0\]\.id"):
            schema.cast({"rows": [{"id": 1.5}], "nullable": None})
        with self.assertRaisesRegex(FormatError, "missing required field"):
            schema.cast({"rows": []})
        original["rows"][0]["label"] = None
        with self.assertRaisesRegex(FormatError, "label"):
            schema.cast(original)

    def test_alias_constraints_are_checked_and_cast_before_comparison(self):
        doc = descriptor(
            "T[count](E[choices])", {"count": "T[integer]"}, {"choices": ["3", 4.0]}
        )
        schema = Schema.from_dict(doc)
        self.assertIsInstance(schema.structure, Constrained)
        self.assertEqual(schema.cast("3.0"), 3)
        doc["enums"]["choices"].append(5)
        with self.assertRaisesRegex(FormatError, "outside allowed"):
            schema.cast(5)
        with self.assertRaisesRegex(FormatError, "cannot safely cast"):
            Schema.from_dict(descriptor("T[count](1.5)", {"count": "T[integer]"}))
        pair = Schema.from_dict(descriptor("T[float_pair]([1, 2])"))
        self.assertEqual(pair.cast(("1", 2)), [1.0, 2.0])
        with self.assertRaisesRegex(FormatError, "outside allowed"):
            pair.cast([1, 3])

    def test_unions_preserve_already_typed_values_and_reject_ambiguity(self):
        schema = Schema.from_dict(descriptor("T[integer] | T[string]"))
        self.assertEqual(schema.cast("3"), "3")
        self.assertEqual(schema.cast(3), 3)
        with self.assertRaisesRegex(FormatError, "ambiguous union"):
            Schema.from_dict(descriptor("T[integer] | T[float]")).cast("3")
        with self.assertRaisesRegex(FormatError, "no union branch"):
            Schema.from_dict(descriptor("T[integer] | T[null]")).cast("bad")

    def test_tuple_length_and_ambiguous_optional_columns(self):
        schema = Schema.from_dict(
            descriptor(["T[integer]", "? : T[float]", "? : T[integer]"])
        )
        self.assertEqual(schema.cast([1]), [1])
        self.assertEqual(schema.cast([1, 0.9]), [1, 0.9])
        self.assertEqual(schema.cast([1, 0.9, 7]), [1, 0.9, 7])
        for value in ([], [1, 0.9, 7, 8]):
            with self.assertRaisesRegex(FormatError, "tuple positions"):
                schema.cast(value)
        with self.assertRaisesRegex(FormatError, "ambiguous optional tuple"):
            schema.cast([1, 1])

    def test_conversion_through_common_ir_with_explicit_coordinates(self):
        formats = ROOT / "static/formats"
        source = Schema.load(formats / "yolov5-detect-txt.json")
        target = Schema.load(formats / "ultralytics-detect-json.json")
        ir = Schema.from_dict(
            descriptor(
                [
                    {
                        "class_id": "T[integer]",
                        "xyxy": "T[float_quad]",
                        "score": "T[float]",
                    }
                ]
            )
        )

        # The adapter knows input dimensions and the enabled confidence column.
        def to_ir(rows):
            return [
                {
                    "class_id": cls,
                    "xyxy": [
                        (x - w / 2) * 100,
                        (y - h / 2) * 80,
                        (x + w / 2) * 100,
                        (y + h / 2) * 80,
                    ],
                    "score": score,
                }
                for cls, x, y, w, h, score in rows
            ]

        def from_ir(rows):
            return [
                {
                    "name": {0: "insect"}[r["class_id"]],
                    "class": r["class_id"],
                    "confidence": r["score"],
                    "box": dict(zip(("x1", "y1", "x2", "y2"), r["xyxy"])),
                }
                for r in rows
            ]

        rows = [["0", ".5", ".5", ".2", ".5", ".9"]]
        intermediate = convert(rows, source, ir, to_ir)
        result = convert(intermediate, ir, target, from_ir)
        self.assertEqual(
            result,
            [
                {
                    "name": "insect",
                    "class": 0,
                    "confidence": 0.9,
                    "box": {"x1": 40.0, "y1": 20.0, "x2": 60.0, "y2": 60.0},
                }
            ],
        )
        self.assertEqual(rows[0][0], "0")
        with self.assertRaisesRegex(FormatError, "missing required field"):
            convert(intermediate, ir, target, lambda rows: [{}])

    def test_primitives_do_not_silently_truncate_or_overflow(self):
        for target, value in [
            ("integer", "1.5"),
            ("float", "1e999"),
            ("float", 2**53 + 1),
            ("float", "1e-999"),
            ("boolean", "anything"),
        ]:
            with (
                self.subTest(target=target, value=value),
                self.assertRaises(FormatError),
            ):
                Schema.from_dict(descriptor(f"T[{target}]")).cast(value)
        self.assertIs(Schema.from_dict(descriptor("T[boolean]")).cast("False"), False)
        self.assertEqual(Schema.from_dict(descriptor("T[number]")).cast("3"), 3)
        self.assertEqual(Schema.from_dict(descriptor("T[number]")).cast(".5"), 0.5)


if __name__ == "__main__":
    unittest.main()
