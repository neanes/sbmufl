"""Bake generated anchor and contextual mark positioning into SFDs.

This script intentionally mutates the checked-in FontForge sources. It is a
source-regeneration step to run when anchor or contextual positioning rules
change, not a normal build step.

Usage:
    fontforge -script scripts/generate-contextual-positioning.py
    cd scripts
    ./build.sh

Commit the regenerated sources and build artifacts together.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Final, Iterable, TypeAlias

import fontforge  # type: ignore[import-not-found]

Anchor: TypeAlias = tuple[int, int]
AxisDeltas: TypeAlias = dict[str, dict[str, dict[str, int]]]
ContextMarksByAxis: TypeAlias = dict[str, dict[str, Anchor]]
DeltaBuckets: TypeAlias = defaultdict[int, set[str]]
DeltaBucketsByAxis: TypeAlias = dict[str, DeltaBuckets]
MarkSlot: TypeAlias = tuple[str, frozenset[str]]
RaiseRuleKey: TypeAlias = tuple[tuple[MarkSlot, ...], int]
ContextRules: TypeAlias = defaultdict[RaiseRuleKey, set[str]]

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
SOURCES_DIR: Final = REPO_ROOT / "sources"

BASE_ANCHOR_KIND: Final = "base"
MARK_ANCHOR_KIND: Final = "mark"
MARK_LOOKUP: Final = "'mark' Mark Positioning lookup 0"
MARK_FEATURES: Final[tuple[Any, ...]] = (
    (
        "mark",
        (
            ("DFLT", ("dflt")),
            ("byzm", ("dflt")),
            ("latn", ("dflt")),
        ),
    ),
)
MODIFICATION_TIME_PREFIX: Final = "ModificationTime: "

GENERATED_RAISE_LOOKUP_PREFIX: Final = "contextualRaise"
GENERATED_CONTEXT_LOOKUP_PREFIX: Final = "contextualRaiseContext"
GENERATED_CONTEXT_MARK_CLASS: Final = "contextualRaiseMarks"

ISON_ANCHOR: Final = "isonIndicator"
ISON_OBSOLETE_ABOVE_MARK_ANCHOR: Final = "isonIndicatorAboveMark"
KORONIS_ANCHOR: Final = "koronis"
KLASMA_TOP_ANCHOR: Final = "klasmaTop"
GORGON_TOP_ANCHOR: Final = "gorgonTop"
GORGON_SECONDARY_ANCHOR: Final = "gorgonSecondary"
FTHORA_TOP_ANCHOR: Final = "fthoraTop"
FTHORA_SECONDARY_ANCHOR: Final = "fthoraTopSecondary"
FTHORA_TERTIARY_ANCHOR: Final = "fthoraTopTertiary"

STACK_CLEARANCE: Final = 120
CONTEXTUAL_RAISE_GRID: Final = 20
PRIMARY_RAISE_STAGE: Final = "primary"
SECONDARY_RAISE_STAGE: Final = "secondary"
TERTIARY_RAISE_STAGE: Final = "tertiary"
KLASMA_RAISE_STAGE: Final = "klasma"
GORGON_PRIMARY_RAISE_STAGE: Final = f"gorgon_{PRIMARY_RAISE_STAGE}"
GORGON_SECONDARY_RAISE_STAGE: Final = f"gorgon_{SECONDARY_RAISE_STAGE}"
FTHORA_PRIMARY_RAISE_STAGE: Final = f"fthora_{PRIMARY_RAISE_STAGE}"
FTHORA_SECONDARY_RAISE_STAGE: Final = f"fthora_{SECONDARY_RAISE_STAGE}"
FTHORA_TERTIARY_RAISE_STAGE: Final = f"fthora_{TERTIARY_RAISE_STAGE}"

ISON_INDICATOR_CODEPOINTS: Final = tuple(range(0xE260, 0xE26B))
KORONIS_CODEPOINTS: Final = (0xE0D6,)  # U+E0D6 koronis
KLASMA_ABOVE_CODEPOINTS: Final = (0xE0D0,)  # U+E0D0 klasmaAbove
GORGON_ABOVE_CODEPOINTS: Final = (
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
)
GORGON_SECONDARY_ABOVE_CODEPOINTS: Final = (
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
)
FTHORA_ABOVE_CODEPOINTS: Final = (
    0xE190,  # U+E190 fthoraDiatonicNiLowAbove
    0xE191,  # U+E191 fthoraDiatonicPaAbove
    0xE192,  # U+E192 fthoraDiatonicVouAbove
    0xE193,  # U+E193 fthoraDiatonicGaAbove
    0xE194,  # U+E194 fthoraDiatonicDiAbove
    0xE195,  # U+E195 fthoraDiatonicKeAbove
    0xE196,  # U+E196 fthoraDiatonicZoAbove
    0xE197,  # U+E197 fthoraDiatonicNiHighAbove
    0xE198,  # U+E198 fthoraHardChromaticPaAbove
    0xE199,  # U+E199 fthoraHardChromaticDiAbove
    0xE19A,  # U+E19A fthoraSoftChromaticDiAbove
    0xE19B,  # U+E19B fthoraSoftChromaticKeAbove
    0xE19C,  # U+E19C fthoraEnharmonicAbove
    0xE19D,  # U+E19D chroaZygosAbove
    0xE19E,  # U+E19E chroaKlitonAbove
    0xE19F,  # U+E19F chroaSpathiAbove
)
FTHORA_SECONDARY_ABOVE_CODEPOINTS: Final = (
    0xE1A0,  # U+E1A0 fthoraDiatonicNiLowSecondary
    0xE1A1,  # U+E1A1 fthoraDiatonicPaSecondary
    0xE1A2,  # U+E1A2 fthoraDiatonicVouSecondary
    0xE1A3,  # U+E1A3 fthoraDiatonicGaSecondary
    0xE1A4,  # U+E1A4 fthoraDiatonicDiSecondary
    0xE1A5,  # U+E1A5 fthoraDiatonicKeSecondary
    0xE1A6,  # U+E1A6 fthoraDiatonicZoSecondary
    0xE1A7,  # U+E1A7 fthoraDiatonicNiHighSecondary
    0xE1A8,  # U+E1A8 fthoraHardChromaticPaSecondary
    0xE1A9,  # U+E1A9 fthoraHardChromaticDiSecondary
    0xE1AA,  # U+E1AA fthoraSoftChromaticDiSecondary
    0xE1AB,  # U+E1AB fthoraSoftChromaticKeSecondary
    0xE1AC,  # U+E1AC fthoraEnharmonicSecondary
    0xE1AD,  # U+E1AD chroaZygosSecondary
    0xE1AE,  # U+E1AE chroaKlitonSecondary
    0xE1AF,  # U+E1AF chroaSpathiSecondary
)
FTHORA_TERTIARY_ABOVE_CODEPOINTS: Final = (
    0xE1B0,  # U+E1B0 fthoraDiatonicNiLowTertiary
    0xE1B1,  # U+E1B1 fthoraDiatonicPaTertiary
    0xE1B2,  # U+E1B2 fthoraDiatonicVouTertiary
    0xE1B3,  # U+E1B3 fthoraDiatonicGaTertiary
    0xE1B4,  # U+E1B4 fthoraDiatonicDiTertiary
    0xE1B5,  # U+E1B5 fthoraDiatonicKeTertiary
    0xE1B6,  # U+E1B6 fthoraDiatonicZoTertiary
    0xE1B7,  # U+E1B7 fthoraDiatonicNiHighTertiary
    0xE1B8,  # U+E1B8 fthoraHardChromaticPaTertiary
    0xE1B9,  # U+E1B9 fthoraHardChromaticDiTertiary
    0xE1BA,  # U+E1BA fthoraSoftChromaticDiTertiary
    0xE1BB,  # U+E1BB fthoraSoftChromaticKeTertiary
    0xE1BC,  # U+E1BC fthoraEnharmonicTertiary
    0xE1BD,  # U+E1BD chroaZygosTertiary
    0xE1BE,  # U+E1BE chroaKlitonTertiary
    0xE1BF,  # U+E1BF chroaSpathiTertiary
)

ISON_COMPROMISE_CODEPOINTS: Final = {
    0xE005,  # U+E005 oligonYpsiliRight
    0xE006,  # U+E006 oligonYpsiliLeft
    0xE007,  # U+E007 oligonKentimaYpsiliRight
    0xE044,  # U+E044 petastiYpsiliRight
    0xE046,  # U+E046 petastiKentimaYpsiliRight
    0xE086,  # U+E086 oligonYpsiliRightKentimata
    0xE087,  # U+E087 oligonYpsiliLeftKentimata
}


@dataclass(frozen=True)
class BaseAnchorRule:
    anchor_name: str
    reference_glyph_name: str
    clearance: int
    compromise_codepoints: frozenset[int] = frozenset()
    obsolete_anchor_classes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextAxis:
    name: str
    anchor_name: str
    codepoints: tuple[int, ...]
    order: int
    contributes_to_raise: bool = True


@dataclass(frozen=True)
class ContextualRaiseRelation:
    name: str
    target_anchor: str
    target_codepoints: tuple[int, ...]
    axes: tuple[ContextAxis, ...]
    clearance: int
    grid: int
    target_order: int
    mark_class: str = GENERATED_CONTEXT_MARK_CLASS
    features: tuple[Any, ...] = MARK_FEATURES

    @property
    def lookup_prefix(self) -> str:
        return f"{GENERATED_RAISE_LOOKUP_PREFIX}_{self.name}"

    @property
    def context_lookup_prefix(self) -> str:
        return f"{GENERATED_CONTEXT_LOOKUP_PREFIX}_{self.name}"

    @property
    def axis_names(self) -> tuple[str, ...]:
        return tuple(axis.name for axis in self.axes)


@dataclass(frozen=True)
class ActiveContextualRaiseRelation:
    relation: ContextualRaiseRelation
    target_names: list[str]
    marks_by_axis: ContextMarksByAxis


def pass_through_axis(axis: ContextAxis) -> ContextAxis:
    return ContextAxis(
        axis.name,
        axis.anchor_name,
        axis.codepoints,
        axis.order,
        contributes_to_raise=False,
    )


ISON_BASE_ANCHOR_RULE = BaseAnchorRule(
    anchor_name=ISON_ANCHOR,
    reference_glyph_name="ison",
    clearance=STACK_CLEARANCE,
    compromise_codepoints=frozenset(ISON_COMPROMISE_CODEPOINTS),
    obsolete_anchor_classes=(ISON_OBSOLETE_ABOVE_MARK_ANCHOR,),
)

TEMPORAL_AXES = (
    ContextAxis(
        KLASMA_RAISE_STAGE,
        KLASMA_TOP_ANCHOR,
        KLASMA_ABOVE_CODEPOINTS,
        6,
    ),
)
KORONIS_AXIS = ContextAxis(
    "koronis",
    KORONIS_ANCHOR,
    KORONIS_CODEPOINTS,
    7,
    contributes_to_raise=False,
)
GORGON_AXES = (
    ContextAxis(
        GORGON_PRIMARY_RAISE_STAGE,
        GORGON_TOP_ANCHOR,
        GORGON_ABOVE_CODEPOINTS,
        8,
    ),
    ContextAxis(
        GORGON_SECONDARY_RAISE_STAGE,
        GORGON_SECONDARY_ANCHOR,
        GORGON_SECONDARY_ABOVE_CODEPOINTS,
        9,
    ),
)
FTHORA_AXES = (
    ContextAxis(
        FTHORA_PRIMARY_RAISE_STAGE,
        FTHORA_TOP_ANCHOR,
        FTHORA_ABOVE_CODEPOINTS,
        10,
    ),
    ContextAxis(
        FTHORA_SECONDARY_RAISE_STAGE,
        FTHORA_SECONDARY_ANCHOR,
        FTHORA_SECONDARY_ABOVE_CODEPOINTS,
        11,
    ),
    ContextAxis(
        FTHORA_TERTIARY_RAISE_STAGE,
        FTHORA_TERTIARY_ANCHOR,
        FTHORA_TERTIARY_ABOVE_CODEPOINTS,
        12,
    ),
)
TARGET_CONTEXT_AXES = (
    TEMPORAL_AXES[0],
    GORGON_AXES[0],
    pass_through_axis(GORGON_AXES[1]),
    *FTHORA_AXES,
)
FTHORA_PRIMARY_CONTEXT_AXES = (
    TEMPORAL_AXES[0],
    KORONIS_AXIS,
    GORGON_AXES[0],
    pass_through_axis(GORGON_AXES[1]),
)
FTHORA_SECONDARY_CONTEXT_AXES = (
    KORONIS_AXIS,
    pass_through_axis(GORGON_AXES[0]),
    GORGON_AXES[1],
    pass_through_axis(FTHORA_AXES[0]),
)
FTHORA_TARGET_STAGE_BY_RELATION_NAME = {
    "fthora": FTHORA_PRIMARY_RAISE_STAGE,
    "fthoraSecondary": FTHORA_SECONDARY_RAISE_STAGE,
}

CONTEXTUAL_RAISE_RELATIONS = (
    ContextualRaiseRelation(
        name="fthora",
        target_anchor=FTHORA_TOP_ANCHOR,
        target_codepoints=FTHORA_ABOVE_CODEPOINTS,
        axes=FTHORA_PRIMARY_CONTEXT_AXES,
        clearance=STACK_CLEARANCE,
        grid=CONTEXTUAL_RAISE_GRID,
        target_order=10,
    ),
    ContextualRaiseRelation(
        name="fthoraSecondary",
        target_anchor=FTHORA_SECONDARY_ANCHOR,
        target_codepoints=FTHORA_SECONDARY_ABOVE_CODEPOINTS,
        axes=FTHORA_SECONDARY_CONTEXT_AXES,
        clearance=STACK_CLEARANCE,
        grid=CONTEXTUAL_RAISE_GRID,
        target_order=11,
    ),
    ContextualRaiseRelation(
        name="ison",
        target_anchor=ISON_ANCHOR,
        target_codepoints=ISON_INDICATOR_CODEPOINTS,
        axes=TARGET_CONTEXT_AXES,
        clearance=STACK_CLEARANCE,
        grid=CONTEXTUAL_RAISE_GRID,
        target_order=17,
    ),
    ContextualRaiseRelation(
        name="koronis",
        target_anchor=KORONIS_ANCHOR,
        target_codepoints=KORONIS_CODEPOINTS,
        axes=TARGET_CONTEXT_AXES,
        clearance=STACK_CLEARANCE,
        grid=CONTEXTUAL_RAISE_GRID,
        target_order=7,
    ),
)
CONTEXTUAL_FTHORA_CORRECTION_RELATIONS = (
    ContextualRaiseRelation(
        name="ison_fthoraCorrection",
        target_anchor=ISON_ANCHOR,
        target_codepoints=ISON_INDICATOR_CODEPOINTS,
        axes=TARGET_CONTEXT_AXES,
        clearance=STACK_CLEARANCE,
        grid=CONTEXTUAL_RAISE_GRID,
        target_order=17,
    ),
    ContextualRaiseRelation(
        name="koronis_fthoraCorrection",
        target_anchor=KORONIS_ANCHOR,
        target_codepoints=KORONIS_CODEPOINTS,
        axes=TARGET_CONTEXT_AXES,
        clearance=STACK_CLEARANCE,
        grid=CONTEXTUAL_RAISE_GRID,
        target_order=7,
    ),
)
GENERATED_CONTEXTUAL_RAISE_RELATIONS = (
    CONTEXTUAL_RAISE_RELATIONS + CONTEXTUAL_FTHORA_CORRECTION_RELATIONS
)
FTHORA_CONTEXT_RELATIONS: Final = tuple(
    relation
    for relation in CONTEXTUAL_RAISE_RELATIONS
    if relation.name in FTHORA_TARGET_STAGE_BY_RELATION_NAME
)
FTHORA_CORRECTION_SUFFIX: Final = "_fthoraCorrection"
FTHORA_CORRECTION_RELATION_BY_SOURCE_NAME: Final = {
    relation.name[: -len(FTHORA_CORRECTION_SUFFIX)]: relation
    for relation in CONTEXTUAL_FTHORA_CORRECTION_RELATIONS
}
BASE_ANCHOR_RULES = (ISON_BASE_ANCHOR_RULE,)


def source_paths() -> list[Path]:
    return sorted(SOURCES_DIR.glob("*.sfd"))


def get_anchor(glyph: Any, name: str, kind: str) -> Anchor | None:
    for anchor_name, anchor_kind, x, y in glyph.anchorPoints:
        if anchor_name == name and anchor_kind == kind:
            return x, y
    return None


def replace_anchor(glyph: Any, name: str, kind: str, x: int, y: int) -> None:
    glyph.anchorPoints = tuple(
        anchor
        for anchor in glyph.anchorPoints
        if not (anchor[0] == name and anchor[1] == kind)
    )
    glyph.addAnchorPoint(name, kind, x, y)


def read_modification_time(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(MODIFICATION_TIME_PREFIX):
            return line
    return None


def restore_modification_time(path: Path, modification_time: str | None) -> None:
    if modification_time is None:
        return

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if not line.startswith(MODIFICATION_TIME_PREFIX):
            continue

        ending = "\n" if line.endswith("\n") else ""
        lines[index] = f"{modification_time}{ending}"
        path.write_text("".join(lines), encoding="utf-8")
        return


def glyph_names_for_codepoints(font: Any, codepoints: Iterable[int]) -> list[str]:
    glyph_names = []
    for codepoint in codepoints:
        try:
            glyph = font[codepoint]
        except (KeyError, TypeError):
            continue
        glyph_names.append(glyph.glyphname)
    return glyph_names


def glyph_list(glyph_names: Iterable[str]) -> str:
    return "[" + " ".join(glyph_names) + "]"


def remove_mark_class(font: Any, class_name: str) -> bool:
    mark_classes = tuple(font.markClasses or ())
    updated_mark_classes = tuple(
        (name, names) for name, names in mark_classes if name != class_name
    )
    font.markClasses = updated_mark_classes
    return len(updated_mark_classes) != len(mark_classes)


def set_mark_class(font: Any, class_name: str, glyph_names: Iterable[str]) -> None:
    remove_mark_class(font, class_name)
    font.markClasses = (font.markClasses or ()) + (
        (class_name, tuple(sorted(glyph_names))),
    )


def remove_generated_lookups(
    font: Any, relations: Iterable[ContextualRaiseRelation]
) -> bool:
    generated_prefixes = {
        prefix
        for relation in relations
        for prefix in (relation.lookup_prefix, relation.context_lookup_prefix)
    }

    removed = False
    for lookup in list(font.gpos_lookups):
        if any(lookup.startswith(prefix) for prefix in generated_prefixes):
            font.removeLookup(lookup)
            removed = True
    return removed


def remove_generated_mark_classes(
    font: Any, relations: Iterable[ContextualRaiseRelation]
) -> bool:
    generated_classes = {relation.mark_class for relation in relations}
    removed = False
    for class_name in generated_classes:
        removed = remove_mark_class(font, class_name) or removed
    return removed


def reference_anchor_y(font: Any, rule: BaseAnchorRule) -> int | None:
    try:
        reference_glyph = font[rule.reference_glyph_name]
    except (KeyError, TypeError):
        return None

    anchor = get_anchor(reference_glyph, rule.anchor_name, BASE_ANCHOR_KIND)
    if anchor is None:
        return None
    return anchor[1]


def expected_base_anchor_y(glyph: Any, reference_y: int, rule: BaseAnchorRule) -> int:
    if glyph.glyphname == rule.reference_glyph_name:
        return reference_y

    full_y = max(reference_y, math.ceil(glyph.boundingBox()[3] + rule.clearance))
    if glyph.unicode in rule.compromise_codepoints:
        return math.ceil((reference_y + full_y) / 2)
    return full_y


def update_base_anchors(font: Any, rule: BaseAnchorRule) -> bool:
    reference_y = reference_anchor_y(font, rule)
    if reference_y is None:
        return False

    for anchor_class in rule.obsolete_anchor_classes:
        try:
            font.removeAnchorClass(anchor_class)
        except EnvironmentError:
            pass

    for glyph in font.glyphs():
        anchor = get_anchor(glyph, rule.anchor_name, BASE_ANCHOR_KIND)
        if anchor is None:
            continue

        replace_anchor(
            glyph,
            rule.anchor_name,
            BASE_ANCHOR_KIND,
            anchor[0],
            expected_base_anchor_y(glyph, reference_y, rule),
        )

    return True


def quantize_positive_delta(delta_y: int, grid: int) -> int:
    if delta_y <= 0:
        return 0
    return math.ceil(delta_y / grid) * grid


def required_raise_delta(
    target_base_y: int,
    context_base_y: int,
    context_mark_y: int,
    context_ymax: int,
    relation: ContextualRaiseRelation,
) -> int:
    context_top_y = context_base_y - context_mark_y + context_ymax
    required_y = max(target_base_y, math.ceil(context_top_y + relation.clearance))
    return quantize_positive_delta(required_y - target_base_y, relation.grid)


def context_marks_by_axis(
    font: Any, relation: ContextualRaiseRelation
) -> ContextMarksByAxis:
    marks_by_axis: ContextMarksByAxis = {}
    for axis in relation.axes:
        mark_names = glyph_names_for_codepoints(font, axis.codepoints)
        if not mark_names:
            continue

        mark_anchors = {}
        for mark_name in mark_names:
            mark_anchor = get_anchor(
                font[mark_name], axis.anchor_name, MARK_ANCHOR_KIND
            )
            if mark_anchor is None:
                raise ValueError(
                    f"{mark_name} is missing a {axis.anchor_name} mark anchor"
                )
            mark_anchors[mark_name] = mark_anchor

        marks_by_axis[axis.name] = mark_anchors

    return marks_by_axis


def active_contextual_raise_relation(
    font: Any, relation: ContextualRaiseRelation
) -> ActiveContextualRaiseRelation | None:
    target_names = glyph_names_for_codepoints(font, relation.target_codepoints)
    marks_by_axis = context_marks_by_axis(font, relation)
    if not target_names or not marks_by_axis:
        return None
    return ActiveContextualRaiseRelation(
        relation=relation,
        target_names=target_names,
        marks_by_axis=marks_by_axis,
    )


def active_contextual_raise_relations(
    font: Any, relations: Iterable[ContextualRaiseRelation]
) -> list[ActiveContextualRaiseRelation]:
    active: list[ActiveContextualRaiseRelation] = []
    for relation in relations:
        active_relation = active_contextual_raise_relation(font, relation)
        if active_relation is None:
            continue
        active.append(active_relation)
    return active


def build_axis_raise_deltas(
    font: Any,
    relation: ContextualRaiseRelation,
    marks_by_axis: ContextMarksByAxis,
) -> AxisDeltas:
    axis_by_name = {axis.name: axis for axis in relation.axes}
    axis_deltas: AxisDeltas = {axis.name: {} for axis in relation.axes}
    for base in font.glyphs():
        target_anchor = get_anchor(base, relation.target_anchor, BASE_ANCHOR_KIND)
        if target_anchor is None:
            continue

        _, target_base_y = target_anchor
        for axis_name, mark_anchors in marks_by_axis.items():
            axis = axis_by_name[axis_name]
            if not axis.contributes_to_raise:
                axis_deltas[axis_name][base.glyphname] = {
                    mark_name: 0 for mark_name in mark_anchors
                }
                continue

            context_base_anchor = get_anchor(base, axis.anchor_name, BASE_ANCHOR_KIND)
            if context_base_anchor is None:
                continue

            _, context_base_y = context_base_anchor
            deltas_by_mark: dict[str, int] = {}
            for mark_name, (_, context_mark_y) in mark_anchors.items():
                delta_y = required_raise_delta(
                    target_base_y,
                    context_base_y,
                    context_mark_y,
                    font[mark_name].boundingBox()[3],
                    relation,
                )
                deltas_by_mark[mark_name] = delta_y

            axis_deltas[axis_name][base.glyphname] = deltas_by_mark

    return axis_deltas


def bucket_glyphs_by_delta(
    deltas_by_glyph: dict[str, int],
) -> DeltaBuckets:
    buckets: DeltaBuckets = defaultdict(set)
    for glyph_name, delta_y in deltas_by_glyph.items():
        buckets[delta_y].add(glyph_name)
    return buckets


def add_raise_rule(
    context_rules: ContextRules,
    base_name: str,
    mark_slots: Iterable[tuple[str, Iterable[str]]],
    delta_y: int,
) -> None:
    if delta_y <= 0:
        return

    key = (
        tuple(
            (axis_name, frozenset(mark_names)) for axis_name, mark_names in mark_slots
        ),
        delta_y,
    )
    context_rules[key].add(base_name)


def axis_subsets(
    axis_names: tuple[str, ...],
    minimum_size: int = 0,
) -> Iterable[tuple[str, ...]]:
    for subset_size in range(minimum_size, len(axis_names) + 1):
        yield from combinations(axis_names, subset_size)


def mark_names_below_delta(
    delta_buckets: dict[int, set[str]],
    delta_y: int,
    *,
    strict: bool,
) -> set[str]:
    return {
        mark_name
        for mark_delta_y, mark_names in delta_buckets.items()
        if mark_delta_y < delta_y or (not strict and mark_delta_y == delta_y)
        for mark_name in mark_names
    }


def winner_mark_slots(
    delta_buckets_by_axis: DeltaBucketsByAxis,
    axis_subset: tuple[str, ...],
    winner_index: int,
    winner_axis: str,
    delta_y: int,
    winner_mark_names: set[str],
) -> tuple[tuple[str, set[str]], ...] | None:
    mark_slots = []
    for axis_index, axis_name in enumerate(axis_subset):
        if axis_name == winner_axis:
            mark_names = winner_mark_names
        else:
            mark_names = mark_names_below_delta(
                delta_buckets_by_axis[axis_name],
                delta_y,
                strict=axis_index < winner_index,
            )

        if not mark_names:
            return None
        mark_slots.append((axis_name, mark_names))

    return tuple(mark_slots)


def add_winner_raise_rules_for_base(
    context_rules: ContextRules,
    base_name: str,
    delta_buckets_by_axis: DeltaBucketsByAxis,
    active_axes: tuple[str, ...],
    trailing_mark_slots: tuple[tuple[str, Iterable[str]], ...] = (),
) -> None:
    for axis_subset in axis_subsets(active_axes, minimum_size=1):
        for winner_index, winner_axis in enumerate(axis_subset):
            for delta_y, winner_mark_names in delta_buckets_by_axis[
                winner_axis
            ].items():
                if delta_y <= 0:
                    continue

                mark_slots = winner_mark_slots(
                    delta_buckets_by_axis,
                    axis_subset,
                    winner_index,
                    winner_axis,
                    delta_y,
                    winner_mark_names,
                )
                if mark_slots is not None:
                    add_raise_rule(
                        context_rules,
                        base_name,
                        (*mark_slots, *trailing_mark_slots),
                        delta_y,
                    )


def delta_buckets_by_axis_for_base(
    axis_deltas: AxisDeltas,
    base_name: str,
    axis_names: Iterable[str],
) -> DeltaBucketsByAxis:
    return {
        axis_name: bucket_glyphs_by_delta(axis_deltas[axis_name].get(base_name, {}))
        for axis_name in axis_names
    }


def base_names_for_axis_deltas(axis_deltas: AxisDeltas) -> list[str]:
    return sorted(
        {
            base_name
            for deltas_by_base in axis_deltas.values()
            for base_name in deltas_by_base
        }
    )


def active_axis_names(
    delta_buckets_by_axis: DeltaBucketsByAxis,
    axis_names: Iterable[str],
) -> tuple[str, ...]:
    return tuple(
        axis_name for axis_name in axis_names if delta_buckets_by_axis[axis_name]
    )


def build_contextual_raise_rules(
    font: Any,
    relation: ContextualRaiseRelation,
    marks_by_axis: ContextMarksByAxis,
) -> ContextRules:
    axis_deltas = build_axis_raise_deltas(font, relation, marks_by_axis)
    axis_names = relation.axis_names
    context_rules: ContextRules = defaultdict(set)

    for base_name in base_names_for_axis_deltas(axis_deltas):
        delta_buckets_by_axis = delta_buckets_by_axis_for_base(
            axis_deltas,
            base_name,
            axis_names,
        )
        add_winner_raise_rules_for_base(
            context_rules,
            base_name,
            delta_buckets_by_axis,
            active_axis_names(delta_buckets_by_axis, axis_names),
        )

    return context_rules


def fthora_correction_relation(
    relation: ContextualRaiseRelation,
) -> ContextualRaiseRelation | None:
    return FTHORA_CORRECTION_RELATION_BY_SOURCE_NAME.get(relation.name)


def shared_fthora_dependency_axes(
    relation: ContextualRaiseRelation,
    fthora_relation: ContextualRaiseRelation,
) -> tuple[ContextAxis, ...]:
    relation_axis_names = set(relation.axis_names)
    return tuple(
        axis for axis in fthora_relation.axes if axis.name in relation_axis_names
    )


def build_dependent_fthora_correction_rules(
    font: Any,
    relation: ContextualRaiseRelation,
    marks_by_axis: ContextMarksByAxis,
) -> ContextRules:
    if fthora_correction_relation(relation) is None:
        return defaultdict(set)

    target_axis_deltas = build_axis_raise_deltas(font, relation, marks_by_axis)
    context_rules: ContextRules = defaultdict(set)

    for fthora_relation in FTHORA_CONTEXT_RELATIONS:
        fthora_stage_name = FTHORA_TARGET_STAGE_BY_RELATION_NAME[fthora_relation.name]
        fthora_axis_deltas = build_axis_raise_deltas(
            font,
            fthora_relation,
            context_marks_by_axis(font, fthora_relation),
        )
        fthora_dependency_axes = shared_fthora_dependency_axes(
            relation,
            fthora_relation,
        )
        fthora_dependency_axis_names = tuple(
            axis.name for axis in fthora_dependency_axes
        )

        for base_name, fthora_target_deltas in sorted(
            target_axis_deltas.get(fthora_stage_name, {}).items()
        ):
            covered_fthora_mark_names = set(fthora_target_deltas)
            delta_buckets_by_axis = delta_buckets_by_axis_for_base(
                fthora_axis_deltas,
                base_name,
                fthora_dependency_axis_names,
            )
            add_winner_raise_rules_for_base(
                context_rules,
                base_name,
                delta_buckets_by_axis,
                active_axis_names(delta_buckets_by_axis, fthora_dependency_axis_names),
                ((fthora_stage_name, covered_fthora_mark_names),),
            )

    return context_rules


def contextual_raise_rule(
    relation: ContextualRaiseRelation,
    base_names: Iterable[str],
    mark_slots: Iterable[MarkSlot],
    target_class: str,
    delta_lookup: str,
) -> str:
    axis_by_name = {axis.name: axis for axis in relation.axes}
    before_target = []
    after_target = []
    for axis_name, mark_names in mark_slots:
        axis = axis_by_name[axis_name]
        mark_class = glyph_list(sorted(mark_names))
        if axis.order < relation.target_order:
            before_target.append(mark_class)
        else:
            after_target.append(mark_class)

    before_context = " ".join([glyph_list(sorted(base_names)), *before_target])
    after_context = " ".join(after_target)
    if after_context:
        return (
            f"{before_context} | " f"{target_class} @<{delta_lookup}> {after_context} |"
        )

    return f"{before_context} | " f"{target_class} @<{delta_lookup}> |"


def delta_lookup_name(relation: ContextualRaiseRelation, delta_y: int) -> str:
    if delta_y <= 0:
        raise ValueError(f"delta lookup requires a positive delta, got {delta_y}")
    return f"{relation.lookup_prefix}_p{delta_y:03d}"


def raise_rule_sort_key(
    item: tuple[RaiseRuleKey, set[str]],
) -> tuple[int, int, tuple[tuple[str, tuple[str, ...]], ...], tuple[str, ...]]:
    (mark_slots, delta_y), base_names = item
    normalized_mark_slots = tuple(
        (axis_name, tuple(sorted(mark_names))) for axis_name, mark_names in mark_slots
    )
    return (
        -len(mark_slots),
        -delta_y,
        normalized_mark_slots,
        tuple(sorted(base_names)),
    )


def add_delta_lookups(
    font: Any,
    relation: ContextualRaiseRelation,
    context_rules: ContextRules,
    target_names: Iterable[str],
    previous_lookup: str,
) -> tuple[dict[int, str], str]:
    delta_lookup_names: dict[int, str] = {}
    delta_values = sorted({delta_y for _mark_slots, delta_y in context_rules})
    for delta_y in delta_values:
        lookup = delta_lookup_name(relation, delta_y)
        subtable = f"{lookup}-1"
        font.addLookup(lookup, "gpos_single", (), (), previous_lookup)
        font.addLookupSubtable(lookup, subtable)
        for target_name in target_names:
            font[target_name].addPosSub(subtable, 0, delta_y, 0, 0)

        delta_lookup_names[delta_y] = lookup
        previous_lookup = lookup

    return delta_lookup_names, previous_lookup


def add_context_lookup(
    font: Any,
    relation: ContextualRaiseRelation,
    context_rules: ContextRules,
    target_class: str,
    delta_lookup_names: dict[int, str],
    previous_lookup: str,
) -> str:
    context_lookup = relation.context_lookup_prefix
    font.addLookup(
        context_lookup,
        "gpos_contextchain",
        (relation.mark_class),
        relation.features,
        previous_lookup,
    )

    previous_subtable = None
    subtable_index = 1
    for (mark_slots, delta_y), base_names in sorted(
        context_rules.items(), key=raise_rule_sort_key
    ):
        subtable = f"{context_lookup}-{subtable_index}"
        rule = contextual_raise_rule(
            relation,
            base_names,
            mark_slots,
            target_class,
            delta_lookup_names[delta_y],
        )
        if previous_subtable is None:
            font.addContextualSubtable(context_lookup, subtable, "coverage", rule)
        else:
            font.addContextualSubtable(
                context_lookup,
                subtable,
                "coverage",
                rule,
                previous_subtable,
            )
        previous_subtable = subtable
        subtable_index += 1

    return context_lookup


def add_contextual_raise_lookups(
    font: Any,
    relation: ContextualRaiseRelation,
    context_rules: ContextRules,
    target_names: Iterable[str],
    previous_lookup: str,
) -> str:
    if not context_rules:
        return previous_lookup

    delta_lookup_names, previous_lookup = add_delta_lookups(
        font,
        relation,
        context_rules,
        target_names,
        previous_lookup,
    )
    target_class = glyph_list(target_names)

    context_lookup = add_context_lookup(
        font,
        relation,
        context_rules,
        target_class,
        delta_lookup_names,
        previous_lookup,
    )
    print(
        f"{font.fontname}: {context_lookup}: {len(context_rules)} "
        f"contextual subtables, {len(delta_lookup_names)} delta subtables"
    )
    return context_lookup


def add_contextual_raise_relation(
    font: Any,
    active_relation: ActiveContextualRaiseRelation,
    previous_lookup: str,
) -> str:
    relation = active_relation.relation
    rules = build_contextual_raise_rules(
        font,
        relation,
        active_relation.marks_by_axis,
    )
    previous_lookup = add_contextual_raise_lookups(
        font,
        relation,
        rules,
        active_relation.target_names,
        previous_lookup,
    )
    correction_relation = fthora_correction_relation(relation)
    if correction_relation is None:
        return previous_lookup

    correction_rules = build_dependent_fthora_correction_rules(
        font,
        relation,
        active_relation.marks_by_axis,
    )
    return add_contextual_raise_lookups(
        font,
        correction_relation,
        correction_rules,
        active_relation.target_names,
        previous_lookup,
    )


def set_context_mark_classes(
    font: Any, active_relations: Iterable[ActiveContextualRaiseRelation]
) -> None:
    glyph_names_by_mark_class: defaultdict[str, set[str]] = defaultdict(set)
    for active_relation in active_relations:
        glyph_names = glyph_names_by_mark_class[active_relation.relation.mark_class]
        glyph_names.update(active_relation.target_names)
        for mark_anchors in active_relation.marks_by_axis.values():
            glyph_names.update(mark_anchors)

    for mark_class, glyph_names in glyph_names_by_mark_class.items():
        set_mark_class(font, mark_class, glyph_names)


def update_font(path: Path) -> bool:
    modification_time = read_modification_time(path)
    font = fontforge.open(str(path))

    try:
        changed = remove_generated_lookups(
            font,
            GENERATED_CONTEXTUAL_RAISE_RELATIONS,
        )
        changed = (
            remove_generated_mark_classes(font, GENERATED_CONTEXTUAL_RAISE_RELATIONS)
            or changed
        )

        for rule in BASE_ANCHOR_RULES:
            changed = update_base_anchors(font, rule) or changed

        active_relations = active_contextual_raise_relations(
            font,
            CONTEXTUAL_RAISE_RELATIONS,
        )
        if active_relations:
            set_context_mark_classes(font, active_relations)

        previous_lookup = MARK_LOOKUP
        for active_relation in active_relations:
            previous_lookup = add_contextual_raise_relation(
                font,
                active_relation,
                previous_lookup,
            )
            changed = True

        if changed:
            font.save(str(path))
    finally:
        font.close()
        restore_modification_time(path, modification_time)
    return changed


if __name__ == "__main__":
    for source_path in source_paths():
        update_font(source_path)
