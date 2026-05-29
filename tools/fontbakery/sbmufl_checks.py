from __future__ import annotations

import json
import math
import re
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from itertools import product
from pathlib import Path
from typing import Any, Final, cast

import uharfbuzz as hb
from fontbakery.prelude import FAIL, WARN, Message
from fontbakery.prelude import check as fontbakery_check
from fontbakery.utils import bullet_list
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables import otTables

REPO_ROOT: Final = Path(__file__).resolve().parents[2]
DOCS_TABLES_PATH: Final = REPO_ROOT / "docs" / "tables"
NAMELIST_PATH: Final = REPO_ROOT / "sources" / "namelist.txt"
GLYPHNAMES_PATH: Final = REPO_ROOT / "metadata" / "glyphnames.json"
RANGES_PATH: Final = REPO_ROOT / "metadata" / "ranges.json"
NEANES_METADATA_PATH: Final = REPO_ROOT / "fonts" / "neanes.metadata.json"
NAMELIST_RE: Final = re.compile(r"^0x([0-9A-Fa-f]+)\s+(\S+)\s*$")


def _parse_namelist(problems: list[str]) -> dict[int, str]:
    glyphs: dict[int, str] = {}
    glyph_names: dict[str, int] = {}
    try:
        lines = NAMELIST_PATH.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        problems.append(f"Missing file: {NAMELIST_PATH.relative_to(REPO_ROOT)}")
        return glyphs

    for line in lines:
        match = NAMELIST_RE.match(line)
        if not match:
            continue
        codepoint = int(match.group(1), 16)
        glyph_name = match.group(2)
        if codepoint in glyphs:
            problems.append(
                "Duplicate namelist codepoint "
                f"U+{codepoint:04X}: {glyphs[codepoint]} and {glyph_name}"
            )
        if glyph_name in glyph_names:
            previous_codepoint = glyph_names[glyph_name]
            problems.append(
                "Duplicate namelist glyph "
                f"{glyph_name}: U+{previous_codepoint:04X} and U+{codepoint:04X}"
            )
        glyphs[codepoint] = glyph_name
        glyph_names[glyph_name] = codepoint

    return glyphs


SBMUFL_OPTIONAL_RANGE: Final = range(0xF000, 0xF900)
SBMUFL_RESERVED_RANGE: Final = range(0xE430, 0xF000)

SBMUFL_NAMELIST_GLYPHS: Final[dict[int, str]] = _parse_namelist([])

SBMUFL_REQUIRED_GLYPHS: Final[dict[int, str]] = {
    codepoint: glyph_name
    for codepoint, glyph_name in SBMUFL_NAMELIST_GLYPHS.items()
    if codepoint not in SBMUFL_OPTIONAL_RANGE
}

SBMUFL_OPTIONAL_GLYPHS: Final[dict[int, str]] = {
    codepoint: glyph_name
    for codepoint, glyph_name in SBMUFL_NAMELIST_GLYPHS.items()
    if codepoint in SBMUFL_OPTIONAL_RANGE
}

SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME: Final[dict[str, int]] = {
    glyph_name: codepoint for codepoint, glyph_name in SBMUFL_OPTIONAL_GLYPHS.items()
}

SBMUFL_MARK_CODEPOINTS: Final[set[int]] = {
    # Quality marks with zero advance width. Spacing signs in this block,
    # including vareia, stavros, and breath, are intentionally excluded.
    *range(0xE0A1, 0xE0A8),
    *range(0xE0B0, 0xE0B2),
    0xE0C8,
    # Temporal augmentation marks. Leimmata are spacing signs.
    *range(0xE0D0, 0xE0D7),
    # Temporal division marks
    *range(0xE0F0, 0xE0FF),
    *range(0xE100, 0xE10B),
    # Tempo marks that may be placed above a martyria of the notes
    *range(0xE128, 0xE130),
    # Martyria of the notes
    *range(0xE150, 0xE15C),
    *range(0xE170, 0xE17C),
    # Fthora/chroa combining forms: above, secondary, tertiary, and below
    # U+E1D0..U+E1DF are spacing fthora/chroa signs
    *range(0xE190, 0xE1D0),
    # Diesis/yfesis combining alteration signs
    *range(0xE1F0, 0xE210),
    # Combining barline Marks
    *range(0xE216, 0xE21C),
    # Measure numbers
    *range(0xE220, 0xE227),
    # Note indicators and ison indicators
    *range(0xE250, 0xE257),
    *range(0xE260, 0xE26B),
    # Martyria of the tones
    *range(0xE2E7, 0xE2EB),
    # Optional mark alternates. U+F003..U+F005 are spacing glyphs.
    0xF002,
    *range(0xF006, 0xF009),
}

SBMUFL_MARK_TO_MARK_CODEPOINTS: Final[set[int]] = {
    # Tempo marks and combining barline marks may stack on marks.
    *range(0xE128, 0xE130),
    *range(0xE216, 0xE21C),
}

