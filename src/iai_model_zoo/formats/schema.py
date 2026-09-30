"""Compile format descriptors to a small type IR and cast decoded Python data.

File/tensor decoding and semantic transformations belong to explicit adapters.
Only the standard library is required. See README.md alongside this module.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from itertools import combinations
import json
import math
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any
from uuid import UUID

BASE_TYPES = {
    "string",
    "number",
    "boolean",
    "null",
    "object",
    "array",
    "ISO",
    "UUIDv4",
    "integer",
    "float",
}
NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9]*\Z")
REFERENCE = re.compile(r"T\[([A-Za-z_][A-Za-z_0-9]*)\]")
ENUM_REFERENCE = re.compile(r"E\[([A-Za-z_][A-Za-z_0-9]*)\]")


def compatible(value, name):
    """Check conservative, meaning-preserving casts of constraint options."""
    if name in {"integer", "float", "number"}:
        if type(value) not in (int, float, str):
            return False
        text = str(value).strip()
        if not re.fullmatch(
            r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", text
        ):
            return False
        try:
            numeric = Decimal(text)
        except InvalidOperation:
            return False
        if not numeric.is_finite():
            return False
        if name == "integer":
            return numeric == numeric.to_integral_value()
        if name == "number":
            return True
        converted = float(numeric)
        if not math.isfinite(converted) or (converted == 0 and numeric != 0):
            return False
        # Ordinary fractional rounding is expected for floats; integral IDs
        # must not silently change value when cast to the checker's binary64.
        return numeric != numeric.to_integral_value() or Decimal(converted) == numeric
    if name == "string":
        return (
            isinstance(value, str)
            or type(value) in (int, bool)
            or (type(value) is float and math.isfinite(value))
        )
    if name == "boolean":
        return (
            type(value) is bool
            or (type(value) in (int, float) and value in (0, 1))
            or (isinstance(value, str) and value.lower() in ("true", "false", "0", "1"))
        )
    if name in {"ISO", "UUIDv4"}:
        if not isinstance(value, str):
            return False
        try:
            if name == "ISO":
                return bool(
                    re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", value)
                ) and bool(datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ"))
            return (
                bool(
                    re.fullmatch(
                        r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", value
                    )
                )
                and UUID(value).version == 4
            )
        except ValueError:
            return False
    return (
        type(value)
        is {
            "string": str,
            "boolean": bool,
            "null": type(None),
            "object": dict,
            "array": list,
        }[name]
    )


class FormatError(ValueError):
    pass


@dataclass(frozen=True)
class Primitive:
    name: str


@dataclass(frozen=True)
class Array:
    item: Type


@dataclass(frozen=True)
class Tuple:
    items: tuple[Type, ...]


@dataclass(frozen=True)
class Object:
    fields: tuple[tuple[str, Type], ...]


@dataclass(frozen=True)
class Union:
    options: tuple[Type, ...]


@dataclass(frozen=True)
class Optional:
    inner: Type


@dataclass(frozen=True)
class Constrained:
    inner: Type
    values: tuple[Any, ...]


Type = Primitive | Array | Tuple | Object | Union | Optional | Constrained


def _same(a, b):
    """Equality that preserves numeric and container type distinctions."""
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def _choose(results, value, path):
    for result in results:
        if _same(result, value):
            return result
    first = results[0]
    if all(_same(first, result) for result in results[1:]):
        return first
    raise FormatError(
        f"{path}: ambiguous union cast; specialize the schema or use an adapter"
    )


def cast(node: Type, value: Any, path: str = "$") -> Any:
    """Return a fresh normalized value, or a path-qualified FormatError."""

    def fail(message):
        raise FormatError(f"{path}: {message}")

    if isinstance(node, Primitive):
        name = node.name
        if not compatible(value, name):
            fail(f"cannot safely cast {value!r} to {name}")
        if name in {"integer", "float", "number"}:
            numeric = Decimal(str(value).strip())
            if name == "integer":
                return int(numeric)
            if name == "float":
                return float(numeric)
            if type(value) in (int, float):
                return value
            if numeric == numeric.to_integral_value():
                return int(numeric)
            if not compatible(value, "float"):
                fail("number cannot be represented as a finite Python float")
            return float(numeric)
        if name == "string":
            return str(value).lower() if type(value) is bool else str(value)
        if name == "boolean":
            return (
                value.lower() in ("true", "1")
                if isinstance(value, str)
                else bool(value)
            )
        return deepcopy(value)
    if isinstance(node, Optional):
        return cast(node.inner, value, path)
    if isinstance(node, Constrained):
        result = cast(node.inner, value, path)
        if not any(_same(result, option) for option in node.values):
            fail(f"value is outside allowed values {node.values!r}")
        return result
    if isinstance(node, Object):
        if not isinstance(value, Mapping):
            fail("expected a decoded object/mapping")
        # Preserve unlisted data, including fields in partial API profiles.
        result = deepcopy(dict(value))
        for name, field in node.fields:
            if name not in value:
                if isinstance(field, Optional):
                    continue
                raise FormatError(f"{path}.{name}: missing required field")
            result[name] = cast(field, value[name], f"{path}.{name}")
        return result
    if isinstance(node, (Array, Tuple)):
        if not isinstance(value, (list, tuple)):
            fail("expected a decoded array (list or tuple)")
        if isinstance(node, Array):
            return [cast(node.item, v, f"{path}[{i}]") for i, v in enumerate(value)]
        required = sum(not isinstance(item, Optional) for item in node.items)
        if not required <= len(value) <= len(node.items):
            fail(
                f"expected {required}..{len(node.items)} tuple positions, got {len(value)}"
            )
        results = []
        errors = []
        for suffix in combinations(
            range(required, len(node.items)), len(value) - required
        ):
            layout = (*range(required), *suffix)
            try:
                results.append(
                    [
                        cast(node.items[k], v, f"{path}[{i}]")
                        for i, (k, v) in enumerate(zip(layout, value))
                    ]
                )
            except FormatError as exc:
                errors.append(str(exc))
        if not results:
            fail("no tuple layout matches: " + "; ".join(errors))
        if len(results) > 1:
            fail(
                "ambiguous optional tuple positions; specialize using producer settings"
            )
        return results[0]
    if isinstance(node, Union):
        results, errors = [], []
        for option in node.options:
            try:
                results.append(cast(option, value, path))
            except FormatError as exc:
                errors.append(str(exc))
        if not results:
            fail("no union branch matches: " + "; ".join(errors))
        return _choose(results, value, path)
    raise TypeError(f"Unknown IR node: {node!r}")


@dataclass(frozen=True)
class Schema:
    structure: Type
    types: Mapping[str, Type]
    notes: Mapping[str, Any]

    @classmethod
    def from_dict(
        cls, document: dict, *, shared_types: Mapping[str, Any] | None = None
    ) -> Schema:
        """Compile a descriptor. Local definitions override the injected library.

        None loads the bundled library; {} disables it. Inputs are not mutated.
        """
        if not isinstance(document, dict):
            raise FormatError("$: format descriptor must be an object")
        library = (
            shared_types
            if shared_types is not None
            else load_json(Path(__file__).with_name("shared_types.json"))
        )
        return _Compiler(deepcopy(document), deepcopy(dict(library))).compile()

    @classmethod
    def load(cls, path: str | Path, **kwargs) -> Schema:
        return cls.from_dict(load_json(path), **kwargs)

    def cast(self, value: Any) -> Any:
        return cast(self.structure, value)


def convert(
    value: Any, source: Schema, target: Schema, transform: Callable[[Any], Any]
) -> Any:
    """Cast source, apply an explicit semantic mapping, then cast target.

    For a common data IR, compose source -> IR and IR -> target conversions.
    """
    return target.cast(transform(source.cast(value)))


class _Compiler:
    def __init__(self, document, shared_types):
        self.document = document
        self.types = shared_types
        local = document.get("types", {})
        if isinstance(local, dict):
            self.types.update(local)
        self.resolved = {}
        self.resolving = []
        self.enums = document.get("enums", {})

    def fail(self, path, message):
        raise FormatError(f"{path}: {message}")

    def reference(self, name, path):
        if name in BASE_TYPES:
            return Primitive(name)
        if name not in self.types:
            self.fail(path, f"undefined type T[{name}]")
        if name in self.resolving:
            self.fail(
                path, "cyclic type definitions: " + " -> ".join([*self.resolving, name])
            )
        if name not in self.resolved:
            self.resolving.append(name)
            self.resolved[name] = self.node(self.types[name], f"types.{name}")
            self.resolving.pop()
        return self.resolved[name]

    def expression(self, text, path, optional):
        is_optional = text.startswith("? : ")
        if is_optional:
            if not optional:
                self.fail(
                    path, "optional marker is only allowed on fields or tuple positions"
                )
            text = text[4:]
        position = 0

        def whitespace():
            nonlocal position
            while position < len(text) and text[position].isspace():
                position += 1

        def constraint(inner):
            nonlocal position
            position += 1  # opening parenthesis
            whitespace()
            enum = ENUM_REFERENCE.match(text, position)
            if enum:
                name = enum.group(1)
                if name not in self.enums:
                    self.fail(path, f"undefined enum E[{name}]")
                values = self.enums[name]
                position = enum.end()
                whitespace()
            else:
                decoder = json.JSONDecoder(
                    object_pairs_hook=unique_object, parse_constant=reject_constant
                )
                values = []
                while True:
                    try:
                        value, position = decoder.raw_decode(text, position)
                        json.dumps(value, allow_nan=False)
                    except ValueError as exc:
                        self.fail(
                            path, f"expected a finite JSON literal in constraint: {exc}"
                        )
                    values.append(value)
                    whitespace()
                    if position >= len(text) or text[position] != "|":
                        break
                    position += 1
                    whitespace()
                encoded = [json.dumps(v, sort_keys=True) for v in values]
                if len(set(encoded)) != len(encoded):
                    self.fail(path, "duplicate literal constraint options")
            if position >= len(text) or text[position] != ")":
                self.fail(path, "expected closing ) after constraint")
            position += 1
            # Constraints on aliases and containers use the same cast as data.
            normalized = tuple(cast(inner, value, path) for value in values)
            return Constrained(inner, normalized)

        def term():
            nonlocal position
            whitespace()
            match = REFERENCE.match(text, position)
            if match:
                name = match.group(1)
                result = self.reference(name, path)
                position = match.end()
                whitespace()
                if position < len(text) and text[position] == "(":
                    result = constraint(result)
            elif position < len(text) and text[position] == "[":
                position += 1
                result = Array(union())
                if position >= len(text) or text[position] != "]":
                    self.fail(path, "expected closing ] for repeated-item array")
                position += 1
            else:
                self.fail(
                    path, f"expected T[name] or [expression] at {text[position:]!r}"
                )
            whitespace()
            return result

        def union():
            nonlocal position
            options = [term()]
            while position < len(text) and text[position] == "|":
                position += 1
                options.append(term())
            return options[0] if len(options) == 1 else Union(tuple(options))

        result = union()
        if position != len(text):
            self.fail(path, f"unexpected text {text[position:]!r}")
        return Optional(result) if is_optional else result

    def node(self, node, path, optional=False):
        if isinstance(node, str):
            return self.expression(node, path, optional)
        elif isinstance(node, dict):
            return Object(
                tuple(
                    (name, self.node(value, f"{path}.{name}", optional=True))
                    for name, value in node.items()
                )
            )
        elif isinstance(node, list):
            if not node:
                self.fail(
                    path, "empty schema array; use T[array] for an unspecified array"
                )
            items = []
            saw_optional = False
            for index, value in enumerate(node):
                is_optional = isinstance(value, str) and value.startswith("? : ")
                if saw_optional and not is_optional:
                    self.fail(
                        path,
                        "required tuple positions cannot follow optional positions",
                    )
                saw_optional |= is_optional
                items.append(
                    self.node(value, f"{path}[{index}]", optional=len(node) > 1)
                )
            return Array(items[0]) if len(items) == 1 else Tuple(tuple(items))
        else:
            self.fail(
                path,
                "expected a type expression, field object, or schema array; literals belong in constraints, enums or notes",
            )

    def compile(self):
        expected = {"types", "enums", "structure", "notes"}
        if set(self.document) != expected:
            self.fail(
                "$", f"expected exactly {sorted(expected)}; got {sorted(self.document)}"
            )
        for name in ("types", "enums", "notes"):
            if not isinstance(self.document[name], dict):
                self.fail(name, "must be an object")
        for name in self.types:
            if not NAME.fullmatch(name) or name in BASE_TYPES:
                self.fail("types", f"invalid or reserved type name {name!r}")
        for name, values in self.enums.items():
            if not NAME.fullmatch(name):
                self.fail("enums", f"invalid enum name {name!r}")
            if not isinstance(values, list) or not values:
                self.fail(f"enums.{name}", "must be a nonempty array of JSON options")
            encoded = [json.dumps(v, sort_keys=True, allow_nan=False) for v in values]
            if len(set(encoded)) != len(encoded):
                self.fail(f"enums.{name}", "duplicate options")
        for name, value in self.types.items():
            self.reference(name, f"types.{name}")
        structure = self.node(self.document["structure"], "structure")
        return Schema(
            structure,
            MappingProxyType(self.resolved),
            MappingProxyType(self.document["notes"]),
        )


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise FormatError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value):
    raise FormatError(f"{value} is not a JSON value")


def load_json(path: str | Path):
    return json.loads(
        Path(path).read_text(),
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
    )
