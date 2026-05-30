from typing import Any, Final

PROFILE: Final[dict[str, Any]] = {
    "name": "sbmufl",
    "check_definitions": ["tools/fontbakery/sbmufl/checks.py"],
    "sections": {
        "SBMuFL Checks": [
            "sbmufl/glyph_coverage",
            "sbmufl/reserved_codepoints",
            "sbmufl/mark_positioning",
            "sbmufl/mark_attachment",
            "sbmufl/contextual_subtable_count",
            "sbmufl/contextual_prompt_probe_cases",
            "sbmufl/fthora_contextual_positioning",
            "sbmufl/ison_contextual_positioning",
            "sbmufl/koronis_contextual_positioning",
            "sbmufl/repository_metadata_consistency",
        ],
    },
}
