from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

from fontTools.ttLib.tables import otTables

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sbmufl.constants import (  # noqa: E402
    SBMUFL_CONTEXTUAL_LOOKUP_COUNT,
    SBMUFL_CONTEXTUAL_SUBTABLE_LIMITS,
    SBMUFL_FTHORA_ABOVE_CODEPOINTS,
    SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS,
    SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS,
    SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
    SBMUFL_FTHORA_TERTIARY_ABOVE_CODEPOINTS,
    SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS,
    SBMUFL_ISON_INDICATOR_CODEPOINTS,
    SBMUFL_ISON_INDICATOR_COMPROMISE_CODEPOINTS,
    SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
    SBMUFL_KLASMA_ABOVE_CODEPOINTS,
    SBMUFL_KORONIS_CODEPOINTS,
    SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
    SBMUFL_MARK_CODEPOINTS,
    SBMUFL_MARK_TO_MARK_CODEPOINTS,
    SBMUFL_NAMELIST_GLYPHS,
    SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME,
    SBMUFL_OPTIONAL_GLYPHS,
    SBMUFL_REQUIRED_GLYPHS,
    SBMUFL_RESERVED_RANGE,
)
from sbmufl.domain import contextual_positioning, ison, metadata  # noqa: E402
from sbmufl.framework.checks import (  # noqa: E402
    CheckIterator,
    CheckResult,
    check,
    fail,
    fail_list,
    warn,
    warn_list,
)
from sbmufl.framework.glyphs import GlyphIntrospector, cmap_label  # noqa: E402
from sbmufl.framework.gpos import (  # noqa: E402
    GposIntrospector,
    MarkClassRef,
    format_mark_class,
)
from sbmufl.framework.shaping import Shaper  # noqa: E402

ContextualDeltas = dict[tuple[str, tuple[str, ...]], int]
ContextualRuleCollector = Callable[
    [GposIntrospector, set[str], set[str], str],
    tuple[ContextualDeltas, list[str]],
]
ContextualShapingChecker = Callable[
    [GlyphIntrospector, Shaper, Mapping[tuple[str, tuple[str, ...]], int], int, str],
    list[str],
]


class ContextualFamily(NamedTuple):
    code: str
    label: str
    context_codepoints: set[int]
    primary_codepoints: set[int]
    secondary_codepoints: set[int]
    tertiary_codepoints: set[int] | None = None

    def encoded(self, glyphs: GlyphIntrospector) -> EncodedContextualFamily:
        return EncodedContextualFamily(
            code=self.code,
            label=self.label,
            context_marks=glyphs.encoded_glyph_names(self.context_codepoints),
            primary_context_marks=glyphs.encoded_glyph_names(self.primary_codepoints),
            secondary_context_marks=glyphs.encoded_glyph_names(
                self.secondary_codepoints
            ),
            tertiary_context_marks=(
                None
                if self.tertiary_codepoints is None
                else glyphs.encoded_glyph_names(self.tertiary_codepoints)
            ),
        )


class EncodedContextualFamily(NamedTuple):
    code: str
    label: str
    context_marks: set[str]
    primary_context_marks: set[str]
    secondary_context_marks: set[str]
    tertiary_context_marks: set[str] | None = None

    @property
    def mark_groups(self) -> tuple[set[str], ...]:
        groups = (self.primary_context_marks, self.secondary_context_marks)
        if self.tertiary_context_marks is None:
            return groups
        return (*groups, self.tertiary_context_marks)


def combined_encoded_contextual_family(
    *,
    glyphs: GlyphIntrospector,
    code: str,
    label: str,
    families: tuple[ContextualFamily, ContextualFamily],
) -> EncodedContextualFamily:
    first_family, second_family = (family.encoded(glyphs) for family in families)
    return EncodedContextualFamily(
        code=code,
        label=label,
        context_marks=first_family.context_marks | second_family.context_marks,
        primary_context_marks=first_family.context_marks,
        secondary_context_marks=second_family.context_marks,
    )


