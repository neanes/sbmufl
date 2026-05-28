from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, cast

from fontbakery.prelude import FAIL, WARN, Message
from fontbakery.prelude import check as fontbakery_check
from fontbakery.utils import bullet_list
from fontTools.ttLib.tables import otTables

SBMUFL_GLYPHS: Final[dict[int, str]] = {
    0xE000: "ison",
    0xE001: "oligon",
    0xE002: "oligonKentimaMiddle",
    0xE003: "oligonKentimaBelow",
    0xE004: "oligonKentimaAbove",
    0xE005: "oligonYpsiliRight",
    0xE006: "oligonYpsiliLeft",
    0xE007: "oligonKentimaYpsiliRight",
    0xE008: "oligonKentimaYpsiliMiddle",
    0xE009: "oligonDoubleYpsili",
    0xE00A: "oligonKentimataDoubleYpsili",
    0xE00B: "oligonKentimaDoubleYpsiliRight",
    0xE00C: "oligonKentimaDoubleYpsiliLeft",
    0xE00D: "oligonTripleYpsili",
    0xE00E: "oligonKentimataTripleYpsili",
    0xE00F: "oligonKentimaTripleYpsili",
    0xE010: "oligonIson",
    0xE011: "oligonApostrofos",
    0xE012: "oligonYporroi",
    0xE013: "oligonElafron",
    0xE014: "oligonElafronApostrofos",
    0xE015: "oligonChamili",
    0xE020: "isonApostrofos",
    0xE021: "apostrofos",
    0xE022: "apostrofosSyndesmos",
    0xE023: "yporroi",
    0xE024: "elafron",
    0xE025: "runningElafron",
    0xE026: "elafronApostrofos",
    0xE027: "chamili",
    0xE028: "chamiliApostrofos",
    0xE029: "chamiliElafron",
    0xE02A: "chamiliElafronApostrofos",
    0xE02B: "doubleChamili",
    0xE02C: "doubleChamiliApostrofos",
    0xE02D: "doubleChamiliElafron",
    0xE02E: "doubleChamiliElafronApostrofos",
    0xE02F: "tripleChamili",
    0xE040: "petastiIson",
    0xE041: "petasti",
    0xE042: "petastiOligon",
    0xE043: "petastiKentima",
    0xE044: "petastiYpsiliRight",
    0xE045: "petastiYpsiliLeft",
    0xE046: "petastiKentimaYpsiliRight",
    0xE047: "petastiKentimaYpsiliMiddle",
    0xE048: "petastiDoubleYpsili",
    0xE049: "petastiKentimataDoubleYpsili",
    0xE04A: "petastiKentimaDoubleYpsiliRight",
    0xE04B: "petastiKentimaDoubleYpsiliLeft",
    0xE04C: "petastiTripleYpsili",
    0xE04D: "petastiKentimataTripleYpsili",
    0xE04E: "petastiKentimaTripleYpsili",
    0xE060: "petastiApostrofos",
    0xE061: "petastiYporroi",
    0xE062: "petastiElafron",
    0xE063: "petastiRunningElafron",
    0xE064: "petastiElafronApostrofos",
    0xE065: "petastiChamili",
    0xE066: "petastiChamiliApostrofos",
    0xE067: "petastiChamiliElafron",
    0xE068: "petastiChamiliElafronApostrofos",
    0xE069: "petastiDoubleChamili",
    0xE06A: "petastiDoubleChamiliApostrofos",
    0xE080: "kentima",
    0xE081: "kentimata",
    0xE082: "oligonKentimataBelow",
    0xE083: "oligonKentimataAbove",
    0xE084: "oligonIsonKentimata",
    0xE085: "oligonKentimaMiddleKentimata",
    0xE086: "oligonYpsiliRightKentimata",
    0xE087: "oligonYpsiliLeftKentimata",
    0xE088: "oligonApostrofosKentimata",
    0xE089: "oligonYporroiKentimata",
    0xE08A: "oligonElafronKentimata",
    0xE08B: "oligonRunningElafronKentimata",
    0xE08C: "oligonElafronApostrofosKentimata",
    0xE08D: "oligonChamiliKentimata",
    0xE0A0: "vareia",
    0xE0A1: "psifiston",
    0xE0A2: "antikenoma",
    0xE0A3: "omalon",
    0xE0A4: "omalonConnecting",
    0xE0A5: "heteron",
    0xE0A6: "heteronConnecting",
    0xE0A7: "endofonon",
    0xE0B0: "yfenAbove",
    0xE0B1: "yfenBelow",
    0xE0C0: "stavros",
    0xE0C1: "breath",
    0xE0C8: "stavrosAbove",
    0xE0D0: "klasmaAbove",
    0xE0D1: "klasmaBelow",
    0xE0D2: "apli",
    0xE0D3: "dipli",
    0xE0D4: "tripli",
    0xE0D5: "tetrapli",
    0xE0D6: "koronis",
    0xE0E0: "leimma1",
    0xE0E1: "leimma2",
    0xE0E2: "leimma3",
    0xE0E3: "leimma4",
    0xE0E4: "leimmaDot",
    0xE0F0: "gorgonAbove",
    0xE0F1: "gorgonBelow",
    0xE0F2: "gorgonDottedLeft",
    0xE0F3: "gorgonDottedRight",
    0xE0F4: "digorgon",
    0xE0F5: "digorgonDottedLeftBelow",
    0xE0F6: "digorgonDottedLeftAbove",
    0xE0F7: "digorgonDottedRight",
    0xE0F8: "trigorgon",
    0xE0F9: "trigorgonDottedLeftBelow",
    0xE0FA: "trigorgonDottedLeftAbove",
    0xE0FB: "trigorgonDottedRight",
    0xE0FC: "argon",
    0xE0FD: "diargon",
    0xE0FE: "triargon",
    0xE100: "gorgonSecondary",
    0xE101: "gorgonDottedLeftSecondary",
    0xE102: "gorgonDottedRightSecondary",
    0xE103: "digorgonSecondary",
    0xE104: "digorgonDottedLeftBelowSecondary",
    0xE105: "digorgonDottedRightSecondary",
    0xE106: "trigorgonSecondary",
    0xE107: "trigorgonDottedLeftBelowSecondary",
    0xE108: "trigorgonDottedRightSecondary",
    0xE109: "digorgonDottedLeftSecondary",
    0xE10A: "trigorgonDottedLeftSecondary",
    0xE120: "agogiPoliArgi",
    0xE121: "agogiArgoteri",
    0xE122: "agogiArgi",
    0xE123: "agogiMetria",
    0xE124: "agogiMesi",
    0xE125: "agogiGorgi",
    0xE126: "agogiGorgoteri",
    0xE127: "agogiPoliGorgi",
    0xE128: "agogiPoliArgiAbove",
    0xE129: "agogiArgoteriAbove",
    0xE12A: "agogiArgiAbove",
    0xE12B: "agogiMetriaAbove",
    0xE12C: "agogiMesiAbove",
    0xE12D: "agogiGorgiAbove",
    0xE12E: "agogiGorgoteriAbove",
    0xE12F: "agogiPoliGorgiAbove",
    0xE130: "martyriaNoteZoLow",
    0xE131: "martyriaNoteNiLow",
    0xE132: "martyriaNotePaLow",
    0xE133: "martyriaNoteVouLow",
    0xE134: "martyriaNoteGaLow",
    0xE135: "martyriaNoteDiLow",
    0xE136: "martyriaNoteKeLow",
    0xE137: "martyriaNoteZo",
    0xE138: "martyriaNoteNi",
    0xE139: "martyriaNotePa",
    0xE13A: "martyriaNoteVou",
    0xE13B: "martyriaNoteGa",
    0xE13C: "martyriaNoteDi",
    0xE13D: "martyriaNoteKe",
    0xE13E: "martyriaNoteZoHigh",
    0xE13F: "martyriaNoteNiHigh",
    0xE140: "martyriaNotePaHigh",
    0xE141: "martyriaNoteVouHigh",
    0xE142: "martyriaNoteGaHigh",
    0xE143: "martyriaNoteDiHigh",
    0xE144: "martyriaNoteKeHigh",
    0xE145: "martyriaTick",
    0xE150: "martyriaZoBelow",
    0xE151: "martyriaDeltaBelow",
    0xE152: "martyriaAlphaBelow",
    0xE153: "martyriaLegetosBelow",
    0xE154: "martyriaNanaBelow",
    0xE155: "martyriaDeltaDottedBelow",
    0xE156: "martyriaAlphaDottedBelow",
    0xE157: "martyriaHardChromaticPaBelow",
    0xE158: "martyriaHardChromaticDiBelow",
    0xE159: "martyriaSoftChromaticDiBelow",
    0xE15A: "martyriaSoftChromaticKeBelow",
    0xE15B: "martyriaZygosBelow",
    0xE170: "martyriaZoAbove",
    0xE171: "martyriaDeltaAbove",
    0xE172: "martyriaAlphaAbove",
    0xE173: "martyriaLegetosAbove",
    0xE174: "martyriaNanaAbove",
    0xE175: "martyriaDeltaDottedAbove",
    0xE176: "martyriaAlphaDottedAbove",
    0xE177: "martyriaHardChromaticPaAbove",
    0xE178: "martyriaHardChromaticDiAbove",
    0xE179: "martyriaSoftChromaticDiAbove",
    0xE17A: "martyriaSoftChromaticKeAbove",
    0xE17B: "martyriaZygosAbove",
    0xE190: "fthoraDiatonicNiLowAbove",
    0xE191: "fthoraDiatonicPaAbove",
    0xE192: "fthoraDiatonicVouAbove",
    0xE193: "fthoraDiatonicGaAbove",
    0xE194: "fthoraDiatonicDiAbove",
    0xE195: "fthoraDiatonicKeAbove",
    0xE196: "fthoraDiatonicZoAbove",
    0xE197: "fthoraDiatonicNiHighAbove",
    0xE198: "fthoraHardChromaticPaAbove",
    0xE199: "fthoraHardChromaticDiAbove",
    0xE19A: "fthoraSoftChromaticDiAbove",
    0xE19B: "fthoraSoftChromaticKeAbove",
    0xE19C: "fthoraEnharmonicAbove",
    0xE19D: "chroaZygosAbove",
    0xE19E: "chroaKlitonAbove",
    0xE19F: "chroaSpathiAbove",
    0xE1A0: "fthoraDiatonicNiLowSecondary",
    0xE1A1: "fthoraDiatonicPaSecondary",
    0xE1A2: "fthoraDiatonicVouSecondary",
    0xE1A3: "fthoraDiatonicGaSecondary",
    0xE1A4: "fthoraDiatonicDiSecondary",
    0xE1A5: "fthoraDiatonicKeSecondary",
    0xE1A6: "fthoraDiatonicZoSecondary",
    0xE1A7: "fthoraDiatonicNiHighSecondary",
    0xE1A8: "fthoraHardChromaticPaSecondary",
    0xE1A9: "fthoraHardChromaticDiSecondary",
    0xE1AA: "fthoraSoftChromaticDiSecondary",
    0xE1AB: "fthoraSoftChromaticKeSecondary",
    0xE1AC: "fthoraEnharmonicSecondary",
    0xE1AD: "chroaZygosSecondary",
    0xE1AE: "chroaKlitonSecondary",
    0xE1AF: "chroaSpathiSecondary",
    0xE1B0: "fthoraDiatonicNiLowTertiary",
    0xE1B1: "fthoraDiatonicPaTertiary",
    0xE1B2: "fthoraDiatonicVouTertiary",
    0xE1B3: "fthoraDiatonicGaTertiary",
    0xE1B4: "fthoraDiatonicDiTertiary",
    0xE1B5: "fthoraDiatonicKeTertiary",
    0xE1B6: "fthoraDiatonicZoTertiary",
    0xE1B7: "fthoraDiatonicNiHighTertiary",
    0xE1B8: "fthoraHardChromaticPaTertiary",
    0xE1B9: "fthoraHardChromaticDiTertiary",
    0xE1BA: "fthoraSoftChromaticDiTertiary",
    0xE1BB: "fthoraSoftChromaticKeTertiary",
    0xE1BC: "fthoraEnharmonicTertiary",
    0xE1BD: "chroaZygosTertiary",
    0xE1BE: "chroaKlitonTertiary",
    0xE1BF: "chroaSpathiTertiary",
    0xE1C0: "fthoraDiatonicNiLowBelow",
    0xE1C1: "fthoraDiatonicPaBelow",
    0xE1C2: "fthoraDiatonicVouBelow",
    0xE1C3: "fthoraDiatonicGaBelow",
    0xE1C4: "fthoraDiatonicDiBelow",
    0xE1C5: "fthoraDiatonicKeBelow",
    0xE1C6: "fthoraDiatonicZoBelow",
    0xE1C7: "fthoraDiatonicNiHighBelow",
    0xE1C8: "fthoraHardChromaticPaBelow",
    0xE1C9: "fthoraHardChromaticDiBelow",
    0xE1CA: "fthoraSoftChromaticDiBelow",
    0xE1CB: "fthoraSoftChromaticKeBelow",
    0xE1CC: "fthoraEnharmonicBelow",
    0xE1CD: "chroaZygosBelow",
    0xE1CE: "chroaKlitonBelow",
    0xE1CF: "chroaSpathiBelow",
    0xE1D0: "fthoraDiatonicNiLow",
    0xE1D1: "fthoraDiatonicPa",
    0xE1D2: "fthoraDiatonicVou",
    0xE1D3: "fthoraDiatonicGa",
    0xE1D4: "fthoraDiatonicDi",
    0xE1D5: "fthoraDiatonicKe",
    0xE1D6: "fthoraDiatonicZo",
    0xE1D7: "fthoraDiatonicNiHigh",
    0xE1D8: "fthoraHardChromaticPa",
    0xE1D9: "fthoraHardChromaticDi",
    0xE1DA: "fthoraSoftChromaticDi",
    0xE1DB: "fthoraSoftChromaticKe",
    0xE1DC: "fthoraEnharmonic",
    0xE1DD: "chroaZygos",
    0xE1DE: "chroaKliton",
    0xE1DF: "chroaSpathi",
    0xE1F0: "diesis2",
    0xE1F1: "diesis4",
    0xE1F2: "diesis6",
    0xE1F3: "diesis8",
    0xE1F4: "diesisGenikiAbove",
    0xE1F5: "diesisGenikiBelow",
    0xE1F6: "diesis2Secondary",
    0xE1F7: "diesis4Secondary",
    0xE1F8: "diesis6Secondary",
    0xE1F9: "diesis8Secondary",
    0xE1FA: "diesis2Tertiary",
    0xE1FB: "diesis4Tertiary",
    0xE1FC: "diesis6Tertiary",
    0xE1FD: "diesis8Tertiary",
    0xE1FE: "diesisGenikiSecondary",
    0xE1FF: "diesisGenikiTertiary",
    0xE200: "yfesis2",
    0xE201: "yfesis4",
    0xE202: "yfesis6",
    0xE203: "yfesis8",
    0xE204: "yfesisGenikiAbove",
    0xE205: "yfesisGenikiBelow",
    0xE206: "yfesis2Secondary",
    0xE207: "yfesis4Secondary",
    0xE208: "yfesis6Secondary",
    0xE209: "yfesis8Secondary",
    0xE20A: "yfesis2Tertiary",
    0xE20B: "yfesis4Tertiary",
    0xE20C: "yfesis6Tertiary",
    0xE20D: "yfesis8Tertiary",
    0xE20E: "yfesisGenikiSecondary",
    0xE20F: "yfesisGenikiTertiary",
    0xE210: "barlineSingle",
    0xE211: "barlineDouble",
    0xE212: "barlineTheseos",
    0xE213: "barlineShortSingle",
    0xE214: "barlineShortDouble",
    0xE215: "barlineShortTheseos",
    0xE216: "barlineSingleAbove",
    0xE217: "barlineDoubleAbove",
    0xE218: "barlineTheseosAbove",
    0xE219: "barlineShortSingleAbove",
    0xE21A: "barlineShortDoubleAbove",
    0xE21B: "barlineShortTheseosAbove",
    0xE220: "measureNumber2",
    0xE221: "measureNumber3",
    0xE222: "measureNumber4",
    0xE223: "measureNumber5",
    0xE224: "measureNumber6",
    0xE225: "measureNumber7",
    0xE226: "measureNumber8",
    0xE250: "noteIndicatorNi",
    0xE251: "noteIndicatorPa",
    0xE252: "noteIndicatorVou",
    0xE253: "noteIndicatorGa",
    0xE254: "noteIndicatorDi",
    0xE255: "noteIndicatorKe",
    0xE256: "noteIndicatorZo",
    0xE260: "isonIndicatorUnison",
    0xE261: "isonIndicatorDiLow",
    0xE262: "isonIndicatorKeLow",
    0xE263: "isonIndicatorZo",
    0xE264: "isonIndicatorNi",
    0xE265: "isonIndicatorPa",
    0xE266: "isonIndicatorVou",
    0xE267: "isonIndicatorGa",
    0xE268: "isonIndicatorDi",
    0xE269: "isonIndicatorKe",
    0xE26A: "isonIndicatorZoHigh",
    0xE280: "gorthmikon",
    0xE281: "pelastikon",
    0xE2A0: "modeFirst",
    0xE2A8: "modeSecond",
    0xE2B0: "modeThird",
    0xE2B1: "modeThirdNana",
    0xE2B8: "modeFourth",
    0xE2BA: "modeLegetos",
    0xE2C0: "modePlagalFirst",
    0xE2C8: "modePlagalSecond",
    0xE2D0: "modeVarys",
    0xE2D1: "modeVarys2",
    0xE2D8: "modePlagalFourth",
    0xE2E0: "modeNi",
    0xE2E1: "modePa",
    0xE2E2: "modeVou",
    0xE2E3: "modeGa",
    0xE2E4: "modeDi",
    0xE2E5: "modeKe",
    0xE2E6: "modeZo",
    0xE2E7: "modeOligonKentimaAbove",
    0xE2E8: "modeOligonYpsili",
    0xE2E9: "modeElafron",
    0xE2EA: "modeRunningElafron",
    0xE2F0: "modePlagal",
    0xE2F1: "modeWordEchos",
    0xE2F2: "modeWordVarys",
    0xE2F3: "modeAlpha",
    0xE2F4: "modeBeta",
    0xE2F5: "modeGamma",
    0xE2F6: "modeDelta",
    0xE2F7: "modeAlphaCapital",
    0xE2F8: "modeBetaCapital",
    0xE2F9: "modeGammaCapital",
    0xE2FA: "modeDeltaCapital",
}

