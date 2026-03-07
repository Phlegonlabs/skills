#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

PLACEHOLDER_PREFIX = "<fill"
ERROR_TYPE: type[Exception] = RuntimeError
REPO_ROOT: Path | None = None


class YamlLine(NamedTuple):
    indent: int
    text: str
    lineno: int


def configure_context(
    *,
    error_type: type[Exception] = RuntimeError,
    repo_root: Path | None = None,
    placeholder_prefix: str = "<fill",
) -> None:
    global ERROR_TYPE, REPO_ROOT, PLACEHOLDER_PREFIX
    ERROR_TYPE = error_type
    REPO_ROOT = repo_root
    PLACEHOLDER_PREFIX = placeholder_prefix


def fail(message: str, code: int = 1) -> int:
    print(message, file=sys.stderr)
    return code


def raise_error(message: str, code: int = 1) -> None:
    try:
        raise ERROR_TYPE(message, code)  # type: ignore[misc]
    except TypeError:
        error = ERROR_TYPE(message)
        try:
            setattr(error, "code", code)
        except (AttributeError, TypeError):
            pass
        raise error


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise_error(f"missing required file: {label} -> {path}", 2)


def is_placeholder(value: object) -> bool:
    return isinstance(value, str) and value.strip().startswith(PLACEHOLDER_PREFIX)


def non_placeholder_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned or is_placeholder(cleaned):
        return None
    return cleaned


def parse_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def as_mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def split_flow_items(raw: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in raw:
        if quote is not None:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "[":
            depth += 1
            current.append(char)
            continue
        if char == "]" and depth > 0:
            depth -= 1
            current.append(char)
            continue
        if char == "," and depth == 0:
            items.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        items.append(tail)
    return items


def parse_scalar(raw: str) -> object:
    value = raw.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in split_flow_items(inner)]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def preprocess_yaml(text: str) -> list[YamlLine]:
    lines: list[YamlLine] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append(YamlLine(indent=indent, text=raw[indent:], lineno=lineno))
    return lines


def split_key_value(line: YamlLine, text: str) -> tuple[str, str]:
    if ":" not in text:
        raise_error(f"unsupported yaml syntax at line {line.lineno}: {text}", 2)
    key, rest = text.split(":", 1)
    return key.strip(), rest.strip()


def is_mapping_text(text: str) -> bool:
    return re.match(r"^[A-Za-z0-9_.\-/]+:\s*.*$", text) is not None


def parse_mapping_entries(
    lines: list[YamlLine],
    index: int,
    indent: int,
    mapping: dict[str, object],
    parent_list_indent: int | None = None,
) -> int:
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if parent_list_indent is not None and line.indent == parent_list_indent and line.text.startswith("-"):
            break
        if line.indent != indent or line.text.startswith("-"):
            raise_error(f"unsupported yaml indentation at line {line.lineno}: {line.text}", 2)
        key, rest = split_key_value(line, line.text)
        index += 1
        if rest:
            mapping[key] = parse_scalar(rest)
            continue
        if index < len(lines) and lines[index].indent > indent:
            child, index = parse_block(lines, index, lines[index].indent)
            mapping[key] = child
        else:
            mapping[key] = None
    return index


def parse_map(lines: list[YamlLine], index: int, indent: int) -> tuple[dict[str, object], int]:
    mapping: dict[str, object] = {}
    index = parse_mapping_entries(lines, index, indent, mapping)
    return mapping, index


def parse_list(lines: list[YamlLine], index: int, indent: int) -> tuple[list[object], int]:
    values: list[object] = []
    while index < len(lines):
        line = lines[index]
        if line.indent < indent or line.indent != indent or not line.text.startswith("-"):
            break
        content = line.text[1:].lstrip()
        index += 1
        if not content:
            if index < len(lines) and lines[index].indent > indent:
                value, index = parse_block(lines, index, lines[index].indent)
            else:
                value = None
            values.append(value)
            continue
        if is_mapping_text(content):
            item: dict[str, object] = {}
            key, rest = split_key_value(line, content)
            if rest:
                item[key] = parse_scalar(rest)
            elif index < len(lines) and lines[index].indent > indent:
                child, index = parse_block(lines, index, lines[index].indent)
                item[key] = child
            else:
                item[key] = None
            index = parse_mapping_entries(lines, index, indent + 2, item, parent_list_indent=indent)
            values.append(item)
            continue
        values.append(parse_scalar(content))
    return values, index


def parse_block(lines: list[YamlLine], index: int, indent: int) -> tuple[object, int]:
    if index >= len(lines):
        return {}, index
    line = lines[index]
    if line.indent != indent:
        raise_error(f"unsupported yaml indentation at line {line.lineno}: {line.text}", 2)
    if line.text.startswith("-"):
        return parse_list(lines, index, indent)
    return parse_map(lines, index, indent)


def parse_yaml_subset(text: str) -> object:
    lines = preprocess_yaml(text)
    if not lines:
        return {}
    value, index = parse_block(lines, 0, lines[0].indent)
    if index != len(lines):
        line = lines[index]
        raise_error(f"unsupported yaml trailing content at line {line.lineno}: {line.text}", 2)
    return value


def relative_label(path: Path) -> str:
    if REPO_ROOT is not None:
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            pass
    return str(path)


def read_yaml(path: Path) -> dict[str, object]:
    require_file(path, relative_label(path))
    data = parse_yaml_subset(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise_error(f"expected a yaml mapping in {path}", 2)
    return data


__all__ = [
    "YamlLine",
    "as_list",
    "as_mapping",
    "as_string_list",
    "configure_context",
    "fail",
    "is_mapping_text",
    "is_placeholder",
    "non_placeholder_string",
    "parse_block",
    "parse_int",
    "parse_list",
    "parse_map",
    "parse_mapping_entries",
    "parse_scalar",
    "parse_yaml_subset",
    "preprocess_yaml",
    "read_yaml",
    "require_file",
    "split_flow_items",
    "split_key_value",
]