GORGON_FAMILY = ContextualFamily(
    code="gorgon",
    label="Gorgon-family",
    context_codepoints=SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS,
    primary_codepoints=SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS,
    secondary_codepoints=set(),
)
FTHORA_FAMILY = ContextualFamily(
    code="fthora",
    label="Fthora/chroa",
    context_codepoints=SBMUFL_FTHORA_ABOVE_CODEPOINTS,
    primary_codepoints=SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS,
    secondary_codepoints=SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS,
    tertiary_codepoints=SBMUFL_FTHORA_TERTIARY_ABOVE_CODEPOINTS,
)
KLASMA_FAMILY = ContextualFamily(
    code="klasma",
    label="Klasma",
    context_codepoints=SBMUFL_KLASMA_ABOVE_CODEPOINTS,
    primary_codepoints=SBMUFL_KLASMA_ABOVE_CODEPOINTS,
    secondary_codepoints=set(),
)


def _check_contextual_mark_family_positioning(
    *,
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
    shaper: Shaper,
    config: Any,
    anchor_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]],
    expected_y_by_name: Mapping[str, int],
    encoded_targets: set[str],
    target_code: str,
    target_label: str,
    target_probe_codepoint: int,
    family: EncodedContextualFamily,
    collect_contextual_deltas: ContextualRuleCollector,
    collect_shaping_problems: ContextualShapingChecker,
    rule_target_label: str,
    shaping_target_label: str,
    expected_context_mark_groups: tuple[set[str], ...] | None = None,
    check_contextual_rules: bool = True,
) -> CheckIterator:
    context_mark_positions = gpos.mark_to_base_mark_anchor_positions(
        family.context_marks,
    )
    missing_context_mark_anchors = sorted(
        family.context_marks - context_mark_positions.keys()
    )
    if missing_context_mark_anchors:
        yield fail_list(
            f"missing-{family.code}-top-mark",
            f"{family.label} marks missing their Mark-to-Base mark anchor:",
            config,
            missing_context_mark_anchors,
        )

    context_ymax_by_name, missing_context_bounds = (
        contextual_positioning.glyph_ymax_by_name(glyphs, family.context_marks)
    )
    if missing_context_bounds:
        yield fail_list(
            f"missing-{family.code}-bounds",
            f"{family.label} marks missing outline bounds:",
            config,
            missing_context_bounds,
        )
        return

    context_mark_classes_by_name, conflicting_context_mark_anchors = (
        contextual_positioning.context_mark_classes_by_name(context_mark_positions)
    )

    if conflicting_context_mark_anchors:
        yield fail_list(
            f"conflicting-{family.code}-top-mark-anchors",
            f"{family.label} marks have conflicting Mark-to-Base mark anchors:",
            config,
            conflicting_context_mark_anchors,
        )

    context_base_positions = gpos.mark_to_base_base_anchor_positions(
        {mark_class for mark_class, _ in context_mark_classes_by_name.values()},
    )
    expected_shaping_deltas = contextual_positioning.expected_contextual_deltas(
        anchor_positions,
        expected_y_by_name,
        context_base_positions,
        context_mark_classes_by_name,
        context_ymax_by_name,
        expected_context_mark_groups or (family.context_marks,),
    )

    if check_contextual_rules:
        actual_contextual_deltas, contextual_delta_problems = collect_contextual_deltas(
            gpos,
            encoded_targets,
            family.context_marks,
            rule_target_label,
        )
        if contextual_delta_problems:
            yield fail_list(
                f"invalid-{target_code}-{family.code}-contextual-positioning",
                f"{target_label.title()} contextual GPOS positioning is malformed "
                f"for {family.label} marks:",
                config,
                sorted(contextual_delta_problems),
            )

        missing_contextual_deltas = [
            f"{base_name} + {' + '.join(context_names)}: "
            f"expected YPlacement +{expected_delta}"
            for (base_name, context_names), expected_delta in sorted(
                expected_shaping_deltas.items()
            )
            if expected_delta
            and actual_contextual_deltas.get((base_name, context_names), 0)
            != expected_delta
        ]
        if missing_contextual_deltas:
            yield fail_list(
                f"missing-{target_code}-{family.code}-contextual-positioning",
                f"Missing contextual GPOS raises for {target_label} above "
                f"{family.label} marks:",
                config,
                missing_contextual_deltas,
            )

        unexpected_contextual_deltas = [
            f"{base_name} + {' + '.join(context_names)}: accumulated YPlacement "
            f"{actual_delta:+d} "
            f"(expected {expected_delta_text})"
            for (base_name, context_names), actual_delta in sorted(
                actual_contextual_deltas.items()
            )
            if (base_name, context_names) in expected_shaping_deltas
            for expected_delta in [
                expected_shaping_deltas.get((base_name, context_names), 0)
            ]
            for expected_delta_text in [
                "none" if expected_delta == 0 else f"+{expected_delta}"
            ]
            if actual_delta != expected_delta
        ]
        if unexpected_contextual_deltas:
            yield fail_list(
                f"inconsistent-{target_code}-{family.code}-contextual-positioning",
                f"{target_label.title()} contextual GPOS raises do not match the dynamic "
                f"{family.label} clearance formula:",
                config,
                unexpected_contextual_deltas,
            )

    shaping_problems = collect_shaping_problems(
        glyphs,
        shaper,
        expected_shaping_deltas,
        target_probe_codepoint,
        shaping_target_label,
    )
    if shaping_problems:
        yield fail_list(
            f"inconsistent-{target_code}-{family.code}-contextual-shaping",
            f"HarfBuzz shaping does not preserve {target_label} X and apply the expected "
            f"{family.label} Y raise:",
            config,
            shaping_problems,
        )


