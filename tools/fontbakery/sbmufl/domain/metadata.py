from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, cast

from ..constants import (
    DOCS_TABLE_ROW_RE,
    DOCS_TABLES_PATH,
    GLYPHNAMES_PATH,
    NEANES_METADATA_PATH,
    RANGES_PATH,
    REPO_ROOT,
    SBMUFL_OPTIONAL_GLYPHS,
    expected_by_name,
    parse_namelist,
)


def _load_json(
    path: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        with path.open(encoding="utf-8") as infile:
            return cast(dict[str, Any], json.load(infile)), []
    except FileNotFoundError:
        return None, [f"Missing file: {path.relative_to(REPO_ROOT)}"]
    except json.JSONDecodeError as e:
        return None, [
            f"Invalid JSON in {path.relative_to(REPO_ROOT)}: "
            f"line {e.lineno}, column {e.colno}"
        ]


def _compare_glyph_map(
    label: str,
    actual_by_name: Mapping[str, int],
    expected_by_name: Mapping[str, int],
) -> list[str]:
    problems: list[str] = []
    missing = [
        f"U+{codepoint:04X} {glyph_name}"
        for glyph_name, codepoint in sorted(
            expected_by_name.items(), key=lambda item: item[1]
        )
        if glyph_name not in actual_by_name
    ]
    extra = [
        f"U+{codepoint:04X} {glyph_name}"
        for glyph_name, codepoint in sorted(
            actual_by_name.items(), key=lambda item: item[1]
        )
        if glyph_name not in expected_by_name
    ]
    mismatched = [
        f"{glyph_name}: expected U+{expected_by_name[glyph_name]:04X}, "
        f"found U+{actual_by_name[glyph_name]:04X}"
        for glyph_name in sorted(set(actual_by_name).intersection(expected_by_name))
        if actual_by_name[glyph_name] != expected_by_name[glyph_name]
    ]

    if missing:
        problems.append(f"{label} is missing glyphs:\n{chr(10).join(missing)}")
    if extra:
        problems.append(f"{label} contains unknown glyphs:\n{chr(10).join(extra)}")
    if mismatched:
        problems.append(
            f"{label} has codepoint mismatches:\n{chr(10).join(mismatched)}"
        )

    return problems


def _compare_name_set(
    label: str,
    actual_names: Iterable[str],
    expected_by_name: Mapping[str, int],
) -> list[str]:
    problems: list[str] = []
    actual_names = set(actual_names)
    missing = [
        f"U+{codepoint:04X} {glyph_name}"
        for glyph_name, codepoint in sorted(
            expected_by_name.items(), key=lambda item: item[1]
        )
        if glyph_name not in actual_names
    ]
    extra = sorted(actual_names - set(expected_by_name))

    if missing:
        problems.append(f"{label} is missing glyphs:\n{chr(10).join(missing)}")
    if extra:
        problems.append(f"{label} contains unknown glyphs:\n{chr(10).join(extra)}")

    return problems


def _parse_docs_tables() -> tuple[list[tuple[Path, int, str]], list[str]]:
    entries: list[tuple[Path, int, str]] = []
    problems: list[str] = []
    if not DOCS_TABLES_PATH.exists():
        problems.append(f"Missing directory: {DOCS_TABLES_PATH.relative_to(REPO_ROOT)}")
        return entries, problems

    for path in sorted(DOCS_TABLES_PATH.glob("*.md")):
        if path.name == "index.md":
            continue
        text = path.read_text(encoding="utf-8")
        for match in DOCS_TABLE_ROW_RE.finditer(text):
            span_codepoint = int(match.group(1), 16)
            listed_codepoint = int(match.group(2).removeprefix("U+"), 16)
            glyph_name = match.group(3).strip()
            relative_path = path.relative_to(REPO_ROOT)
            if span_codepoint != listed_codepoint:
                problems.append(
                    f"{relative_path}: span U+{span_codepoint:04X} does not match "
                    f"listed U+{listed_codepoint:04X} for {glyph_name}"
                )
            entries.append((relative_path, listed_codepoint, glyph_name))

    return entries, problems


def _check_docs_tables() -> list[str]:
    problems: list[str] = []
    expected_names = expected_by_name(include_optional=True)
    entries, table_problems = _parse_docs_tables()
    problems.extend(table_problems)
    actual_by_name: dict[str, int] = {}

    name_counts = Counter(glyph_name for _, _, glyph_name in entries)
    codepoint_counts = Counter(codepoint for _, codepoint, _ in entries)
    for relative_path, codepoint, glyph_name in entries:
        actual_by_name[glyph_name] = codepoint

    duplicates = [
        f"{glyph_name} appears {count} times"
        for glyph_name, count in sorted(name_counts.items())
        if count > 1
    ]
    duplicate_codepoints = [
        f"U+{codepoint:04X} appears {count} times"
        for codepoint, count in sorted(codepoint_counts.items())
        if count > 1
    ]
    if duplicates:
        problems.append(
            f"docs/tables has duplicate glyph names:\n{chr(10).join(duplicates)}"
        )
    if duplicate_codepoints:
        problems.append(
            f"docs/tables has duplicate codepoints:\n{chr(10).join(duplicate_codepoints)}"
        )

    problems.extend(
        _compare_glyph_map("docs/tables/*.md", actual_by_name, expected_names)
    )
    return problems


def _check_glyphnames_json() -> list[str]:
    problems: list[str] = []
    expected_names = expected_by_name(include_optional=True)
    glyphnames, json_problems = _load_json(GLYPHNAMES_PATH)
    problems.extend(json_problems)
    if glyphnames is None:
        return problems
    if not isinstance(glyphnames, dict):
        problems.append("metadata/glyphnames.json root is not an object")
        return problems

    actual_by_name: dict[str, int] = {}
    codepoint_counts: Counter[int] = Counter()
    for glyph_name, data in glyphnames.items():
        if not isinstance(glyph_name, str):
            problems.append("metadata/glyphnames.json has a non-string glyph name")
            continue
        if not isinstance(data, dict):
            problems.append(
                f"metadata/glyphnames.json entry for {glyph_name} is not an object"
            )
            continue

        codepoint = data.get("codepoint")
        if not isinstance(codepoint, str) or not codepoint.startswith("U+"):
            problems.append(
                f"metadata/glyphnames.json entry for {glyph_name} has invalid codepoint"
            )
            continue

        try:
            parsed_codepoint = int(codepoint.removeprefix("U+"), 16)
        except ValueError:
            problems.append(
                f"metadata/glyphnames.json entry for {glyph_name} has invalid codepoint"
            )
            continue
        actual_by_name[glyph_name] = parsed_codepoint
        codepoint_counts[parsed_codepoint] += 1

    duplicate_codepoints = [
        f"U+{codepoint:04X} appears {count} times"
        for codepoint, count in sorted(codepoint_counts.items())
        if count > 1
    ]
    if duplicate_codepoints:
        problems.append(
            "metadata/glyphnames.json has duplicate codepoints:\n"
            f"{chr(10).join(duplicate_codepoints)}"
        )

    problems.extend(
        _compare_glyph_map("metadata/glyphnames.json", actual_by_name, expected_names)
    )
    return problems


def _check_ranges_json() -> list[str]:
    problems: list[str] = []
    expected_names = expected_by_name(include_optional=False)
    ranges, json_problems = _load_json(RANGES_PATH)
    problems.extend(json_problems)
    if ranges is None:
        return problems

    actual_by_name: dict[str, int] = {}
    occurrences: Counter[str] = Counter()
    for range_name, data in ranges.items():
        if not isinstance(data, dict):
            problems.append(f"metadata/ranges.json range {range_name} is not an object")
            continue
        try:
            range_start = int(data["rangeStart"].removeprefix("U+"), 16)
            range_end = int(data["rangeEnd"].removeprefix("U+"), 16)
            glyph_names = data["glyphs"]
        except KeyError as e:
            problems.append(f"metadata/ranges.json range {range_name} is missing {e}")
            continue

        if not isinstance(range_start, int) or not isinstance(range_end, int):
            problems.append(
                f"metadata/ranges.json range {range_name} has invalid bounds"
            )
            continue
        if not isinstance(glyph_names, list):
            problems.append(
                f"metadata/ranges.json range {range_name} has invalid glyphs"
            )
            continue

        for glyph_name in glyph_names:
            if not isinstance(glyph_name, str):
                problems.append(
                    f"metadata/ranges.json range {range_name} has non-string glyph"
                )
                continue
            occurrences[glyph_name] += 1
            expected_codepoint = expected_names.get(glyph_name)
            if expected_codepoint is None:
                continue
            actual_by_name[glyph_name] = expected_codepoint
            if expected_codepoint < range_start or expected_codepoint > range_end:
                problems.append(
                    "metadata/ranges.json places "
                    f"U+{expected_codepoint:04X} {glyph_name} outside "
                    f"{range_name} (U+{range_start:04X}-U+{range_end:04X})"
                )

    duplicates = [
        f"{glyph_name} appears {count} times"
        for glyph_name, count in sorted(occurrences.items())
        if count > 1
    ]
    if duplicates:
        problems.append(
            f"metadata/ranges.json has duplicate glyphs:\n{chr(10).join(duplicates)}"
        )

    problems.extend(
        _compare_glyph_map("metadata/ranges.json", actual_by_name, expected_names)
    )
    return problems


def _check_neanes_metadata_json() -> list[str]:
    problems: list[str] = []
    metadata, json_problems = _load_json(NEANES_METADATA_PATH)
    problems.extend(json_problems)
    if metadata is None:
        return problems

    expected_names = expected_by_name(include_optional=True)
    for section in ("glyphAdvanceWidths", "glyphBBoxes"):
        actual = metadata.get(section)
        if not isinstance(actual, dict):
            problems.append(
                f"fonts/neanes.metadata.json is missing object section {section}"
            )
            continue
        problems.extend(
            _compare_name_set(
                f"fonts/neanes.metadata.json {section}", actual, expected_names
            )
        )

    optional_glyphs = metadata.get("optionalGlyphs")
    if not isinstance(optional_glyphs, dict):
        problems.append(
            "fonts/neanes.metadata.json is missing object section optionalGlyphs"
        )
        return problems

    actual_optional: dict[str, int] = {}
    for glyph_name, data in optional_glyphs.items():
        codepoint = data.get("codepoint") if isinstance(data, dict) else None
        if not isinstance(codepoint, str) or not codepoint.startswith("U+"):
            problems.append(
                "fonts/neanes.metadata.json optionalGlyphs has invalid codepoint for "
                f"{glyph_name}"
            )
            continue
        actual_optional[glyph_name] = int(codepoint.removeprefix("U+"), 16)

    problems.extend(
        _compare_glyph_map(
            "fonts/neanes.metadata.json optionalGlyphs",
            actual_optional,
            {name: codepoint for codepoint, name in SBMUFL_OPTIONAL_GLYPHS.items()},
        )
    )
    return problems


def repository_metadata_problems() -> list[str]:
    problems: list[str] = []
    namelist, namelist_problems = parse_namelist()
    problems.extend(namelist_problems)
    namelist_by_name = {name: codepoint for codepoint, name in namelist.items()}
    problems.extend(
        _compare_glyph_map(
            "sources/namelist.txt",
            namelist_by_name,
            expected_by_name(include_optional=True),
        )
    )
    problems.extend(_check_docs_tables())
    problems.extend(_check_glyphnames_json())
    problems.extend(_check_ranges_json())
    problems.extend(_check_neanes_metadata_json())
    return problems
