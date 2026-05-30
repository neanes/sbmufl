from __future__ import annotations

import re
from pathlib import Path
from typing import Final

REPO_ROOT: Final = Path(__file__).resolve().parents[3]
DOCS_TABLES_PATH: Final = REPO_ROOT / "docs" / "tables"
NAMELIST_PATH: Final = REPO_ROOT / "sources" / "namelist.txt"
GLYPHNAMES_PATH: Final = REPO_ROOT / "metadata" / "glyphnames.json"
RANGES_PATH: Final = REPO_ROOT / "metadata" / "ranges.json"
NEANES_METADATA_PATH: Final = REPO_ROOT / "fonts" / "neanes.metadata.json"
NAMELIST_RE: Final = re.compile(r"^0x([0-9A-Fa-f]+)\s+(\S+)\s*$")
DOCS_TABLE_ROW_RE: Final = re.compile(
    r"<tr>.*?"
    r"<span class=\"neanes\">&#x([0-9A-Fa-f]+);</span>.*?"
    r"<div class=\"code-point\">\s*(U\+[0-9A-Fa-f]{4,6})\s*</div>.*?"
    r"<div class=\"glyph-name\">\s*([^<]+?)\s*</div>.*?"
    r"</tr>",
    re.DOTALL,
)


def parse_namelist(path: Path = NAMELIST_PATH) -> tuple[dict[int, str], list[str]]:
    glyphs: dict[int, str] = {}
    glyph_names: dict[str, int] = {}
    problems: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        problems.append(f"Missing file: {path.relative_to(REPO_ROOT)}")
        return glyphs, problems

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

    return glyphs, problems


SBMUFL_OPTIONAL_RANGE: Final = range(0xF000, 0xF900)
SBMUFL_RESERVED_RANGE: Final = range(0xE430, 0xF000)

SBMUFL_NAMELIST_GLYPHS: Final[dict[int, str]] = parse_namelist()[0]

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
SBMUFL_CONTEXTUAL_SUBTABLE_LIMITS: Final[tuple[tuple[str, int], ...]] = (
    ("fthora_gorgon", 64),
    ("fthora_klasma", 64),
    ("secondary_fthora_secondary_gorgon", 64),
    ("ison_gorgon", 64),
    ("ison_klasma", 64),
    ("ison_fthora", 64),
    ("ison_secondary_fthora", 64),
    ("ison_tertiary_fthora", 64),
    ("ison_gorgon_correction", 64),
    ("ison_klasma_correction", 64),
    ("ison_secondary_fthora_correction", 64),
    ("fthora_klasma_gorgon_correction", 64),
    ("ison_klasma_gorgon_correction", 64),
    ("koronis_klasma", 64),
    ("koronis_gorgon", 64),
    ("koronis_fthora", 64),
    ("koronis_klasma_correction", 64),
    ("koronis_gorgon_correction", 64),
    ("koronis_klasma_gorgon_correction", 64),
)
SBMUFL_CONTEXTUAL_LOOKUP_COUNT: Final = len(SBMUFL_CONTEXTUAL_SUBTABLE_LIMITS)
SBMUFL_KORONIS_CODEPOINTS: Final[set[int]] = {0xE0D6}
SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT: Final = 0xE0D6
SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT: Final = 0xE190
SBMUFL_SECONDARY_FTHORA_SHAPING_PROBE_CODEPOINT: Final = 0xE1A0
SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT: Final = 0xE0D0
SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT: Final = 0xE0F0
SBMUFL_SECONDARY_GORGON_SHAPING_PROBE_CODEPOINT: Final = 0xE100
SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT: Final = 0xE0F4
SBMUFL_TRIGORGON_SHAPING_PROBE_CODEPOINT: Final = 0xE0F8
SBMUFL_APOSTROFOS_SHAPING_PROBE_CODEPOINT: Final = 0xE021
SBMUFL_ELAFRON_SHAPING_PROBE_CODEPOINT: Final = 0xE024
SBMUFL_DOUBLE_CHAMILI_SHAPING_PROBE_CODEPOINT: Final = 0xE02B
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
    0xE0F5,  # U+E0F5 digorgonDottedLeftBelow
    0xE0F6,  # U+E0F6 digorgonDottedLeftAbove
    0xE0F7,  # U+E0F7 digorgonDottedRight
    0xE0F8,  # U+E0F8 trigorgon
    0xE0F9,  # U+E0F9 trigorgonDottedLeftBelow
    0xE0FA,  # U+E0FA trigorgonDottedLeftAbove
    0xE0FB,  # U+E0FB trigorgonDottedRight
}
SBMUFL_GORGON_SECONDARY_ABOVE_CODEPOINTS: Final[set[int]] = {
    # Secondary above gorgon-family marks.
    0xE100,  # U+E100 gorgonSecondary
    0xE101,  # U+E101 gorgonDottedLeftSecondary
    0xE102,  # U+E102 gorgonDottedRightSecondary
    0xE103,  # U+E103 digorgonSecondary
    0xE104,  # U+E104 digorgonDottedLeftBelowSecondary
    0xE105,  # U+E105 digorgonDottedRightSecondary
    0xE106,  # U+E106 trigorgonSecondary
    0xE107,  # U+E107 trigorgonDottedLeftBelowSecondary
    0xE108,  # U+E108 trigorgonDottedRightSecondary
    0xE109,  # U+E109 digorgonDottedLeftSecondary
    0xE10A,  # U+E10A trigorgonDottedLeftSecondary
}
SBMUFL_GORGON_ABOVE_CODEPOINTS: Final[set[int]] = (
    SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS | SBMUFL_GORGON_SECONDARY_ABOVE_CODEPOINTS
)
SBMUFL_KLASMA_ABOVE_CODEPOINTS: Final[set[int]] = {0xE0D0}
SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS: Final[set[int]] = set(range(0xE190, 0xE1A0))
SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS: Final[set[int]] = set(range(0xE1A0, 0xE1B0))
SBMUFL_FTHORA_TERTIARY_ABOVE_CODEPOINTS: Final[set[int]] = set(range(0xE1B0, 0xE1C0))
SBMUFL_FTHORA_ABOVE_CODEPOINTS: Final[set[int]] = (
    SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS
    | SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS
    | SBMUFL_FTHORA_TERTIARY_ABOVE_CODEPOINTS
)


def expected_glyphs(include_optional: bool = True) -> dict[int, str]:
    if include_optional:
        return dict(SBMUFL_NAMELIST_GLYPHS)
    return dict(SBMUFL_REQUIRED_GLYPHS)


def expected_by_name(include_optional: bool = True) -> dict[str, int]:
    return {
        name: codepoint for codepoint, name in expected_glyphs(include_optional).items()
    }
