from __future__ import annotations

from pathlib import Path
from typing import Any

import uharfbuzz as hb


class Shaper:
    def __init__(self, font_data: bytes, glyph_order: list[str]) -> None:
        self.glyph_order = glyph_order
        self.face = hb.Face(font_data)
        self.font = hb.Font(self.face)
        hb.ot_font_set_funcs(self.font)

    @classmethod
    def from_ttfont(cls, ttfont: Any) -> Shaper:
        font_path = Path(ttfont.reader.file.name)
        return cls(font_path.read_bytes(), ttfont.getGlyphOrder())

    def position_of(self, text: str, glyph_name: str) -> tuple[int, int] | None:
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.font, buffer)

        x = 0
        y = 0
        for glyph_info, glyph_position in zip(
            buffer.glyph_infos,
            buffer.glyph_positions,
            strict=True,
        ):
            if self.glyph_order[glyph_info.codepoint] == glyph_name:
                return x + glyph_position.x_offset, y + glyph_position.y_offset
            x += glyph_position.x_advance
            y += glyph_position.y_advance

        return None

    def position_of_codepoints(
        self, codepoints: list[int], glyph_name: str
    ) -> tuple[int, int] | None:
        return self.position_of(
            "".join(chr(codepoint) for codepoint in codepoints), glyph_name
        )