def _check_target_last_contextual_mark_family_positioning(
    *,
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
    shaper: Shaper,
    config: Any,
    anchor_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]],
    expected_y_by_name: Mapping[str, int],
    encoded_targets: set[str],
    target_code: str,
    target_label: str,
    target_probe_codepoint: int,
    family: EncodedContextualFamily,
    expected_context_mark_groups: tuple[set[str], ...] | None = None,
    check_contextual_rules: bool = True,
) -> CheckIterator:
    yield from _check_contextual_mark_family_positioning(
        glyphs=glyphs,
        gpos=gpos,
        shaper=shaper,
        config=config,
        anchor_positions=anchor_positions,
        expected_y_by_name=expected_y_by_name,
        encoded_targets=encoded_targets,
        target_code=target_code,
        target_label=target_label,
        target_probe_codepoint=target_probe_codepoint,
        family=family,
        collect_contextual_deltas=contextual_positioning.contextual_ison_raise_rules,
        collect_shaping_problems=contextual_positioning.contextual_shaping_problems,
        rule_target_label=target_label,
        shaping_target_label=f"{target_label} over {family.code}",
        expected_context_mark_groups=expected_context_mark_groups,
        check_contextual_rules=check_contextual_rules,
    )


def _check_target_first_contextual_mark_family_positioning(
    *,
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
    shaper: Shaper,
    config: Any,
    anchor_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]],
    expected_y_by_name: Mapping[str, int],
    encoded_targets: set[str],
    target_code: str,
    target_label: str,
    target_probe_codepoint: int,
    family: EncodedContextualFamily,
    expected_context_mark_groups: tuple[set[str], ...] | None = None,
    check_contextual_rules: bool = True,
) -> CheckIterator:
    yield from _check_contextual_mark_family_positioning(
        glyphs=glyphs,
        gpos=gpos,
        shaper=shaper,
        config=config,
        anchor_positions=anchor_positions,
        expected_y_by_name=expected_y_by_name,
        encoded_targets=encoded_targets,
        target_code=target_code,
        target_label=target_label,
        target_probe_codepoint=target_probe_codepoint,
        family=family,
        collect_contextual_deltas=(
            contextual_positioning.contextual_target_first_raise_rules
        ),
        collect_shaping_problems=(
            contextual_positioning.target_first_contextual_shaping_problems
        ),
        rule_target_label=f"{target_label} marks",
        shaping_target_label=target_label,
        expected_context_mark_groups=expected_context_mark_groups,
        check_contextual_rules=check_contextual_rules,
    )


class ContextualTargetAnchors(NamedTuple):
    encoded_targets: set[str]
    anchor_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]]
    expected_y_by_name: Mapping[str, int]


class ContextualTargetAnchorSpec(NamedTuple):
    codepoints: set[int]
    missing_target_code: str
    missing_target_message: str
    missing_mark_class_code: str
    missing_mark_class_message: str
    missing_mark_anchor_code: str
    missing_mark_anchor_message: str
    missing_base_anchor_code: str
    missing_base_anchor_message: str
    conflicting_base_anchor_code: str
    conflicting_base_anchor_message: str


