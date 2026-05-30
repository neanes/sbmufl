from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cached_property
from typing import Any, cast

from fontTools.pens.boundsPen import BoundsPen


class GlyphIntrospector:
    def __init__(self, ttfont: Any) -> None:
        self.ttfont = ttfont

    @cached_property
    def cmap(self) -> Mapping[int, str]:
        return cast(Mapping[int, str], self.ttfont.getBestCmap() or {})

    @cached_property
    def all_cmap_items(self) -> list[tuple[int, str]]:
        cmap_table = self.ttfont.get("cmap")
        if cmap_table is None:
            return []

        items: set[tuple[int, str]] = set()
        for subtable in cmap_table.tables:
            items.update(subtable.cmap.items())
        return sorted(items)

    @cached_property
    def glyph_names(self) -> set[str]:
        return set(self.ttfont.getGlyphOrder())

    @cached_property
    def glyph_order(self) -> Sequence[str]:
        return cast(Sequence[str], self.ttfont.getGlyphOrder())

    @cached_property
    def gdef_classes(self) -> Mapping[str, int]:
        if "GDEF" not in self.ttfont:
            return {}

        glyph_class_def = self.ttfont["GDEF"].table.GlyphClassDef
        if glyph_class_def is None:
            return {}

        return cast(Mapping[str, int], glyph_class_def.classDefs)

    def glyph_ymax(self, glyph_name: str) -> float | None:
        glyph_set = self.ttfont.getGlyphSet()
        if glyph_name not in glyph_set:
            return None

        pen = BoundsPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        if pen.bounds is None:
            return None
        return cast(float, pen.bounds[3])

    def encoded_glyph_names(self, codepoints: set[int]) -> set[str]:
        return {
            self.cmap[codepoint] for codepoint in sorted(codepoints & self.cmap.keys())
        }

    def codepoint_for_glyph_name(self, glyph_name: str) -> int | None:
        for codepoint, name in self.cmap.items():
            if name == glyph_name:
                return codepoint
        return None


def cmap_label(
    codepoint: int,
    expected_glyph_name: str,
    actual_glyph_name: str | None,
) -> str:
    actual_glyph_suffix = (
        "" if actual_glyph_name == expected_glyph_name else f" ({actual_glyph_name})"
    )
    return f"U+{codepoint:04X} {expected_glyph_name}{actual_glyph_suffix}"