SBMUFL_OPTIONAL_GLYPHS: Final[dict[int, str]] = {
    0xF000: "oligonKentimataBelow.alt01",
    0xF001: "oligonKentimataAbove.alt01",
    0xF002: "antikenoma.alt01",
    0xF003: "modeFirst.salt01",
    0xF004: "modeFourth.salt01",
    0xF005: "oligonKentimataBelow.alt02",
    0xF006: "psifiston.salt01",
    0xF007: "heteronConnecting.salt01",
    0xF008: "psifiston.alt01",
    0xF009: "yporroi.gorgon",
    0xF00A: "yporroi.digorgon",
    0xF00B: "yporroi.trigorgon",
}

SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME: Final[dict[str, int]] = {
    glyph_name: codepoint for codepoint, glyph_name in SBMUFL_OPTIONAL_GLYPHS.items()
}

SBMUFL_RESERVED_RANGE: Final = range(0xE430, 0xF000)
SBMUFL_OPTIONAL_RANGE: Final = range(0xF000, 0xF900)

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
}

SBMUFL_MARK_TO_MARK_CODEPOINTS: Final[set[int]] = {
    # Tempo marks and combining barline marks are expected to stack on marks.
    *range(0xE128, 0xE130),
    *range(0xE216, 0xE21C),
}


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
    missing = sorted(set(SBMUFL_GLYPHS) - set(cmap))

    missing_glyph_names = [
        f"U+{codepoint:04X} {glyph_name}"
        for codepoint, glyph_name in sorted(SBMUFL_GLYPHS.items())
        if codepoint not in cmap and glyph_name not in glyph_order
    ]

    inconsistent_names = [
        f"U+{codepoint:04X} {glyph_name} (expected {SBMUFL_GLYPHS[codepoint]})"
        for codepoint, glyph_name in sorted(cmap.items())
        if codepoint in SBMUFL_GLYPHS and glyph_name != SBMUFL_GLYPHS[codepoint]
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
            f"U+{codepoint:04X} {SBMUFL_GLYPHS[codepoint]}" for codepoint in missing
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
        SBMUFL_MARK_CODEPOINTS.intersection(SBMUFL_GLYPHS).intersection(cmap)
    )
    encoded_mark_to_mark_codepoints = sorted(
        SBMUFL_MARK_TO_MARK_CODEPOINTS.intersection(SBMUFL_GLYPHS).intersection(cmap)
    )

    for codepoint in encoded_mark_codepoints:
        glyph_name = cmap[codepoint]

        expected_glyph_name = SBMUFL_GLYPHS[codepoint]
        label = _cmap_label(codepoint, expected_glyph_name, glyph_name)
        if glyph_classes.get(glyph_name) != 3:
            missing_gdef.append(label)
        if glyph_name not in mark_to_base_glyphs:
            missing_mark_to_base.append(label)

    for codepoint in encoded_mark_to_mark_codepoints:
        glyph_name = cmap[codepoint]

        if glyph_name not in mark_to_mark_glyphs:
            expected_glyph_name = SBMUFL_GLYPHS[codepoint]
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


REPO_ROOT: Final = Path(__file__).resolve().parents[2]
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


def _expected_glyphs(include_optional: bool = True) -> dict[int, str]:
    glyphs = dict(SBMUFL_GLYPHS)
    if include_optional:
        glyphs.update(SBMUFL_OPTIONAL_GLYPHS)
    return glyphs


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


def _parse_namelist(problems: list[str]) -> dict[str, int]:
    glyphs: dict[str, int] = {}
    try:
        lines = NAMELIST_PATH.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        problems.append(f"Missing file: {NAMELIST_PATH.relative_to(REPO_ROOT)}")
        return glyphs

    for line_number, line in enumerate(lines, start=1):
        match = NAMELIST_RE.match(line)
        if not match:
            continue
        codepoint = int(match.group(1), 16)
        glyph_name = match.group(2)
        if glyph_name in glyphs:
            previous_codepoint = glyphs[glyph_name]
            problems.append(
                "Duplicate namelist glyph "
                f"{glyph_name}: U+{previous_codepoint:04X} and U+{codepoint:04X}"
            )
        glyphs[glyph_name] = codepoint

    return glyphs


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
    problems.extend(
        _compare_glyph_map(
            "sources/namelist.txt",
            namelist,
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
