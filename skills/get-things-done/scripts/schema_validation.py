from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any


class SchemaValidationError(ValueError):
    pass


def _path(parent: str, key: str | int) -> str:
    if isinstance(key, int):
        return f"{parent}[{key}]"
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
        return f"{parent}.{key}"
    return f"{parent}[{json.dumps(key)}]"


def _is_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise SchemaValidationError(f"unsupported schema type: {expected}")


def _resolve_local_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        raise SchemaValidationError(f"remote or unsupported schema reference: {ref}")
    name = ref[len(prefix):]
    defs = root.get("$defs")
    if not isinstance(defs, dict) or not isinstance(defs.get(name), dict):
        raise SchemaValidationError(f"unresolved local schema reference: {ref}")
    return defs[name]


def _valid_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate(value: Any, schema: dict[str, Any], root: dict[str, Any], path: str, errors: list[str]) -> None:
    if "$ref" in schema:
        target = _resolve_local_ref(root, str(schema["$ref"]))
        _validate(value, target, root, path, errors)
        return

    if "anyOf" in schema:
        options = schema.get("anyOf")
        if not isinstance(options, list):
            raise SchemaValidationError("anyOf must be an array")
        for option in options:
            if not isinstance(option, dict):
                raise SchemaValidationError("anyOf entries must be objects")
            candidate: list[str] = []
            _validate(value, option, root, path, candidate)
            if not candidate:
                break
        else:
            errors.append(f"{path}: value does not match any allowed schema")
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']!r}")

    expected = schema.get("type")
    if expected is not None:
        allowed = [expected] if isinstance(expected, str) else list(expected)
        if not any(_is_type(value, item) for item in allowed):
            errors.append(f"{path}: expected type {' or '.join(allowed)}")
            return

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}: string is shorter than {min_length}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}: does not match required pattern {pattern!r}")
        if schema.get("format") == "date-time" and not _valid_datetime(value):
            errors.append(f"{path}: must be a valid date-time")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{path}: must be >= {minimum}")
        exclusive = schema.get("exclusiveMinimum")
        if isinstance(exclusive, (int, float)) and value <= exclusive:
            errors.append(f"{path}: must be > {exclusive}")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}: requires at least {min_items} item(s)")
        if schema.get("uniqueItems") is True:
            seen: set[str] = set()
            for index, item in enumerate(value):
                marker = _canonical(item)
                if marker in seen:
                    errors.append(f"{_path(path, index)}: duplicate array item")
                seen.add(marker)
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate(item, item_schema, root, _path(path, index), errors)

    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    errors.append(f"{_path(path, str(key))}: required property is missing")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        for key, item in value.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                _validate(item, child_schema, root, _path(path, key), errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{_path(path, key)}: additional property is not allowed")


def validate_instance(instance: Any, schema: dict[str, Any]) -> list[str]:
    if not isinstance(schema, dict):
        raise SchemaValidationError("schema must be an object")
    errors: list[str] = []
    _validate(instance, schema, schema, "$", errors)
    return errors
