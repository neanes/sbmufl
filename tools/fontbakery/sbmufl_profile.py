from typing import Any, Final

PROFILE: Final[dict[str, Any]] = {
    "name": "sbmufl",
    "check_definitions": ["tools/fontbakery/sbmufl_checks.py"],
    "sections": {
        "SBMuFL Checks": [
            "sbmufl/glyph_coverage",
            "sbmufl/reserved_codepoints",
            "sbmufl/mark_positioning",
            "sbmufl/mark_attachment",
            "sbmufl/repository_metadata_consistency",
        ],
    },
}