SBMUFL_ISON_INDICATOR_CODEPOINTS: Final[set[int]] = {
    0xE260,  # U+E260 isonIndicatorUnison
    0xE261,  # U+E261 isonIndicatorDiLow
    0xE262,  # U+E262 isonIndicatorKeLow
    0xE263,  # U+E263 isonIndicatorZo
    0xE264,  # U+E264 isonIndicatorNi
    0xE265,  # U+E265 isonIndicatorPa
    0xE266,  # U+E266 isonIndicatorVou
    0xE267,  # U+E267 isonIndicatorGa
    0xE268,  # U+E268 isonIndicatorDi
    0xE269,  # U+E269 isonIndicatorKe
    0xE26A,  # U+E26A isonIndicatorZoHigh
}
SBMUFL_ISON_SHAPING_PROBE_CODEPOINT: Final = 0xE260
SBMUFL_ISON_INDICATOR_CLEARANCE: Final = 120
SBMUFL_ISON_CONTEXTUAL_RAISE_GRID: Final = 20
SBMUFL_ISON_INDICATOR_COMPROMISE_CODEPOINTS: Final[dict[int, str]] = {
    0xE005: "oligonYpsiliRight",
    0xE006: "oligonYpsiliLeft",
    0xE007: "oligonKentimaYpsiliRight",
    0xE044: "petastiYpsiliRight",
    0xE046: "petastiKentimaYpsiliRight",
    0xE086: "oligonYpsiliRightKentimata",
    0xE087: "oligonYpsiliLeftKentimata",
}
SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS: Final[set[int]] = {
    # Primary above gorgon-family marks.
    0xE0F0,  # U+E0F0 gorgonAbove
    0xE0F2,  # U+E0F2 gorgonDottedLeft
    0xE0F3,  # U+E0F3 gorgonDottedRight
    0xE0F4,  # U+E0F4 digorgon
    0xE0F6,  # U+E0F6 digorgonDottedLeftAbove
    0xE0F7,  # U+E0F7 digorgonDottedRight
    0xE0F8,  # U+E0F8 trigorgon
    0xE0FA,  # U+E0FA trigorgonDottedLeftAbove
    0xE0FB,  # U+E0FB trigorgonDottedRight
}
SBMUFL_GORGON_SECONDARY_ABOVE_CODEPOINTS: Final[set[int]] = {
    # Secondary above gorgon-family marks.
    0xE100,  # U+E100 gorgonSecondary
    0xE101,  # U+E101 gorgonDottedLeftSecondary
    0xE102,  # U+E102 gorgonDottedRightSecondary
    0xE103,  # U+E103 digorgonSecondary
    0xE105,  # U+E105 digorgonDottedRightSecondary
    0xE106,  # U+E106 trigorgonSecondary
    0xE108,  # U+E108 trigorgonDottedRightSecondary
    0xE109,  # U+E109 digorgonDottedLeftSecondary
    0xE10A,  # U+E10A trigorgonDottedLeftSecondary
}
SBMUFL_GORGON_ABOVE_CODEPOINTS: Final[set[int]] = (
    SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS | SBMUFL_GORGON_SECONDARY_ABOVE_CODEPOINTS
)
MarkClassRef = tuple[int, int]


def check(
    *args: Any, **kwargs: Any
) -> Callable[[Callable[..., Iterator[tuple[Any, Message]]]], object]:
    return cast(
        Callable[[Callable[..., Iterator[tuple[Any, Message]]]], object],
        fontbakery_check(*args, **kwargs),
    )


def _all_cmap_items(ttFont: Any) -> list[tuple[int, str]]:
    cmap_table = ttFont.get("cmap")
    if cmap_table is None:
        return []

    items: set[tuple[int, str]] = set()
    for subtable in cmap_table.tables:
        items.update(subtable.cmap.items())
    return sorted(items)