FTHORA_TARGET_ANCHORS = ContextualTargetAnchorSpec(
    codepoints=SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS,
    missing_target_code="missing-fthora",
    missing_target_message="Font does not encode any primary fthora/chroa above marks.",
    missing_mark_class_code="missing-fthora-mark-class",
    missing_mark_class_message=(
        "Primary fthora/chroa marks are not covered by GPOS Mark-to-Base attachment."
    ),
    missing_mark_anchor_code="missing-fthora-mark-anchor",
    missing_mark_anchor_message=(
        "Primary fthora/chroa glyphs missing their Mark-to-Base mark anchor:"
    ),
    missing_base_anchor_code="missing-fthora-base-anchors",
    missing_base_anchor_message=(
        "No base glyphs have GPOS base anchors for primary fthora/chroa marks."
    ),
    conflicting_base_anchor_code="conflicting-fthora-base-anchors",
    conflicting_base_anchor_message=(
        "Primary fthora/chroa base glyphs have conflicting vertical anchors:"
    ),
)
KORONIS_TARGET_ANCHORS = ContextualTargetAnchorSpec(
    codepoints=SBMUFL_KORONIS_CODEPOINTS,
    missing_target_code="missing-koronis",
    missing_target_message="Font does not encode the koronis mark.",
    missing_mark_class_code="missing-koronis-mark-class",
    missing_mark_class_message="Koronis is not covered by GPOS Mark-to-Base attachment.",
    missing_mark_anchor_code="missing-koronis-mark-anchor",
    missing_mark_anchor_message="Koronis glyphs missing their Mark-to-Base mark anchor:",
    missing_base_anchor_code="missing-koronis-base-anchors",
    missing_base_anchor_message="No base glyphs have GPOS base anchors for koronis marks.",
    conflicting_base_anchor_code="conflicting-koronis-base-anchors",
    conflicting_base_anchor_message="Koronis base glyphs have conflicting vertical anchors:",
)


