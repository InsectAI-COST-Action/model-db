import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "check_formats.py"
spec = importlib.util.spec_from_file_location("check_formats", SCRIPT)
schema = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema)


class SchemaTests(unittest.TestCase):
    def document(self):
        return {
            "types": {"point": ["T[number]", "T[number]"]},
            "enums": {"formats": ["png", "jpg"]},
            "structure": {
                "points": ["T[point]"],
                "format": "? : T[string](E[formats])",
                "tags": "? : [T[string]]",
                "identifier": "? : T[null] | T[UUIDv4]",
                "created": "T[ISO]",
            },
            "notes": {"example": {"format": "png"}},
        }

    def test_arrays_unions_enums_and_optional_fields(self):
        schema.validate(self.document())

    def test_undefined_and_malformed_expressions(self):
        for expression in (
            "T[str]",
            "T[missing]",
            "E[formats]",
            "T[string](E[missing])",
            "T[string(E[formats])",
            "T[string] |",
            "null",
            "Tensor[N,6]",
            "[T[number]",
            "? : ? : T[string]",
            "T[number] trailing",
        ):
            with self.subTest(expression=expression):
                doc = self.document()
                doc["structure"]["bad"] = expression
                with self.assertRaises(schema.FormatError):
                    schema.validate(doc)

    def test_literals_and_metadata_cannot_leak_into_structure(self):
        for value in (1, None, True, "example.jpg", []):
            doc = self.document()
            doc["structure"]["bad"] = value
            with self.subTest(value=value), self.assertRaises(schema.FormatError):
                schema.validate(doc)
        doc = self.document()
        doc["serialization"] = "application/json"
        with self.assertRaises(schema.FormatError):
            schema.validate(doc)

    def test_optional_is_not_nullable_or_a_repeated_item(self):
        for structure in (
            "? : T[string]",
            ["? : T[number]"],
            ["? : T[number]", "T[number]"],
        ):
            doc = self.document()
            doc["structure"] = structure
            with (
                self.subTest(structure=structure),
                self.assertRaises(schema.FormatError),
            ):
                schema.validate(doc)
        doc["structure"] = ["T[number]", "? : T[number]"]
        schema.validate(doc)

    def test_enum_compatibility_including_json_boolean_number_distinction(self):
        for values, expression in (
            ([True], "T[number](E[formats])"),
            ([{"value": 1}], "T[string](E[formats])"),
            ([], "T[string](E[formats])"),
            (["png", "png"], "T[string](E[formats])"),
            (["2026-09-30"], "T[ISO](E[formats])"),
            (["2026-02-30T00:00:00.000Z"], "T[ISO](E[formats])"),
            (["00000000-0000-0000-0000-000000000000"], "T[UUIDv4](E[formats])"),
        ):
            doc = self.document()
            doc["enums"]["formats"] = values
            doc["structure"] = expression
            with (
                self.subTest(values=values, expression=expression),
                self.assertRaises(schema.FormatError),
            ):
                schema.validate(doc)
        for name, value in (
            ("ISO", "2026-09-30T12:00:00.000Z"),
            ("UUIDv4", "123e4567-e89b-42d3-a456-426614174000"),
        ):
            doc["enums"]["formats"] = [value]
            doc["structure"] = f"T[{name}](E[formats])"
            schema.validate(doc)

    def test_numeric_type_distinctions(self):
        for name, accepted, rejected in (
            (
                "integer",
                [0, -2, 10**100, 1.0, "1", "3.0", "3e2"],
                [1.5, "1.5", True, "", "NaN"],
            ),
            (
                "float",
                [0.0, -2.5, 1.0, 1, "1.0", "0.1"],
                [True, 2**53 + 1, "1e999", "1e-999", float("inf"), float("nan")],
            ),
            (
                "number",
                [0, 1.0, -2.5, "1", "1.5"],
                [True, "not a number", float("inf")],
            ),
        ):
            for value in accepted:
                with self.subTest(name=name, value=value):
                    self.assertTrue(schema.compatible(value, name))
                    doc = self.document()
                    doc["enums"] = {"values": [value]}
                    doc["structure"] = f"T[{name}](E[values])"
                    schema.validate(doc)
            for value in rejected:
                with self.subTest(name=name, value=value):
                    self.assertFalse(schema.compatible(value, name))
        for name in ("integer", "float"):
            doc = self.document()
            doc["types"][name] = "T[number]"
            with self.assertRaises(schema.FormatError):
                schema.validate(doc)

    def test_catalog_declares_intended_numeric_casts(self):
        import json

        def load(name):
            return json.loads(
                (schema.DEFAULT_ROOT / f"{name}.json").read_text()
            )

        exported = load("ultralytics-detect-json")["types"]["instance"]
        self.assertEqual(exported["class"], "T[integer]")
        self.assertEqual(exported["confidence"], "T[float]")
        tensor = load("ultralytics-detect-results")["types"]["box_row"]
        self.assertEqual(tensor, ["T[float]"] * 5 + ["T[integer]"])
        tracked = load("ultralytics-detect-results")["types"]["tracked_box_row"]
        self.assertEqual(tracked[4], "T[integer]")
        self.assertEqual(load("flatbug")["structure"]["classes"], ["T[integer]"])
        self.assertEqual(load("coco")["types"]["box"], ["T[number]"] * 4)

    def test_safe_scalar_casts(self):
        for name, accepted, rejected in (
            (
                "boolean",
                [True, False, 0, 1.0, "False", "true", "0"],
                [2, "yes", "", None],
            ),
            ("string", ["text", 1, 1.5, False], [None, [], {}, float("inf")]),
            ("null", [None], ["null", 0, ""]),
        ):
            for value in accepted:
                with self.subTest(name=name, value=value):
                    self.assertTrue(schema.compatible(value, name))
            for value in rejected:
                with self.subTest(name=name, value=value):
                    self.assertFalse(schema.compatible(value, name))
        for value in ("3.5", "nan", True):
            doc = self.document()
            doc["enums"] = {"ids": [value]}
            doc["structure"] = "T[integer](E[ids])"
            with self.assertRaises(schema.FormatError):
                schema.validate(doc)

    def test_postfix_constraints_and_branch_binding(self):
        for expression in (
            "T[integer](0 | 1)",
            'T[integer]("3" | 4.0)',
            'T[integer](0) | T[string]("unknown")',
            "T[string](E[formats]) | T[null](null)",
            "T[boolean](true | false)",
            'T[string]("")',
            "[T[integer](0 | 1)]",
            "T[array]([0, 1] | [])",
            'T[object]({"name": "a|b)"})',
            'T[string]("x | y" | "z)")',
        ):
            with self.subTest(expression=expression):
                doc = self.document()
                doc["structure"] = expression
                schema.validate(doc)
        doc["structure"] = {"flags": "? : [T[integer](0 | 1)]"}
        schema.validate(doc)

    def test_invalid_postfix_constraints(self):
        for expression in (
            "T[string(E[formats])]",
            "T[string](E[missing])",
            "T[integer]()",
            "T[integer](0 |)",
            "T[integer](| 0)",
            "T[integer](0, 1)",
            "T[integer](0",
            "T[integer](0)(1)",
            'T[string](E[formats] | "gif")',
            'T[string]("gif" | E[formats])',
            "T[string](unquoted)",
            "T[integer](1.5)",
            'T[integer](0) | T[integer]("unknown")',
            "T[integer](0 | 0)",
            "T[float](NaN)",
            "T[float](1e999)",
            'T[object]({"a": 1, "a": 2})',
        ):
            with self.subTest(expression=expression):
                doc = self.document()
                doc["structure"] = expression
                with self.assertRaises(schema.FormatError):
                    schema.validate(doc)

    def test_documented_descriptor_examples(self):
        import json
        import re

        guide = (schema.DEFAULT_ROOT / "README.md").read_text()
        examples = re.findall(r"```json\n(.*?)\n```", guide, re.DOTALL)
        self.assertGreaterEqual(len(examples), 2)
        for example in examples:
            with self.subTest(example=example):
                schema.validate(json.loads(example))

    def test_higher_order_types_require_local_definitions(self):
        doc = self.document()
        doc["types"] = {
            "features": ["T[feature]"],
            "feature": {"outline": "T[polyline]", "label": "? : T[string]"},
            "polyline": ["T[point]"],
            "point": ["T[float]", "T[float]"],
        }
        doc["structure"] = "T[features]"
        schema.validate(doc)
        del doc["types"]["point"]
        with self.assertRaisesRegex(schema.FormatError, r"undefined type T\[point\]"):
            schema.validate(doc)

    def test_json_and_expression_repetition_compose(self):
        for node in (
            ["T[float]"],
            "[T[float]]",
            [["T[float]", "T[float]"]],
            [["T[float]"], ["T[float]"]],
            "[[T[float]]]",
        ):
            doc = self.document()
            doc["structure"] = node
            with self.subTest(node=node):
                schema.validate(doc)
        doc["structure"] = "[T[float], T[float]]"
        with self.assertRaises(schema.FormatError):
            schema.validate(doc)

    def test_duplicate_keys_and_non_json_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            for text in ('{"types": {}, "types": {}}', '{"value": NaN}'):
                path.write_text(text)
                with self.assertRaises(schema.FormatError):
                    schema.check_file(path)

    def test_builtin_names_are_reserved(self):
        doc = self.document()
        doc["types"]["string"] = "T[number]"
        with self.assertRaises(schema.FormatError):
            schema.validate(doc)

    def test_catalog(self):
        files = list(schema.DEFAULT_ROOT.rglob("*.json"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=path):
                schema.check_file(path)


if __name__ == "__main__":
    unittest.main()