@check(
    id="sbmufl/glyph_coverage",
    rationale="""
        The Standard Byzantine Music Font Layout maps Byzantine chant notation
        glyphs into the Basic Multilingual Plane Private Use Area and reserves
        U+F000 through U+F8FF as free space for optional glyphs, including
        stylistic alternates. Fonts that claim SBMuFL compatibility should
        encode the required glyphs in the standard locations, and optional
        encoded glyphs should also use their standard optional-range codepoints.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_glyph_coverage(
    ttFont: Any, config: Any
) -> Iterator[tuple[Any, Message]]:
    """Check that the font covers required and optional SBMuFL glyphs."""
    cmap = cast(Mapping[int, str], ttFont.getBestCmap() or {})
    glyph_order = set(ttFont.getGlyphOrder())
    missing = sorted(set(SBMUFL_REQUIRED_GLYPHS) - set(cmap))

    missing_glyph_names = [
        f"U+{codepoint:04X} {glyph_name}"
        for codepoint, glyph_name in sorted(SBMUFL_REQUIRED_GLYPHS.items())
        if codepoint not in cmap and glyph_name not in glyph_order
    ]

    inconsistent_names = [
        f"U+{codepoint:04X} {glyph_name} (expected {SBMUFL_REQUIRED_GLYPHS[codepoint]})"
        for codepoint, glyph_name in sorted(cmap.items())
        if codepoint in SBMUFL_REQUIRED_GLYPHS
        and glyph_name != SBMUFL_REQUIRED_GLYPHS[codepoint]
    ]

    missing_optional = [
        f"U+{codepoint:04X} {glyph_name}"
        for codepoint, glyph_name in sorted(SBMUFL_OPTIONAL_GLYPHS.items())
        if glyph_name not in glyph_order
    ]

    misplaced_optional = [
        f"U+{codepoint:04X} {glyph_name} (expected U+"
        f"{SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME[glyph_name]:04X})"
        for codepoint, glyph_name in _all_cmap_items(ttFont)
        if glyph_name in SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME
        and codepoint != SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME[glyph_name]
    ]

    inconsistent_optional_names = [
        f"U+{codepoint:04X} {glyph_name} (expected {SBMUFL_OPTIONAL_GLYPHS[codepoint]})"
        for codepoint, glyph_name in _all_cmap_items(ttFont)
        if codepoint in SBMUFL_OPTIONAL_GLYPHS
        and glyph_name != SBMUFL_OPTIONAL_GLYPHS[codepoint]
    ]

    if missing:
        missing_glyphs = [
            f"U+{codepoint:04X} {SBMUFL_REQUIRED_GLYPHS[codepoint]}"
            for codepoint in missing
        ]
        yield FAIL, Message(
            "missing-codepoints",
            "Missing required SBMuFL codepoints:\n\n"
            f"{bullet_list(config, missing_glyphs)}",
        )

    if missing_glyph_names:
        yield WARN, Message(
            "missing-glyphs",
            "Missing required SBMuFL glyphs:\n\n"
            f"{bullet_list(config, missing_glyph_names)}",
        )

    if inconsistent_names:
        yield WARN, Message(
            "inconsistent-glyph-names",
            "Required SBMuFL codepoints mapped to inconsistent glyph names:\n\n"
            f"{bullet_list(config, inconsistent_names)}",
        )

    if missing_optional:
        yield WARN, Message(
            "missing-optional-glyphs",
            "Missing optional SBMuFL glyphs:\n\n"
            f"{bullet_list(config, missing_optional)}",
        )

    if misplaced_optional:
        yield FAIL, Message(
            "optional-glyphs-wrong-codepoint",
            "Optional glyphs encoded at non-standard SBMuFL codepoints:\n\n"
            f"{bullet_list(config, misplaced_optional)}",
        )

    if inconsistent_optional_names:
        yield WARN, Message(
            "optional-glyph-name-inconsistency",
            "SBMuFL optional codepoints mapped to inconsistent glyph names:\n\n"
            f"{bullet_list(config, inconsistent_optional_names)}",
        )


@check(
    id="sbmufl/reserved_codepoints",
    rationale="""
        SBMuFL reserves U+E430 through U+EFFF for future use. Fonts should not
        assign glyphs in that range until the standard gives those codepoints a
        defined meaning, otherwise applications may later interpret those glyphs
        incorrectly.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_reserved_codepoints(
    ttFont: Any, config: Any
) -> Iterator[tuple[Any, Message]]:
    """Check that no glyphs are encoded in the reserved SBMuFL range."""
    reserved = [
        f"U+{codepoint:04X} {glyph_name}"
        for codepoint, glyph_name in _all_cmap_items(ttFont)
        if codepoint in SBMUFL_RESERVED_RANGE
    ]

    if reserved:
        yield FAIL, Message(
            "reserved-codepoints",
            "Glyphs encoded in the SBMuFL reserved range:\n\n"
            f"{bullet_list(config, reserved)}",
        )


def _gpos_lookups(ttFont: Any) -> Sequence[Any]:
    if "GPOS" not in ttFont:
        return []

    lookup_list = ttFont["GPOS"].table.LookupList
    if lookup_list is None:
        return []

    return lookup_list.Lookup


def _gpos_lookup_types(ttFont: Any) -> set[int]:
    return {lookup.LookupType for lookup in _gpos_lookups(ttFont)}


def _gpos_mark_to_base_subtables(ttFont: Any) -> Iterator[tuple[int, Any]]:
    index = 0
    for lookup in _gpos_lookups(ttFont):
        if lookup.LookupType != otTables.MarkBasePos.LookupType:
            continue
        for subtable in lookup.SubTable:
            yield index, subtable
            index += 1


@check(
    id="sbmufl/mark_positioning",
    rationale="""
        SBMuFL mark-like signs, such as fthores, temporal signs, note
        indicators, and ison indicators, are intended to be positioned with
        OpenType GPOS mark attachment. SBMuFL documents Mark-to-Base attachment
        for these signs and Mark-to-Mark attachment for tempo signs stacked
        above fthores.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_mark_positioning(ttFont: Any) -> Iterator[tuple[Any, Message]]:
    """Check that the font has SBMuFL-required GPOS mark positioning lookups."""
    lookup_types = _gpos_lookup_types(ttFont)

    if otTables.MarkBasePos.LookupType not in lookup_types:
        yield FAIL, Message(
            "missing-mark-to-base-lookup",
            "Missing GPOS Lookup Type 4: Mark-to-Base Attachment",
        )

    if otTables.MarkMarkPos.LookupType not in lookup_types:
        yield WARN, Message(
            "missing-mark-to-mark-lookup",
            "Missing GPOS Lookup Type 6: Mark-to-Mark Attachment",
        )


def _gpos_mark_coverages(ttFont: Any) -> tuple[set[str], set[str]]:
    mark_to_base_glyphs: set[str] = set()
    mark_to_mark_glyphs: set[str] = set()

    for lookup in _gpos_lookups(ttFont):
        for subtable in lookup.SubTable:
            if lookup.LookupType == otTables.MarkBasePos.LookupType:
                mark_to_base_glyphs.update(subtable.MarkCoverage.glyphs)
            elif lookup.LookupType == otTables.MarkMarkPos.LookupType:
                mark_to_mark_glyphs.update(subtable.Mark1Coverage.glyphs)

    return mark_to_base_glyphs, mark_to_mark_glyphs


def _gpos_mark_to_base_mark_classes(
    ttFont: Any, glyph_names: set[str]
) -> set[MarkClassRef]:
    mark_classes: set[MarkClassRef] = set()

    for subtable_index, subtable in _gpos_mark_to_base_subtables(ttFont):
        for glyph_name, mark_record in zip(
            subtable.MarkCoverage.glyphs,
            subtable.MarkArray.MarkRecord,
            strict=True,
        ):
            if glyph_name in glyph_names:
                mark_classes.add((subtable_index, mark_record.Class))

    return mark_classes


def _gpos_mark_to_base_mark_anchor_positions(
    ttFont: Any, glyph_names: set[str]
) -> dict[str, set[tuple[MarkClassRef, int, int]]]:
    positions: dict[str, set[tuple[MarkClassRef, int, int]]] = {}

    for subtable_index, subtable in _gpos_mark_to_base_subtables(ttFont):
        for glyph_name, mark_record in zip(
            subtable.MarkCoverage.glyphs,
            subtable.MarkArray.MarkRecord,
            strict=True,
        ):
            if glyph_name in glyph_names and mark_record.MarkAnchor is not None:
                positions.setdefault(glyph_name, set()).add(
                    (
                        (subtable_index, mark_record.Class),
                        mark_record.MarkAnchor.XCoordinate,
                        mark_record.MarkAnchor.YCoordinate,
                    )
                )

    return positions


def _gpos_mark_to_base_mark_anchor_ys(
    ttFont: Any, glyph_names: set[str]
) -> dict[MarkClassRef, set[tuple[str, int]]]:
    anchor_ys: dict[MarkClassRef, set[tuple[str, int]]] = {}

    for subtable_index, subtable in _gpos_mark_to_base_subtables(ttFont):
        for glyph_name, mark_record in zip(
            subtable.MarkCoverage.glyphs,
            subtable.MarkArray.MarkRecord,
            strict=True,
        ):
            if glyph_name in glyph_names and mark_record.MarkAnchor is not None:
                anchor_ys.setdefault((subtable_index, mark_record.Class), set()).add(
                    (glyph_name, mark_record.MarkAnchor.YCoordinate)
                )

    return anchor_ys


def _gpos_mark_to_base_anchor_positions(
    ttFont: Any, mark_classes: set[MarkClassRef]
) -> dict[str, set[tuple[MarkClassRef, int, int]]]:
    positions: dict[str, set[tuple[MarkClassRef, int, int]]] = {}

    for subtable_index, subtable in _gpos_mark_to_base_subtables(ttFont):
        subtable_mark_classes = {
            mark_class
            for class_subtable_index, mark_class in mark_classes
            if class_subtable_index == subtable_index
        }
        if not subtable_mark_classes:
            continue

        for glyph_name, base_record in zip(
            subtable.BaseCoverage.glyphs,
            subtable.BaseArray.BaseRecord,
            strict=True,
        ):
            for mark_class in subtable_mark_classes:
                if mark_class >= len(base_record.BaseAnchor):
                    continue

                anchor = base_record.BaseAnchor[mark_class]
                if anchor is not None:
                    positions.setdefault(glyph_name, set()).add(
                        (
                            (subtable_index, mark_class),
                            anchor.XCoordinate,
                            anchor.YCoordinate,
                        )
                    )

    return positions


def _value_record_has_horizontal_adjustment(value_record: Any) -> bool:
    return any(
        (getattr(value_record, field_name, 0) or 0) != 0
        for field_name in ("XPlacement", "XAdvance", "YAdvance")
    )


def _single_pos_y_placements(
    lookup: Any, glyph_names: set[str]
) -> tuple[dict[str, int], list[str]]:
    positions: dict[str, int] = {}
    problems: list[str] = []

    if lookup.LookupType != otTables.SinglePos.LookupType:
        return positions, [f"lookup type {lookup.LookupType} is not SinglePos"]

    for subtable in lookup.SubTable:
        if subtable.Format == 1:
            value_record = subtable.Value
            if _value_record_has_horizontal_adjustment(value_record):
                problems.append("SinglePos format 1 has non-YPlacement adjustments")
            for glyph_name in set(subtable.Coverage.glyphs).intersection(glyph_names):
                positions[glyph_name] = getattr(value_record, "YPlacement", 0) or 0
        elif subtable.Format == 2:
            for glyph_name, value_record in zip(
                subtable.Coverage.glyphs,
                subtable.Value,
                strict=True,
            ):
                if glyph_name not in glyph_names:
                    continue
                if _value_record_has_horizontal_adjustment(value_record):
                    problems.append(
                        f"{glyph_name}: SinglePos format 2 has "
                        "non-YPlacement adjustments"
                    )
                positions[glyph_name] = getattr(value_record, "YPlacement", 0) or 0
        else:
            problems.append(f"unsupported SinglePos format {subtable.Format}")

    return positions, problems


def _gpos_contextual_ison_raise_rules(
    ttFont: Any,
    encoded_ison_indicators: set[str],
    encoded_gorgon_above_marks: set[str],
) -> tuple[dict[tuple[str, tuple[str, ...]], set[int]], list[str]]:
    rules: dict[tuple[str, tuple[str, ...]], set[int]] = {}
    problems: list[str] = []
    lookups = _gpos_lookups(ttFont)

    for lookup_index, lookup in enumerate(lookups):
        if lookup.LookupType not in {
            otTables.ChainContextPos.LookupType,
            otTables.ExtensionPos.LookupType,
        }:
            continue

        for lookup_subtable in lookup.SubTable:
            subtable = lookup_subtable
            if lookup.LookupType == otTables.ExtensionPos.LookupType:
                if (
                    lookup_subtable.ExtensionLookupType
                    != otTables.ChainContextPos.LookupType
                ):
                    continue
                subtable = lookup_subtable.ExtSubTable

            if subtable.Format != 3:
                continue

            if subtable.LookAheadGlyphCount != 0 or subtable.InputGlyphCount != 1:
                continue

            if subtable.BacktrackGlyphCount not in {2, 3}:
                continue

            # FontForge stores backtrack coverage nearest to the input first.
            backtrack_coverages = list(reversed(subtable.BacktrackCoverage))
            base_glyphs = set(backtrack_coverages[0].glyphs)
            gorgon_coverages = [
                set(coverage.glyphs).intersection(encoded_gorgon_above_marks)
                for coverage in backtrack_coverages[1:]
            ]
            ison_glyphs = set(subtable.InputCoverage[0].glyphs)

            if not all(gorgon_coverages) or not ison_glyphs.intersection(
                encoded_ison_indicators
            ):
                continue

            missing_ison_glyphs = sorted(encoded_ison_indicators - ison_glyphs)
            if missing_ison_glyphs:
                problems.append(
                    f"lookup {lookup_index}: context omits ison indicators "
                    f"{', '.join(missing_ison_glyphs)}"
                )

            for lookup_record in subtable.PosLookupRecord:
                if lookup_record.SequenceIndex != 0:
                    continue
                if lookup_record.LookupListIndex >= len(lookups):
                    problems.append(
                        f"lookup {lookup_index}: referenced lookup "
                        f"{lookup_record.LookupListIndex} is out of range"
                    )
                    continue

                y_placements, placement_problems = _single_pos_y_placements(
                    lookups[lookup_record.LookupListIndex],
                    encoded_ison_indicators,
                )
                problems.extend(
                    f"lookup {lookup_record.LookupListIndex}: {problem}"
                    for problem in placement_problems
                )

                missing_placements = sorted(
                    encoded_ison_indicators - y_placements.keys()
                )
                if missing_placements:
                    problems.append(
                        f"lookup {lookup_record.LookupListIndex}: missing "
                        f"YPlacement for {', '.join(missing_placements)}"
                    )
                    continue

                deltas = set(y_placements.values())
                if len(deltas) != 1:
                    problems.append(
                        f"lookup {lookup_record.LookupListIndex}: inconsistent "
                        "ison indicator YPlacement values"
                    )
                    continue

                delta_y = next(iter(deltas))
                for base_glyph in base_glyphs:
                    for gorgon_glyphs in product(*gorgon_coverages):
                        rules.setdefault((base_glyph, gorgon_glyphs), set()).add(
                            delta_y
                        )

    return rules, problems


def _shape_glyph_position(
    font_data: bytes,
    glyph_order: Sequence[str],
    text: str,
    glyph_name: str,
) -> tuple[int, int] | None:
    face = hb.Face(font_data)
    font = hb.Font(face)
    hb.ot_font_set_funcs(font)

    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)

    x = 0
    y = 0
    for glyph_info, glyph_position in zip(
        buffer.glyph_infos,
        buffer.glyph_positions,
        strict=True,
    ):
        if glyph_order[glyph_info.codepoint] == glyph_name:
            return x + glyph_position.x_offset, y + glyph_position.y_offset
        x += glyph_position.x_advance
        y += glyph_position.y_advance

    return None


def _ison_contextual_shaping_problems(
    ttFont: Any,
    cmap: Mapping[int, str],
    expected_deltas: Mapping[tuple[str, tuple[str, ...]], int],
) -> list[str]:
    font_path = Path(ttFont.reader.file.name)
    font_data = font_path.read_bytes()
    glyph_order = ttFont.getGlyphOrder()
    codepoint_by_glyph = {
        glyph_name: codepoint for codepoint, glyph_name in cmap.items()
    }
    ison_glyph = cmap.get(SBMUFL_ISON_SHAPING_PROBE_CODEPOINT)
    if ison_glyph is None:
        return ["U+E260 isonIndicatorUnison is not encoded"]

    problems: list[str] = []
    ison_text = chr(SBMUFL_ISON_SHAPING_PROBE_CODEPOINT)
    for (base_name, gorgon_names), expected_delta in sorted(expected_deltas.items()):
        base_codepoint = codepoint_by_glyph.get(base_name)
        gorgon_codepoints = [
            codepoint_by_glyph.get(gorgon_name) for gorgon_name in gorgon_names
        ]
        if base_codepoint is None or any(
            gorgon_codepoint is None for gorgon_codepoint in gorgon_codepoints
        ):
            continue

        base_text = chr(base_codepoint)
        gorgon_text = "".join(
            chr(cast(int, gorgon_codepoint)) for gorgon_codepoint in gorgon_codepoints
        )
        base_ison_position = _shape_glyph_position(
            font_data,
            glyph_order,
            base_text + ison_text,
            ison_glyph,
        )
        gorgon_ison_position = _shape_glyph_position(
            font_data,
            glyph_order,
            base_text + gorgon_text + ison_text,
            ison_glyph,
        )
        if base_ison_position is None or gorgon_ison_position is None:
            problems.append(
                f"{base_name} + {' + '.join(gorgon_names)}: ison did not shape"
            )
            continue

        base_x, base_y = base_ison_position
        gorgon_x, gorgon_y = gorgon_ison_position
        actual_delta = gorgon_y - base_y
        if gorgon_x != base_x or actual_delta != expected_delta:
            problems.append(
                f"{base_name} + {' + '.join(gorgon_names)}: shaped ison offset "
                f"X={gorgon_x} Y={gorgon_y}; without gorgon X={base_x} "
                f"Y={base_y}; expected X={base_x} Y={base_y + expected_delta}"
            )

    return problems


def _format_mark_class(mark_class: MarkClassRef) -> str:
    subtable_index, class_id = mark_class
    return f"subtable {subtable_index} class {class_id}"


def _glyph_ymax(ttFont: Any, glyph_name: str) -> float | None:
    glyph_set = ttFont.getGlyphSet()
    if glyph_name not in glyph_set:
        return None

    pen = BoundsPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    if pen.bounds is None:
        return None
    return cast(float, pen.bounds[3])


def _gdef_glyph_classes(ttFont: Any) -> Mapping[str, int]:
    if "GDEF" not in ttFont:
        return {}

    glyph_class_def = ttFont["GDEF"].table.GlyphClassDef
    if glyph_class_def is None:
        return {}

    return cast(Mapping[str, int], glyph_class_def.classDefs)


def _cmap_label(
    codepoint: int,
    expected_glyph_name: str,
    actual_glyph_name: str | None,
) -> str:
    actual_glyph_suffix = (
        "" if actual_glyph_name == expected_glyph_name else f" ({actual_glyph_name})"
    )
    return f"U+{codepoint:04X} {expected_glyph_name}{actual_glyph_suffix}"


@check(
    id="sbmufl/mark_attachment",
    rationale="""
        SBMuFL documents many notation signs as marks that should be positioned
        with OpenType mark attachment. These encoded signs should be classified
        as marks in GDEF and included in GPOS mark attachment coverage so layout
        engines can attach them to their base signs.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_mark_attachment(
    ttFont: Any, config: Any
) -> Iterator[tuple[Any, Message]]:
    """Check that SBMuFL mark codepoints are mark-classed and attached in GPOS."""
    cmap = cast(Mapping[int, str], ttFont.getBestCmap() or {})
    glyph_classes = _gdef_glyph_classes(ttFont)
    mark_to_base_glyphs, mark_to_mark_glyphs = _gpos_mark_coverages(ttFont)

    missing_gdef: list[str] = []
    missing_mark_to_base: list[str] = []
    missing_mark_to_mark: list[str] = []

    encoded_mark_codepoints = sorted(
        SBMUFL_MARK_CODEPOINTS.intersection(SBMUFL_NAMELIST_GLYPHS).intersection(cmap)
    )
    encoded_mark_to_mark_codepoints = sorted(
        SBMUFL_MARK_TO_MARK_CODEPOINTS.intersection(
            SBMUFL_NAMELIST_GLYPHS
        ).intersection(cmap)
    )

    for codepoint in encoded_mark_codepoints:
        glyph_name = cmap[codepoint]

        expected_glyph_name = SBMUFL_NAMELIST_GLYPHS[codepoint]
        label = _cmap_label(codepoint, expected_glyph_name, glyph_name)
        if glyph_classes.get(glyph_name) != 3:
            missing_gdef.append(label)
        if glyph_name not in mark_to_base_glyphs:
            missing_mark_to_base.append(label)

    for codepoint in encoded_mark_to_mark_codepoints:
        glyph_name = cmap[codepoint]

        if glyph_name not in mark_to_mark_glyphs:
            expected_glyph_name = SBMUFL_NAMELIST_GLYPHS[codepoint]
            label = _cmap_label(codepoint, expected_glyph_name, glyph_name)
            missing_mark_to_mark.append(label)

    if missing_gdef:
        yield FAIL, Message(
            "not-gdef-mark",
            "SBMuFL mark codepoints not classified as marks in GDEF:\n\n"
            f"{bullet_list(config, missing_gdef)}",
        )

    if missing_mark_to_base:
        yield FAIL, Message(
            "not-mark-to-base",
            "SBMuFL mark codepoints not covered by GPOS Mark-to-Base attachment:\n\n"
            f"{bullet_list(config, missing_mark_to_base)}",
        )

    if missing_mark_to_mark:
        yield WARN, Message(
            "not-mark-to-mark",
            "SBMuFL mark codepoints not covered by GPOS Mark-to-Mark attachment:\n\n"
            f"{bullet_list(config, missing_mark_to_mark)}",
        )


@check(
    id="sbmufl/ison_mark_vertical_positioning",
    rationale="""
        Ison indicator glyphs are marks that attach above neumes. To keep the
        selected ison pitch from changing the visual height of the notation,
        base glyphs that accept an ison indicator should place that mark at the
        ison glyph's vertical position unless that would collide with the base
        glyph outline. Gorgon-family marks are handled dynamically with a
        contextual GPOS raise on the ison indicator, preserving the base
        glyph's isonIndicator X anchor while clearing the actual gorgon,
        digorgon, or trigorgon mark present in the shaped sequence.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_ison_mark_vertical_positioning(
    ttFont: Any, config: Any
) -> Iterator[tuple[Any, Message]]:
    """Check that ison indicators attach at a consistent vertical position."""
    cmap = cast(Mapping[int, str], ttFont.getBestCmap() or {})
    encoded_ison_indicators = {
        cmap[codepoint]
        for codepoint in sorted(SBMUFL_ISON_INDICATOR_CODEPOINTS.intersection(cmap))
    }
    if not encoded_ison_indicators:
        yield FAIL, Message(
            "missing-ison-indicators",
            "Font does not encode any ison indicator marks.",
        )
        return

    mark_classes = _gpos_mark_to_base_mark_classes(ttFont, encoded_ison_indicators)
    if not mark_classes:
        yield FAIL, Message(
            "missing-ison-mark-class",
            "Ison indicator marks are not covered by GPOS Mark-to-Base attachment.",
        )
        return

    ison_mark_to_base_positions = _gpos_mark_to_base_mark_anchor_positions(
        ttFont,
        encoded_ison_indicators,
    )
    missing_ison_mark_anchors = sorted(
        encoded_ison_indicators - ison_mark_to_base_positions.keys()
    )
    if missing_ison_mark_anchors:
        yield FAIL, Message(
            "missing-ison-mark-anchor",
            "Ison indicator glyphs missing their Mark-to-Base mark anchor:\n\n"
            f"{bullet_list(config, missing_ison_mark_anchors)}",
        )
        return

    anchor_positions = _gpos_mark_to_base_anchor_positions(ttFont, mark_classes)
    reference_positions = anchor_positions.get("ison", set())
    if not reference_positions:
        yield FAIL, Message(
            "missing-ison-base-anchor",
            "The ison glyph is missing a GPOS base anchor for ison indicator marks.",
        )
        return

    reference_y_positions = {y for _, _, y in reference_positions}
    if len(reference_y_positions) > 1:
        formatted_positions = [
            f"{_format_mark_class(mark_class)}, X={x}, Y={y}"
            for mark_class, x, y in sorted(reference_positions)
        ]
        yield FAIL, Message(
            "conflicting-ison-base-anchors",
            "The ison glyph has conflicting GPOS base anchors for ison "
            "indicator marks:\n\n"
            f"{bullet_list(config, formatted_positions)}",
        )
        return

    encoded_gorgon_above_marks = {
        cmap[codepoint]
        for codepoint in sorted(SBMUFL_GORGON_ABOVE_CODEPOINTS.intersection(cmap))
    }
    encoded_primary_gorgon_above_marks = {
        cmap[codepoint]
        for codepoint in sorted(
            SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS.intersection(cmap)
        )
    }
    encoded_secondary_gorgon_above_marks = {
        cmap[codepoint]
        for codepoint in sorted(
            SBMUFL_GORGON_SECONDARY_ABOVE_CODEPOINTS.intersection(cmap)
        )
    }
    gorgon_above_mark_positions = _gpos_mark_to_base_mark_anchor_positions(
        ttFont,
        encoded_gorgon_above_marks,
    )
    missing_gorgon_mark_anchors = sorted(
        encoded_gorgon_above_marks - gorgon_above_mark_positions.keys()
    )
    if missing_gorgon_mark_anchors:
        yield FAIL, Message(
            "missing-gorgon-top-mark",
            "Gorgon-family marks missing their Mark-to-Base mark anchor:\n\n"
            f"{bullet_list(config, missing_gorgon_mark_anchors)}",
        )

    reference_y = next(iter(reference_y_positions))
    glyph_ymax_by_name: dict[str, float] = {}
    missing_bounds: list[str] = []
    for glyph_name in sorted(anchor_positions):
        glyph_ymax = _glyph_ymax(ttFont, glyph_name)
        if glyph_ymax is None:
            missing_bounds.append(glyph_name)
        else:
            glyph_ymax_by_name[glyph_name] = glyph_ymax

    if missing_bounds:
        yield FAIL, Message(
            "missing-ison-base-bounds",
            "Ison indicator base glyphs missing outline bounds:\n\n"
            f"{bullet_list(config, missing_bounds)}",
        )
        return

    gorgon_ymax_by_name = {
        glyph_name: glyph_ymax
        for glyph_name in encoded_gorgon_above_marks
        for glyph_ymax in [_glyph_ymax(ttFont, glyph_name)]
        if glyph_ymax is not None
    }
    missing_gorgon_bounds = sorted(
        encoded_gorgon_above_marks - gorgon_ymax_by_name.keys()
    )
    if missing_gorgon_bounds:
        yield FAIL, Message(
            "missing-gorgon-bounds",
            "Gorgon-family marks missing outline bounds:\n\n"
            f"{bullet_list(config, missing_gorgon_bounds)}",
        )
        return

    compromise_glyph_names = {
        cmap[codepoint]
        for codepoint in SBMUFL_ISON_INDICATOR_COMPROMISE_CODEPOINTS
        if codepoint in cmap
    }
    full_expected_y_by_name = {
        glyph_name: max(
            reference_y,
            math.ceil(glyph_ymax + SBMUFL_ISON_INDICATOR_CLEARANCE),
        )
        for glyph_name, glyph_ymax in glyph_ymax_by_name.items()
    }
    expected_y_by_name = {
        glyph_name: (
            reference_y
            if glyph_name == "ison"
            else (
                math.ceil((reference_y + full_expected_y_by_name[glyph_name]) / 2)
                if glyph_name in compromise_glyph_names
                else full_expected_y_by_name[glyph_name]
            )
        )
        for glyph_name in glyph_ymax_by_name
    }
    expected_y_by_name["ison"] = reference_y
    inconsistent_positions = [
        f"{glyph_name}: {_format_mark_class(mark_class)}, X={x}, Y={y} "
        f"(expected Y={expected_y_by_name[glyph_name]})"
        for glyph_name, positions in sorted(anchor_positions.items())
        for mark_class, x, y in sorted(positions)
        if y != expected_y_by_name[glyph_name]
    ]
    if inconsistent_positions:
        yield FAIL, Message(
            "inconsistent-ison-mark-vertical-position",
            "Ison indicator base anchors do not match base-only vertical "
            "positioning:\n\n"
            f"{bullet_list(config, inconsistent_positions)}",
        )

    gorgon_mark_classes_by_name: dict[str, tuple[MarkClassRef, int]] = {}
    conflicting_gorgon_mark_anchors: list[str] = []
    for glyph_name, positions in sorted(gorgon_above_mark_positions.items()):
        mark_positions = {(mark_class, y) for mark_class, _, y in sorted(positions)}
        if len(mark_positions) != 1:
            formatted_positions = [
                f"{_format_mark_class(mark_class)}, X={x}, Y={y}"
                for mark_class, x, y in sorted(positions)
            ]
            conflicting_gorgon_mark_anchors.append(
                f"{glyph_name}: {', '.join(formatted_positions)}"
            )
            continue

        mark_class, y = next(iter(mark_positions))
        gorgon_mark_classes_by_name[glyph_name] = (mark_class, y)

    if conflicting_gorgon_mark_anchors:
        yield FAIL, Message(
            "conflicting-gorgon-top-mark-anchors",
            "Gorgon-family marks have conflicting Mark-to-Base mark anchors:\n\n"
            f"{bullet_list(config, conflicting_gorgon_mark_anchors)}",
        )

    gorgon_base_positions = _gpos_mark_to_base_anchor_positions(
        ttFont,
        {mark_class for mark_class, _ in gorgon_mark_classes_by_name.values()},
    )
    gorgon_base_positions_by_name = {
        glyph_name: {mark_class: (x, y) for mark_class, x, y in positions}
        for glyph_name, positions in gorgon_base_positions.items()
    }

    single_expected_shaping_deltas: dict[tuple[str, str], int] = {}
    expected_shaping_deltas: dict[tuple[str, tuple[str, ...]], int] = {}
    for base_name, _base_positions in sorted(anchor_positions.items()):
        if base_name not in expected_y_by_name:
            continue

        gorgon_base_anchors = gorgon_base_positions_by_name.get(base_name, {})
        for gorgon_name, (
            gorgon_mark_class,
            gorgon_mark_y,
        ) in gorgon_mark_classes_by_name.items():
            gorgon_base_anchor = gorgon_base_anchors.get(gorgon_mark_class)
            if gorgon_base_anchor is None or gorgon_name not in gorgon_ymax_by_name:
                continue

            _, gorgon_base_y = gorgon_base_anchor
            mark_top_y = (
                gorgon_base_y - gorgon_mark_y + gorgon_ymax_by_name[gorgon_name]
            )
            target_y = max(
                expected_y_by_name[base_name],
                math.ceil(mark_top_y + SBMUFL_ISON_INDICATOR_CLEARANCE),
            )
            delta_y = target_y - expected_y_by_name[base_name]
            if delta_y > 0:
                delta_y = (
                    math.ceil(delta_y / SBMUFL_ISON_CONTEXTUAL_RAISE_GRID)
                    * SBMUFL_ISON_CONTEXTUAL_RAISE_GRID
                )
            else:
                delta_y = 0
            single_expected_shaping_deltas[(base_name, gorgon_name)] = delta_y
            expected_shaping_deltas[(base_name, (gorgon_name,))] = delta_y

        primary_gorgons = sorted(
            encoded_primary_gorgon_above_marks.intersection(
                {
                    gorgon_name
                    for pair_base_name, gorgon_name in single_expected_shaping_deltas
                    if pair_base_name == base_name
                }
            )
        )
        secondary_gorgons = sorted(
            encoded_secondary_gorgon_above_marks.intersection(
                {
                    gorgon_name
                    for pair_base_name, gorgon_name in single_expected_shaping_deltas
                    if pair_base_name == base_name
                }
            )
        )
        for primary_gorgon, secondary_gorgon in product(
            primary_gorgons, secondary_gorgons
        ):
            delta_y = max(
                single_expected_shaping_deltas[(base_name, primary_gorgon)],
                single_expected_shaping_deltas[(base_name, secondary_gorgon)],
            )
            expected_shaping_deltas[(base_name, (primary_gorgon, secondary_gorgon))] = (
                delta_y
            )
            expected_shaping_deltas[(base_name, (secondary_gorgon, primary_gorgon))] = (
                delta_y
            )

    actual_contextual_deltas, contextual_delta_problems = (
        _gpos_contextual_ison_raise_rules(
            ttFont,
            encoded_ison_indicators,
            encoded_gorgon_above_marks,
        )
    )
    if contextual_delta_problems:
        yield FAIL, Message(
            "invalid-ison-contextual-positioning",
            "Ison indicator contextual GPOS positioning is malformed:\n\n"
            f"{bullet_list(config, sorted(contextual_delta_problems))}",
        )

    missing_contextual_deltas = [
        f"{base_name} + {' + '.join(gorgon_names)}: expected YPlacement +{expected_delta}"
        for (base_name, gorgon_names), expected_delta in sorted(
            expected_shaping_deltas.items()
        )
        if expected_delta
        and expected_delta
        not in actual_contextual_deltas.get((base_name, gorgon_names), set())
    ]
    if missing_contextual_deltas:
        yield FAIL, Message(
            "missing-ison-contextual-positioning",
            "Missing contextual GPOS raises for ison indicators above "
            "gorgon-family marks:\n\n"
            f"{bullet_list(config, missing_contextual_deltas)}",
        )

    unexpected_contextual_deltas = [
        f"{base_name} + {' + '.join(gorgon_names)}: YPlacement values "
        f"{', '.join(f'+{delta}' for delta in sorted(actual_deltas))} "
        f"(expected {expected_delta_text})"
        for (base_name, gorgon_names), actual_deltas in sorted(
            actual_contextual_deltas.items()
        )
        for expected_delta in [
            expected_shaping_deltas.get((base_name, gorgon_names)) or None
        ]
        for expected_delta_text in [
            "none" if expected_delta is None else f"+{expected_delta}"
        ]
        if expected_delta is None or actual_deltas != {expected_delta}
    ]
    if unexpected_contextual_deltas:
        yield FAIL, Message(
            "inconsistent-ison-contextual-positioning",
            "Ison indicator contextual GPOS raises do not match the dynamic "
            "gorgon-family clearance formula:\n\n"
            f"{bullet_list(config, unexpected_contextual_deltas)}",
        )

    shaping_problems = _ison_contextual_shaping_problems(
        ttFont,
        cmap,
        expected_shaping_deltas,
    )
    if shaping_problems:
        yield FAIL, Message(
            "inconsistent-ison-contextual-shaping",
            "HarfBuzz shaping does not preserve ison X and apply the expected "
            "gorgon-family Y raise:\n\n"
            f"{bullet_list(config, shaping_problems)}",
        )


DOCS_TABLE_ROW_RE: Final = re.compile(
    r"<tr>.*?"
    r"<span class=\"neanes\">&#x([0-9A-Fa-f]+);</span>.*?"
    r"<div class=\"code-point\">\s*(U\+[0-9A-Fa-f]{4,6})\s*</div>.*?"
    r"<div class=\"glyph-name\">\s*([^<]+?)\s*</div>.*?"
    r"</tr>",
    re.DOTALL,
)


def _expected_glyphs(include_optional: bool = True) -> dict[int, str]:
    if include_optional:
        return dict(SBMUFL_NAMELIST_GLYPHS)
    return dict(SBMUFL_REQUIRED_GLYPHS)


def _expected_by_name(include_optional: bool = True) -> dict[str, int]:
    return {
        name: codepoint
        for codepoint, name in _expected_glyphs(include_optional).items()
    }


def _load_json(path: Path, problems: list[str]) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as infile:
            return cast(dict[str, Any], json.load(infile))
    except FileNotFoundError:
        problems.append(f"Missing file: {path.relative_to(REPO_ROOT)}")
    except json.JSONDecodeError as e:
        problems.append(
            f"Invalid JSON in {path.relative_to(REPO_ROOT)}: line {e.lineno}, column {e.colno}"
        )
    return None


def _parse_docs_tables(problems: list[str]) -> list[tuple[Path, int, str]]:
    entries: list[tuple[Path, int, str]] = []
    if not DOCS_TABLES_PATH.exists():
        problems.append(f"Missing directory: {DOCS_TABLES_PATH.relative_to(REPO_ROOT)}")
        return entries

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

    return entries


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


def _check_docs_tables() -> list[str]:
    problems: list[str] = []
    expected_by_name = _expected_by_name(include_optional=True)
    entries = _parse_docs_tables(problems)
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
        _compare_glyph_map("docs/tables/*.md", actual_by_name, expected_by_name)
    )
    return problems


def _check_glyphnames_json() -> list[str]:
    problems: list[str] = []
    expected_by_name = _expected_by_name(include_optional=True)
    glyphnames = _load_json(GLYPHNAMES_PATH, problems)
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
        _compare_glyph_map("metadata/glyphnames.json", actual_by_name, expected_by_name)
    )
    return problems


def _check_ranges_json() -> list[str]:
    problems: list[str] = []
    expected_by_name = _expected_by_name(include_optional=False)
    ranges = _load_json(RANGES_PATH, problems)
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
            expected_codepoint = expected_by_name.get(glyph_name)
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
        _compare_glyph_map("metadata/ranges.json", actual_by_name, expected_by_name)
    )
    return problems


def _check_neanes_metadata_json() -> list[str]:
    problems: list[str] = []
    metadata = _load_json(NEANES_METADATA_PATH, problems)
    if metadata is None:
        return problems

    expected_by_name = _expected_by_name(include_optional=True)
    for section in ("glyphAdvanceWidths", "glyphBBoxes"):
        actual = metadata.get(section)
        if not isinstance(actual, dict):
            problems.append(
                f"fonts/neanes.metadata.json is missing object section {section}"
            )
            continue
        problems.extend(
            _compare_name_set(
                f"fonts/neanes.metadata.json {section}", actual, expected_by_name
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


@check(
    id="sbmufl/repository_metadata_consistency",
    rationale="""
        SBMuFL keeps the canonical glyph inventory in several repository files:
        the Adobe Glyph List style namelist, documentation tables, range
        metadata, and generated font metadata. These files must describe the
        same glyph names and codepoints so implementers can use any of them
        without encountering stale or incomplete data.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_repository_metadata_consistency(
    config: Any,
) -> Iterator[tuple[Any, Message]]:
    """Check that SBMuFL repository metadata files are complete and in sync."""
    problems: list[str] = []
    namelist = _parse_namelist(problems)
    namelist_by_name = {name: codepoint for codepoint, name in namelist.items()}
    problems.extend(
        _compare_glyph_map(
            "sources/namelist.txt",
            namelist_by_name,
            _expected_by_name(include_optional=True),
        )
    )
    problems.extend(_check_docs_tables())
    problems.extend(_check_glyphnames_json())
    problems.extend(_check_ranges_json())
    problems.extend(_check_neanes_metadata_json())

    if problems:
        yield FAIL, Message(
            "inconsistent-repository-metadata",
            "SBMuFL repository metadata is incomplete or inconsistent:\n\n"
            f"{bullet_list(config, problems)}",
        )