def _contextual_target_anchors(
    *,
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
    config: Any,
    spec: ContextualTargetAnchorSpec,
) -> tuple[ContextualTargetAnchors | None, list[CheckResult]]:
    results: list[CheckResult] = []
    encoded_targets = glyphs.encoded_glyph_names(spec.codepoints)
    if not encoded_targets:
        results.append(fail(spec.missing_target_code, spec.missing_target_message))
        return None, results

    anchors = gpos.mark_attachment_anchors(encoded_targets)
    if not anchors.mark_classes:
        results.append(
            fail(spec.missing_mark_class_code, spec.missing_mark_class_message)
        )
        return None, results

    if anchors.missing_mark_anchors:
        results.append(
            fail_list(
                spec.missing_mark_anchor_code,
                spec.missing_mark_anchor_message,
                config,
                anchors.missing_mark_anchors,
            )
        )
        return None, results

    if not anchors.base_anchor_positions:
        results.append(
            fail(spec.missing_base_anchor_code, spec.missing_base_anchor_message)
        )
        return None, results

    if anchors.conflicting_base_anchors:
        results.append(
            fail_list(
                spec.conflicting_base_anchor_code,
                spec.conflicting_base_anchor_message,
                config,
                anchors.conflicting_base_anchors,
            )
        )
        return None, results

    return (
        ContextualTargetAnchors(
            encoded_targets,
            anchors.base_anchor_positions,
            anchors.base_anchor_y_by_name,
        ),
        results,
    )


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
def check_sbmufl_glyph_coverage(ttFont: Any, config: Any) -> CheckIterator:
    """Check that the font covers required and optional SBMuFL glyphs."""
    glyphs = GlyphIntrospector(ttFont)
    cmap = glyphs.cmap
    glyph_order = glyphs.glyph_names
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
        for codepoint, glyph_name in glyphs.all_cmap_items
        if glyph_name in SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME
        and codepoint != SBMUFL_OPTIONAL_CODEPOINTS_BY_NAME[glyph_name]
    ]

    inconsistent_optional_names = [
        f"U+{codepoint:04X} {glyph_name} (expected {SBMUFL_OPTIONAL_GLYPHS[codepoint]})"
        for codepoint, glyph_name in glyphs.all_cmap_items
        if codepoint in SBMUFL_OPTIONAL_GLYPHS
        and glyph_name != SBMUFL_OPTIONAL_GLYPHS[codepoint]
    ]

    if missing:
        missing_glyphs = [
            f"U+{codepoint:04X} {SBMUFL_REQUIRED_GLYPHS[codepoint]}"
            for codepoint in missing
        ]
        yield fail_list(
            "missing-codepoints",
            "Missing required SBMuFL codepoints:",
            config,
            missing_glyphs,
        )

    if missing_glyph_names:
        yield warn_list(
            "missing-glyphs",
            "Missing required SBMuFL glyphs:",
            config,
            missing_glyph_names,
        )

    if inconsistent_names:
        yield warn_list(
            "inconsistent-glyph-names",
            "Required SBMuFL codepoints mapped to inconsistent glyph names:",
            config,
            inconsistent_names,
        )

    if missing_optional:
        yield warn_list(
            "missing-optional-glyphs",
            "Missing optional SBMuFL glyphs:",
            config,
            missing_optional,
        )

    if misplaced_optional:
        yield fail_list(
            "optional-glyphs-wrong-codepoint",
            "Optional glyphs encoded at non-standard SBMuFL codepoints:",
            config,
            misplaced_optional,
        )

    if inconsistent_optional_names:
        yield warn_list(
            "optional-glyph-name-inconsistency",
            "SBMuFL optional codepoints mapped to inconsistent glyph names:",
            config,
            inconsistent_optional_names,
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
def check_sbmufl_reserved_codepoints(ttFont: Any, config: Any) -> CheckIterator:
    """Check that no glyphs are encoded in the reserved SBMuFL range."""
    glyphs = GlyphIntrospector(ttFont)
    reserved = [
        f"U+{codepoint:04X} {glyph_name}"
        for codepoint, glyph_name in glyphs.all_cmap_items
        if codepoint in SBMUFL_RESERVED_RANGE
    ]

    if reserved:
        yield fail_list(
            "reserved-codepoints",
            "Glyphs encoded in the SBMuFL reserved range:",
            config,
            reserved,
        )


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
def check_sbmufl_mark_positioning(ttFont: Any) -> CheckIterator:
    """Check that the font has SBMuFL-required GPOS mark positioning lookups."""
    gpos = GposIntrospector(ttFont)
    lookup_types = gpos.lookup_types()

    if otTables.MarkBasePos.LookupType not in lookup_types:
        yield fail(
            "missing-mark-to-base-lookup",
            "Missing GPOS Lookup Type 4: Mark-to-Base Attachment",
        )

    if otTables.MarkMarkPos.LookupType not in lookup_types:
        yield warn(
            "missing-mark-to-mark-lookup",
            "Missing GPOS Lookup Type 6: Mark-to-Mark Attachment",
        )


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
def check_sbmufl_mark_attachment(ttFont: Any, config: Any) -> CheckIterator:
    """Check that SBMuFL mark codepoints are mark-classed and attached in GPOS."""
    glyphs = GlyphIntrospector(ttFont)
    gpos = GposIntrospector(ttFont)
    cmap = glyphs.cmap
    glyph_classes = glyphs.gdef_classes
    mark_to_base_glyphs, mark_to_mark_glyphs = gpos.mark_coverages()

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
        label = cmap_label(codepoint, expected_glyph_name, glyph_name)
        if glyph_classes.get(glyph_name) != 3:
            missing_gdef.append(label)
        if glyph_name not in mark_to_base_glyphs:
            missing_mark_to_base.append(label)

    for codepoint in encoded_mark_to_mark_codepoints:
        glyph_name = cmap[codepoint]

        if glyph_name not in mark_to_mark_glyphs:
            expected_glyph_name = SBMUFL_NAMELIST_GLYPHS[codepoint]
            label = cmap_label(codepoint, expected_glyph_name, glyph_name)
            missing_mark_to_mark.append(label)

    if missing_gdef:
        yield fail_list(
            "not-gdef-mark",
            "SBMuFL mark codepoints not classified as marks in GDEF:",
            config,
            missing_gdef,
        )

    if missing_mark_to_base:
        yield fail_list(
            "not-mark-to-base",
            "SBMuFL mark codepoints not covered by GPOS Mark-to-Base attachment:",
            config,
            missing_mark_to_base,
        )

    if missing_mark_to_mark:
        yield warn_list(
            "not-mark-to-mark",
            "SBMuFL mark codepoints not covered by GPOS Mark-to-Mark attachment:",
            config,
            missing_mark_to_mark,
        )


@check(
    id="sbmufl/contextual_subtable_count",
    rationale="""
        Collision handling should be encoded as generated contextual
        positioning lookups for fthora/chroa marks, ison indicators, and
        koronis. Each lookup should remain below its target entry budget.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_contextual_subtable_count(
    ttFont: Any,
) -> CheckIterator:
    """Check that generated contextual positioning stays compact."""
    gpos = GposIntrospector(ttFont)
    counts_by_lookup = gpos.chain_context_pos_subtable_counts_by_lookup({2})
    lookup_counts = sorted(counts_by_lookup.items())
    expected_limits = tuple(SBMUFL_CONTEXTUAL_SUBTABLE_LIMITS)
    expected_labels = tuple(label for label, _limit in expected_limits)

    counts_by_label = dict(
        zip(
            expected_labels,
            (count for _lookup_index, count in lookup_counts),
            strict=False,
        )
    )
    if len(lookup_counts) != len(expected_limits):
        counts_by_label = {
            f"lookup {lookup_index}": count for lookup_index, count in lookup_counts
        }

    lookup_count = len(lookup_counts)
    if lookup_count != SBMUFL_CONTEXTUAL_LOOKUP_COUNT:
        details = ", ".join(
            f"{label}: {count}" for label, count in sorted(counts_by_label.items())
        )
        yield fail(
            "contextual-lookup-count",
            "Generated additive contextual positioning uses "
            f"{lookup_count} Format 2 contextual GPOS lookups; expected "
            f"{SBMUFL_CONTEXTUAL_LOOKUP_COUNT}."
            f"{f' Breakdown: {details}.' if details else ''}",
        )

    oversized_counts = {
        f"{label} lookup {lookup_index}": (count, limit)
        for (lookup_index, count), (label, limit) in zip(
            lookup_counts,
            expected_limits,
            strict=False,
        )
        if count >= limit
    }
    if oversized_counts:
        details = ", ".join(
            f"{label}: {count} >= {limit}"
            for label, (count, limit) in sorted(oversized_counts.items())
        )
        yield fail(
            "contextual-subtable-count-too-large",
            "Generated additive contextual positioning exceeds the contextual GPOS "
            f"entry budget. {details}.",
        )


@check(
    id="sbmufl/contextual_prompt_probe_cases",
    rationale="""
        The generated contextual positioning should cover the concrete stacking
        combinations used by applications: fthora plus ison, gorgon-family plus
        ison, klasma or gorgon-family plus fthora, and the dependent stacks
        where ison or koronis must clear a primary fthora/chroa mark that was
        itself raised by klasma or gorgon-family positioning.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_contextual_prompt_probe_cases(
    ttFont: Any, config: Any
) -> CheckIterator:
    """Check the concrete contextual stacking probe cases."""
    glyphs = GlyphIntrospector(ttFont)
    shaper = Shaper.from_ttfont(ttFont)
    problems = contextual_positioning.contextual_prompt_probe_problems(glyphs, shaper)
    if problems:
        yield fail_list(
            "contextual-prompt-probe-cases",
            "Contextual positioning failed concrete stacking probe cases:",
            config,
            problems,
        )


@check(
    id="sbmufl/ison_contextual_positioning",
    rationale="""
        Ison indicator glyphs are marks that attach above neumes. To keep the
        selected ison pitch from changing the visual height of the notation,
        base glyphs that accept an ison indicator should place that mark at the
        ison glyph's vertical position unless that would collide with the base
        glyph outline. Gorgon-family marks are handled dynamically with a
        contextual GPOS raise on the ison indicator, preserving the base
        glyph's isonIndicator X anchor while clearing the actual gorgon,
        digorgon, trigorgon, fthora, or chroa mark present in the shaped
        sequence.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_ison_contextual_positioning(ttFont: Any, config: Any) -> CheckIterator:
    """Check that ison indicators attach at a consistent vertical position."""
    glyphs = GlyphIntrospector(ttFont)
    gpos = GposIntrospector(ttFont)
    encoded_ison_indicators = glyphs.encoded_glyph_names(
        SBMUFL_ISON_INDICATOR_CODEPOINTS
    )
    if not encoded_ison_indicators:
        yield fail(
            "missing-ison-indicators",
            "Font does not encode any ison indicator marks.",
        )
        return

    anchors = gpos.mark_attachment_anchors(encoded_ison_indicators)
    if not anchors.mark_classes:
        yield fail(
            "missing-ison-mark-class",
            "Ison indicator marks are not covered by GPOS Mark-to-Base attachment.",
        )
        return

    if anchors.missing_mark_anchors:
        yield fail_list(
            "missing-ison-mark-anchor",
            "Ison indicator glyphs missing their Mark-to-Base mark anchor:",
            config,
            anchors.missing_mark_anchors,
        )
        return

    anchor_positions = anchors.base_anchor_positions
    reference_positions = anchor_positions.get("ison", set())
    if not reference_positions:
        yield fail(
            "missing-ison-base-anchor",
            "The ison glyph is missing a GPOS base anchor for ison indicator marks.",
        )
        return

    reference_y_positions = {y for _, _, y in reference_positions}
    if len(reference_y_positions) > 1:
        formatted_positions = [
            f"{format_mark_class(mark_class)}, X={x}, Y={y}"
            for mark_class, x, y in sorted(reference_positions)
        ]
        yield fail_list(
            "conflicting-ison-base-anchors",
            "The ison glyph has conflicting GPOS base anchors for ison "
            "indicator marks:",
            config,
            formatted_positions,
        )
        return

    if anchors.conflicting_base_anchors:
        yield fail_list(
            "conflicting-ison-mark-vertical-position",
            "Ison indicator base anchors have conflicting vertical positions:",
            config,
            anchors.conflicting_base_anchors,
        )
        return

    reference_y = next(iter(reference_y_positions))
    glyph_ymax_by_name, missing_bounds = contextual_positioning.glyph_ymax_by_name(
        glyphs, set(anchor_positions)
    )

    if missing_bounds:
        yield fail_list(
            "missing-ison-base-bounds",
            "Ison indicator base glyphs missing outline bounds:",
            config,
            missing_bounds,
        )
        return

    compromise_glyph_names = glyphs.encoded_glyph_names(
        set(SBMUFL_ISON_INDICATOR_COMPROMISE_CODEPOINTS)
    )
    expected_y_by_name = ison.expected_base_y_by_name(
        reference_y,
        glyph_ymax_by_name,
        compromise_glyph_names,
    )

    shaper = Shaper.from_ttfont(ttFont)
    for family in (GORGON_FAMILY, KLASMA_FAMILY, FTHORA_FAMILY):
        yield from _check_target_last_contextual_mark_family_positioning(
            glyphs=glyphs,
            gpos=gpos,
            shaper=shaper,
            config=config,
            anchor_positions=anchor_positions,
            expected_y_by_name=expected_y_by_name,
            encoded_targets=encoded_ison_indicators,
            target_code="ison",
            target_label="ison indicators",
            target_probe_codepoint=SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
            family=family.encoded(glyphs),
        )

    klasma_gorgon_family = combined_encoded_contextual_family(
        glyphs=glyphs,
        code="klasma-gorgon",
        label="Klasma and gorgon-family",
        families=(KLASMA_FAMILY, GORGON_FAMILY),
    )
    yield from _check_target_last_contextual_mark_family_positioning(
        glyphs=glyphs,
        gpos=gpos,
        shaper=shaper,
        config=config,
        anchor_positions=anchor_positions,
        expected_y_by_name=expected_y_by_name,
        encoded_targets=encoded_ison_indicators,
        target_code="ison",
        target_label="ison indicators",
        target_probe_codepoint=SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        family=klasma_gorgon_family,
        expected_context_mark_groups=klasma_gorgon_family.mark_groups,
        check_contextual_rules=False,
    )


@check(
    id="sbmufl/fthora_contextual_positioning",
    rationale="""
        Primary fthora/chroa marks may stack above temporal marks and
        gorgon-family marks. Generated contextual GPOS raises should lift only
        the fthora/chroa mark while preserving its base X anchor and clearing
        the actual contextual mark present in the shaped sequence.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_fthora_contextual_positioning(
    ttFont: Any, config: Any
) -> CheckIterator:
    """Check that fthora contextual raises match dynamic mark clearance."""
    glyphs = GlyphIntrospector(ttFont)
    gpos = GposIntrospector(ttFont)
    target, target_results = _contextual_target_anchors(
        glyphs=glyphs,
        gpos=gpos,
        config=config,
        spec=FTHORA_TARGET_ANCHORS,
    )
    yield from target_results
    if target is None:
        return

    shaper = Shaper.from_ttfont(ttFont)
    for family in (KLASMA_FAMILY, GORGON_FAMILY):
        yield from _check_target_last_contextual_mark_family_positioning(
            glyphs=glyphs,
            gpos=gpos,
            shaper=shaper,
            config=config,
            anchor_positions=target.anchor_positions,
            expected_y_by_name=target.expected_y_by_name,
            encoded_targets=target.encoded_targets,
            target_code="fthora",
            target_label="fthora/chroa",
            target_probe_codepoint=SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
            family=family.encoded(glyphs),
        )

    klasma_gorgon_family = combined_encoded_contextual_family(
        glyphs=glyphs,
        code="klasma-gorgon",
        label="Klasma and gorgon-family",
        families=(KLASMA_FAMILY, GORGON_FAMILY),
    )
    yield from _check_target_last_contextual_mark_family_positioning(
        glyphs=glyphs,
        gpos=gpos,
        shaper=shaper,
        config=config,
        anchor_positions=target.anchor_positions,
        expected_y_by_name=target.expected_y_by_name,
        encoded_targets=target.encoded_targets,
        target_code="fthora",
        target_label="fthora/chroa",
        target_probe_codepoint=SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        family=klasma_gorgon_family,
        expected_context_mark_groups=klasma_gorgon_family.mark_groups,
        check_contextual_rules=False,
    )


@check(
    id="sbmufl/koronis_contextual_positioning",
    rationale="""
        Koronis is a mark that may stack above klasma, gorgon-family, and
        fthora/chroa marks. Generated
        contextual GPOS raises should lift only the koronis mark while preserving
        its base X anchor and clearing the actual contextual mark present in the
        shaped sequence.
    """,
    proposal="https://github.com/neanes/sbmufl",
)
def check_sbmufl_koronis_contextual_positioning(
    ttFont: Any, config: Any
) -> CheckIterator:
    """Check that koronis contextual raises match dynamic mark clearance."""
    glyphs = GlyphIntrospector(ttFont)
    gpos = GposIntrospector(ttFont)
    target, target_results = _contextual_target_anchors(
        glyphs=glyphs,
        gpos=gpos,
        config=config,
        spec=KORONIS_TARGET_ANCHORS,
    )
    yield from target_results
    if target is None:
        return

    shaper = Shaper.from_ttfont(ttFont)
    yield from _check_target_last_contextual_mark_family_positioning(
        glyphs=glyphs,
        gpos=gpos,
        shaper=shaper,
        config=config,
        anchor_positions=target.anchor_positions,
        expected_y_by_name=target.expected_y_by_name,
        encoded_targets=target.encoded_targets,
        target_code="koronis",
        target_label="koronis",
        target_probe_codepoint=SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
        family=KLASMA_FAMILY.encoded(glyphs),
    )

    for family in (GORGON_FAMILY, FTHORA_FAMILY):
        encoded_family = family.encoded(glyphs)
        if family == FTHORA_FAMILY:
            encoded_family = encoded_family._replace(
                context_marks=encoded_family.primary_context_marks
            )
        yield from _check_target_first_contextual_mark_family_positioning(
            glyphs=glyphs,
            gpos=gpos,
            shaper=shaper,
            config=config,
            anchor_positions=target.anchor_positions,
            expected_y_by_name=target.expected_y_by_name,
            encoded_targets=target.encoded_targets,
            target_code="koronis",
            target_label="koronis",
            target_probe_codepoint=SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
            family=encoded_family,
        )


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
) -> CheckIterator:
    """Check that SBMuFL repository metadata files are complete and in sync."""
    problems = metadata.repository_metadata_problems()

    if problems:
        yield fail_list(
            "inconsistent-repository-metadata",
            "SBMuFL repository metadata is incomplete or inconsistent:",
            config,
            problems,
        )
