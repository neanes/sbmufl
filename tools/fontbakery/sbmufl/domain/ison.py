from __future__ import annotations

import math
from collections.abc import Mapping

from ..constants import SBMUFL_ISON_INDICATOR_CLEARANCE


def expected_base_y_by_name(
    reference_y: int,
    glyph_ymax_by_name: Mapping[str, float],
    compromise_glyph_names: set[str],
) -> dict[str, int]:
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
    return expected_y_by_name
