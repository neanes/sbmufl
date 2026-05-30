#!/usr/bin/env python3
"""Apply additive/max contextual mark positioning to built OTFs.

The source SFDs contain ordinary mark attachment data. This post-build step adds
compact chained contextual GPOS Format 2 lookups to the generated OTFs so marks
such as ison, koronis, and fthora clear lower marks by the needed height:

    fthora += gorgon_fthora_raise
    fthora += klasma_fthora_raise
    secondary_fthora += secondary_gorgon_secondary_fthora_raise
    ison += gorgon_ison_raise
    ison += klasma_ison_raise
    ison += fthora_ison_raise
    ison += secondary_fthora_ison_raise
    ison += tertiary_fthora_ison_raise
    ison += gorgon_fthora_raise - min(gorgon_ison_raise, fthora_ison_raise)
    ison += klasma_fthora_raise - min(klasma_ison_raise, fthora_ison_raise)
    ison += secondary_gorgon_secondary_fthora_raise
    koronis += klasma_koronis_raise
    koronis += gorgon_koronis_raise
    koronis += fthora_koronis_raise
    koronis += gorgon_fthora_raise - min(gorgon_koronis_raise, fthora_koronis_raise)
    koronis += klasma_fthora_raise - min(klasma_koronis_raise, fthora_koronis_raise)

The generated lookups use chained contextual GPOS Format 2 and mark filtering.

Usage:
    python scripts/generate-contextual-positioning.py fonts/*.otf
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Mapping
from dataclasses import dataclass, fields
from enum import Enum, auto
from functools import partial
from pathlib import Path
from typing import Any, TypeVar

from fontTools.otlLib.builder import (
    ChainContextPosBuilder,
    ChainContextualRule,
    SinglePosBuilder,
    ValueRecord,
    buildCoverage,
)
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "fontbakery"))

from sbmufl.constants import (  # noqa: E402
    SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS,
    SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS,
    SBMUFL_FTHORA_TERTIARY_ABOVE_CODEPOINTS,
    SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS,
    SBMUFL_GORGON_SECONDARY_ABOVE_CODEPOINTS,
    SBMUFL_ISON_INDICATOR_CODEPOINTS,
    SBMUFL_ISON_INDICATOR_COMPROMISE_CODEPOINTS,
    SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
    SBMUFL_KLASMA_ABOVE_CODEPOINTS,
    SBMUFL_KORONIS_CODEPOINTS,
    SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
)
from sbmufl.domain import contextual_positioning, ison  # noqa: E402
from sbmufl.framework.glyphs import GlyphIntrospector  # noqa: E402
from sbmufl.framework.gpos import GposIntrospector  # noqa: E402
from sbmufl.framework.shaping import Shaper  # noqa: E402

AxisDeltas = dict[tuple[str, str], int]
LookupDict = dict[int, Any]
SimpleProfile = tuple[tuple[str, int], ...]
DependencyProfile = tuple[tuple[str, int, int], ...]
CombinedProfile = tuple[DependencyProfile, SimpleProfile]
PairProfile = tuple[SimpleProfile, SimpleProfile]
SimpleProfileMap = dict[str, SimpleProfile]
CombinedProfileMap = dict[str, CombinedProfile]
PairProfileMap = dict[str, PairProfile]
Profile = TypeVar("Profile", bound=Hashable)
SimpleRuleBuilderFn = Callable[
    [list[str], SimpleProfile, list[str], LookupDict],
    list[ChainContextualRule],
]
CombinedRuleBuilderFn = Callable[
    [list[str], DependencyProfile, SimpleProfile, list[str], LookupDict],
    list[ChainContextualRule],
]
PairRuleBuilderFn = Callable[
    [list[str], SimpleProfile, SimpleProfile, list[str], LookupDict],
    list[ChainContextualRule],
]


class ContextLookupKind(Enum):
    SIMPLE = auto()
    COMBINED = auto()
    PAIR = auto()


class ContextRuleBuilderKey(Enum):
    SINGLE_AXIS = auto()
    COMBINED_CORRECTION = auto()
    PAIR_MAX_CORRECTION = auto()
    KORONIS_BEFORE_TARGET = auto()
    KORONIS_AFTER_TARGET = auto()
    KORONIS_DEPENDENCY_BEFORE_TARGET = auto()
    KORONIS_DEPENDENCY_AFTER_TARGET = auto()
    KORONIS_PAIR_MAX_CORRECTION = auto()


class MarkSource(Enum):
    PRIMARY_GORGON = auto()
    KLASMA = auto()
    KORONIS = auto()
    SECONDARY_GORGON = auto()
    PRIMARY_FTHORA = auto()
    SECONDARY_FTHORA = auto()
    TERTIARY_FTHORA = auto()
    KORONIS_KLASMA = auto()
    KORONIS_GORGON = auto()
    KORONIS_FTHORA = auto()


@dataclass(frozen=True)
class SimpleRuleBuilder:
    build: SimpleRuleBuilderFn


@dataclass(frozen=True)
class CombinedRuleBuilder:
    build: CombinedRuleBuilderFn


@dataclass(frozen=True)
class PairRuleBuilder:
    build: PairRuleBuilderFn


RuleBuilder = SimpleRuleBuilder | CombinedRuleBuilder | PairRuleBuilder


@dataclass(frozen=True)
class FontGenerationResult:
    path: Path
    original_size: int
    generated_size: int
    original_gpos_size: int
    generated_gpos_size: int
    original_lookup_count: int
    generated_lookup_count: int
    context_lookup_formats: dict[str, list[int]]
    mismatches_by_label: dict[str, list[str]]


@dataclass(frozen=True)
class ContextualDeltaSpec:
    name: str
    target_codepoints: frozenset[int]
    context_codepoints: frozenset[int]
    expected_y: str | None = None


@dataclass(frozen=True)
class ContextualTargetSpec:
    name: str
    codepoints: frozenset[int]


@dataclass(frozen=True)
class ValidationMarkSourceSpec:
    source: MarkSource
    delta: str | None = None
    target: str | None = None

    def __post_init__(self) -> None:
        if (self.delta is None) == (self.target is None):
            raise ValueError(
                "validation mark source specs must declare exactly one "
                "delta or target"
            )


@dataclass(frozen=True)
class CombinedProfileSpec:
    name: str
    target_delta: str | None
    raised_mark_delta: str
    target_profile: str


@dataclass(frozen=True)
class PairProfileSpec:
    name: str
    first_profile: str
    second_profile: str


@dataclass(frozen=True)
class LookupDeltaGroupSpec:
    name: str
    target: str
    label: str
    profiles: tuple[str, ...] = ()
    corrections: tuple[str, ...] = ()
    pair_corrections: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarkFilterSpec:
    name: str
    marks: tuple[str, ...]
    target: str


@dataclass(frozen=True)
class ContextLookupSpec:
    name: str
    kind: ContextLookupKind
    profile: str
    target: str
    lookup_group: str
    rule_builder: ContextRuleBuilderKey


def dataclass_values_from_mapping(
    cls: type[Any],
    values_by_name: Mapping[str, Any],
    *,
    exclude: Iterable[str] = (),
) -> dict[str, Any]:
    excluded_names = set(exclude)
    field_names = tuple(
        field.name for field in fields(cls) if field.name not in excluded_names
    )
    expected_names = set(field_names)
    actual_names = set(values_by_name)
    missing_names = sorted(expected_names - actual_names)
    extra_names = sorted(actual_names - expected_names)
    if missing_names or extra_names:
        message_parts = []
        if missing_names:
            message_parts.append("missing " + ", ".join(missing_names))
        if extra_names:
            message_parts.append("unexpected " + ", ".join(extra_names))
        raise ValueError(f"{cls.__name__} mapping mismatch: {'; '.join(message_parts)}")
    return {name: values_by_name[name] for name in field_names}


@dataclass(frozen=True)
class ContextualDeltas:
    gorgon_ison: AxisDeltas
    klasma_ison: AxisDeltas
    fthora_ison: AxisDeltas
    secondary_fthora_ison: AxisDeltas
    tertiary_fthora_ison: AxisDeltas
    klasma_koronis: AxisDeltas
    gorgon_koronis: AxisDeltas
    fthora_koronis: AxisDeltas
    gorgon_fthora: AxisDeltas
    klasma_fthora: AxisDeltas
    secondary_gorgon_secondary_fthora: AxisDeltas

    @classmethod
    def from_mapping(cls, values_by_name: Mapping[str, AxisDeltas]) -> ContextualDeltas:
        return cls(**dataclass_values_from_mapping(cls, values_by_name))

    def bases_with_context(self) -> set[str]:
        return {
            base_name
            for deltas in (
                self.gorgon_ison,
                self.klasma_ison,
                self.fthora_ison,
                self.secondary_fthora_ison,
                self.tertiary_fthora_ison,
                self.klasma_koronis,
                self.gorgon_koronis,
                self.fthora_koronis,
                self.secondary_gorgon_secondary_fthora,
            )
            for base_name, _mark_name in deltas
        }


@dataclass(frozen=True)
class ContextualTargets:
    base_names: list[str]
    ison: list[str]
    koronis: list[str]
    primary_fthora: list[str]
    secondary_fthora: list[str]

    @classmethod
    def from_mapping(
        cls,
        values_by_name: Mapping[str, list[str]],
        *,
        base_names: list[str],
    ) -> ContextualTargets:
        return cls(
            base_names=base_names,
            **dataclass_values_from_mapping(
                cls, values_by_name, exclude=("base_names",)
            ),
        )


@dataclass(frozen=True)
class ContextualBuildState:
    base_names: list[str]
    target_names: dict[str, list[str]]
    simple_profiles: dict[str, SimpleProfileMap]
    combined_profiles: dict[str, CombinedProfileMap]
    pair_profiles: dict[str, PairProfileMap]
    lookup_groups: dict[str, LookupDict]
    filters: dict[str, int]
    rule_builders: dict[ContextRuleBuilderKey, RuleBuilder]

    @classmethod
    def create(
        cls,
        ttfont: TTFont,
        *,
        targets: ContextualTargets,
        deltas: ContextualDeltas,
    ) -> ContextualBuildState:
        base_names = targets.base_names
        target_names = target_names_by_spec(targets)
        simple_profiles = collect_simple_profiles(base_names, deltas)
        combined_profiles = collect_combined_profiles(
            base_names,
            deltas,
            simple_profiles,
        )
        pair_profiles = collect_pair_profiles(base_names, simple_profiles)
        lookup_groups = add_lookup_groups(
            ttfont,
            target_names,
            simple_profiles,
            combined_profiles,
            pair_profiles,
        )
        filters = add_mark_filters(ttfont, target_names, mark_groups_by_delta(deltas))
        return cls(
            base_names=base_names,
            target_names=target_names,
            simple_profiles=simple_profiles,
            combined_profiles=combined_profiles,
            pair_profiles=pair_profiles,
            lookup_groups=lookup_groups,
            filters=filters,
            rule_builders=context_rule_builders(),
        )


@dataclass(frozen=True)
class ValidationContext:
    base_name: str
    base_codepoint: int
    mark_names_by_source: Mapping[MarkSource, list[str]]

    @classmethod
    def build(
        cls,
        *,
        base_name: str,
        base_codepoint: int,
        targets: ContextualTargets,
        deltas: ContextualDeltas,
        codepoint_by_glyph: Mapping[str, int],
    ) -> ValidationContext:
        target_names = target_names_by_spec(targets)
        mark_names_by_source = {}
        for spec in validation_mark_source_specs():
            if spec.delta is not None:
                mark_names_by_source[spec.source] = mark_names_for_base(
                    getattr(deltas, spec.delta),
                    base_name,
                )
                continue
            if spec.target is None:
                raise ValueError(f"missing validation mark source target: {spec}")
            mark_names_by_source[spec.source] = [
                mark_name
                for mark_name in target_names[spec.target]
                if codepoint_by_glyph.get(mark_name) is not None
            ]
        return cls(base_name, base_codepoint, mark_names_by_source)

    def mark_names(self, source: MarkSource) -> list[str]:
        return self.mark_names_by_source[source]


@dataclass(frozen=True)
class DeltaRef:
    role: str
    key: str

    def __add__(self, other: ExpectedTerm) -> ProbeExpectedSpec:
        return combine_expected(self, other)

    def __radd__(self, other: ExpectedTerm) -> ProbeExpectedSpec:
        return combine_expected(other, self)


@dataclass(frozen=True)
class ProbeMarkSpec:
    role: str
    mark_source: MarkSource
    deltas: tuple[tuple[str, str], ...] = ()
    sample: bool = False


@dataclass(frozen=True)
class ProbeExpectedSpec:
    max_refs: tuple[DeltaRef, ...] = ()
    add_refs: tuple[DeltaRef, ...] = ()
    constant: int = 0

    def __add__(self, other: ExpectedTerm) -> ProbeExpectedSpec:
        return combine_expected(self, other)

    def __radd__(self, other: ExpectedTerm) -> ProbeExpectedSpec:
        return combine_expected(other, self)


@dataclass(frozen=True)
class ContextualProbeSpec:
    label: str
    target: str
    sequence: tuple[str, ...]
    marks: tuple[ProbeMarkSpec, ...]
    expected: ProbeExpectedSpec


@dataclass(frozen=True)
class ContextualProbeGroup:
    name: str
    specs: tuple[ContextualProbeSpec, ...]


ExpectedTerm = DeltaRef | ProbeExpectedSpec | int


def as_expected_spec(term: ExpectedTerm) -> ProbeExpectedSpec:
    if isinstance(term, ProbeExpectedSpec):
        return term
    if isinstance(term, DeltaRef):
        return ProbeExpectedSpec(add_refs=(term,))
    return ProbeExpectedSpec(constant=term)


def combine_expected(left: ExpectedTerm, right: ExpectedTerm) -> ProbeExpectedSpec:
    left_spec = as_expected_spec(left)
    right_spec = as_expected_spec(right)
    if left_spec.max_refs and right_spec.max_refs:
        raise ValueError("expected formula supports one max() term")
    return ProbeExpectedSpec(
        max_refs=left_spec.max_refs or right_spec.max_refs,
        add_refs=left_spec.add_refs + right_spec.add_refs,
        constant=left_spec.constant + right_spec.constant,
    )


def target_delta(role: str) -> DeltaRef:
    return DeltaRef(role, "target")


def raise_delta(role: str) -> DeltaRef:
    return DeltaRef(role, "raise")


def max_delta(*refs: DeltaRef) -> ProbeExpectedSpec:
    return ProbeExpectedSpec(max_refs=refs)


def probe_mark(
    role: str,
    mark_source: MarkSource,
    *,
    target: str | None = None,
    raise_: str | None = None,
    sample: bool = False,
) -> ProbeMarkSpec:
    deltas = []
    if target is not None:
        deltas.append(("target", target))
    if raise_ is not None:
        deltas.append(("raise", raise_))
    return ProbeMarkSpec(role, mark_source, tuple(deltas), sample=sample)


def probe(
    label: str,
    *,
    target: str,
    mark_sequence: tuple[str, ...],
    marks: tuple[ProbeMarkSpec, ...],
    expected: ExpectedTerm = 0,
) -> ContextualProbeSpec:
    return ContextualProbeSpec(
        label=label,
        target=target,
        sequence=("base", *mark_sequence),
        marks=marks,
        expected=as_expected_spec(expected),
    )


def pass_through_probe(
    label: str,
    *,
    target: str,
    mark_sequence: tuple[str, ...],
    marks: tuple[ProbeMarkSpec, ...],
    dependency_role: str = "dependency",
) -> ContextualProbeSpec:
    return probe(
        label,
        target=target,
        mark_sequence=mark_sequence,
        marks=marks,
        expected=raise_delta(dependency_role),
    )


def fthora_pass_through_probe(
    *,
    mark_sequence: tuple[str, ...],
    marks: tuple[ProbeMarkSpec, ...],
) -> ContextualProbeSpec:
    return pass_through_probe(
        "fthora pass-through",
        target="fthora",
        mark_sequence=mark_sequence,
        marks=marks,
    )


def secondary_fthora_pass_through_probe(
    *,
    mark_sequence: tuple[str, ...],
    marks: tuple[ProbeMarkSpec, ...],
) -> ContextualProbeSpec:
    return pass_through_probe(
        "secondary fthora pass-through",
        target="secondary_fthora",
        mark_sequence=mark_sequence,
        marks=marks,
    )


def probe_group(
    name: str,
    specs: tuple[ContextualProbeSpec, ...],
) -> ContextualProbeGroup:
    return ContextualProbeGroup(name, specs)


ProbeSpecGroups = tuple[ContextualProbeGroup, ...]


def contextual_probe_spec_groups() -> ProbeSpecGroups:
    return (
        probe_group(
            "basic_probes",
            (
                probe(
                    "ison tertiary fthora",
                    target="ison",
                    mark_sequence=("mark", "ison"),
                    marks=(
                        probe_mark(
                            "mark",
                            MarkSource.TERTIARY_FTHORA,
                            target="tertiary_fthora_ison",
                        ),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "koronis klasma",
                    target="koronis",
                    mark_sequence=("mark", "koronis"),
                    marks=(
                        probe_mark(
                            "mark", MarkSource.KORONIS_KLASMA, target="klasma_koronis"
                        ),
                        probe_mark("koronis", MarkSource.KORONIS),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "koronis gorgon",
                    target="koronis",
                    mark_sequence=("koronis", "mark"),
                    marks=(
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "mark", MarkSource.KORONIS_GORGON, target="gorgon_koronis"
                        ),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "koronis fthora",
                    target="koronis",
                    mark_sequence=("koronis", "mark"),
                    marks=(
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "mark", MarkSource.KORONIS_FTHORA, target="fthora_koronis"
                        ),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "ison klasma",
                    target="ison",
                    mark_sequence=("mark", "ison"),
                    marks=(
                        probe_mark("mark", MarkSource.KLASMA, target="klasma_ison"),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "ison gorgon",
                    target="ison",
                    mark_sequence=("mark", "ison"),
                    marks=(
                        probe_mark(
                            "mark", MarkSource.PRIMARY_GORGON, target="gorgon_ison"
                        ),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "ison fthora",
                    target="ison",
                    mark_sequence=("mark", "ison"),
                    marks=(
                        probe_mark(
                            "mark", MarkSource.PRIMARY_FTHORA, target="fthora_ison"
                        ),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "ison secondary fthora",
                    target="ison",
                    mark_sequence=("mark", "ison"),
                    marks=(
                        probe_mark(
                            "mark",
                            MarkSource.SECONDARY_FTHORA,
                            target="secondary_fthora_ison",
                        ),
                    ),
                    expected=target_delta("mark"),
                ),
                probe(
                    "koronis klasma gorgon combined",
                    target="koronis",
                    mark_sequence=("first", "koronis", "second"),
                    marks=(
                        probe_mark(
                            "first", MarkSource.KORONIS_KLASMA, target="klasma_koronis"
                        ),
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "second", MarkSource.KORONIS_GORGON, target="gorgon_koronis"
                        ),
                    ),
                    expected=max_delta(target_delta("first"), target_delta("second")),
                ),
                probe(
                    "ison klasma gorgon combined",
                    target="ison",
                    mark_sequence=("first", "second", "ison"),
                    marks=(
                        probe_mark("first", MarkSource.KLASMA, target="klasma_ison"),
                        probe_mark(
                            "second", MarkSource.PRIMARY_GORGON, target="gorgon_ison"
                        ),
                    ),
                    expected=max_delta(target_delta("first"), target_delta("second")),
                ),
            ),
        ),
        probe_group(
            "koronis_combined_probes",
            (
                probe(
                    "koronis klasma combined",
                    target="koronis",
                    mark_sequence=("dependency", "koronis", "fthora"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.KORONIS_KLASMA,
                            target="klasma_koronis",
                            raise_="klasma_fthora",
                        ),
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "fthora", MarkSource.KORONIS_FTHORA, target="fthora_koronis"
                        ),
                    ),
                    expected=(
                        max_delta(target_delta("dependency"), target_delta("fthora"))
                        + raise_delta("dependency")
                    ),
                ),
                probe(
                    "koronis gorgon combined",
                    target="koronis",
                    mark_sequence=("koronis", "dependency", "fthora"),
                    marks=(
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "dependency",
                            MarkSource.KORONIS_GORGON,
                            target="gorgon_koronis",
                            raise_="gorgon_fthora",
                        ),
                        probe_mark(
                            "fthora", MarkSource.KORONIS_FTHORA, target="fthora_koronis"
                        ),
                    ),
                    expected=(
                        max_delta(target_delta("dependency"), target_delta("fthora"))
                        + raise_delta("dependency")
                    ),
                ),
            ),
        ),
        probe_group(
            "fthora_pass_through_probes",
            (
                fthora_pass_through_probe(
                    mark_sequence=("dependency", "koronis", "fthora"),
                    marks=(
                        probe_mark(
                            "dependency", MarkSource.KLASMA, raise_="klasma_fthora"
                        ),
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                ),
                fthora_pass_through_probe(
                    mark_sequence=("dependency", "koronis", "pass", "fthora"),
                    marks=(
                        probe_mark(
                            "dependency", MarkSource.KLASMA, raise_="klasma_fthora"
                        ),
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark("pass", MarkSource.SECONDARY_GORGON),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                ),
                fthora_pass_through_probe(
                    mark_sequence=("koronis", "dependency", "fthora"),
                    marks=(
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "dependency",
                            MarkSource.PRIMARY_GORGON,
                            raise_="gorgon_fthora",
                        ),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                ),
                fthora_pass_through_probe(
                    mark_sequence=("koronis", "dependency", "pass", "fthora"),
                    marks=(
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "dependency",
                            MarkSource.PRIMARY_GORGON,
                            raise_="gorgon_fthora",
                        ),
                        probe_mark("pass", MarkSource.SECONDARY_GORGON),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                ),
                fthora_pass_through_probe(
                    mark_sequence=("dependency", "pass", "fthora"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.PRIMARY_GORGON,
                            raise_="gorgon_fthora",
                        ),
                        probe_mark("pass", MarkSource.SECONDARY_GORGON),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                ),
            ),
        ),
        probe_group(
            "ison_secondary_pass_through_probes",
            (
                probe(
                    "ison secondary gorgon pass-through",
                    target="ison",
                    mark_sequence=("dependency", "ison"),
                    marks=(probe_mark("dependency", MarkSource.SECONDARY_GORGON),),
                    expected=0,
                ),
                probe(
                    "ison secondary gorgon pass-through",
                    target="ison",
                    mark_sequence=("dependency", "fthora", "ison"),
                    marks=(
                        probe_mark("dependency", MarkSource.SECONDARY_GORGON),
                        probe_mark(
                            "fthora", MarkSource.PRIMARY_FTHORA, target="fthora_ison"
                        ),
                    ),
                    expected=target_delta("fthora"),
                ),
            ),
        ),
        probe_group(
            "secondary_fthora_probes",
            (
                probe(
                    "secondary fthora",
                    target="secondary_fthora",
                    mark_sequence=("dependency", "secondary_fthora"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.SECONDARY_GORGON,
                            raise_="secondary_gorgon_secondary_fthora",
                        ),
                        probe_mark("secondary_fthora", MarkSource.SECONDARY_FTHORA),
                    ),
                    expected=raise_delta("dependency"),
                ),
                secondary_fthora_pass_through_probe(
                    mark_sequence=("koronis", "dependency", "secondary_fthora"),
                    marks=(
                        probe_mark("koronis", MarkSource.KORONIS),
                        probe_mark(
                            "dependency",
                            MarkSource.SECONDARY_GORGON,
                            raise_="secondary_gorgon_secondary_fthora",
                        ),
                        probe_mark("secondary_fthora", MarkSource.SECONDARY_FTHORA),
                    ),
                ),
                secondary_fthora_pass_through_probe(
                    mark_sequence=("pass", "dependency", "secondary_fthora"),
                    marks=(
                        probe_mark("pass", MarkSource.PRIMARY_GORGON),
                        probe_mark(
                            "dependency",
                            MarkSource.SECONDARY_GORGON,
                            raise_="secondary_gorgon_secondary_fthora",
                        ),
                        probe_mark("secondary_fthora", MarkSource.SECONDARY_FTHORA),
                    ),
                ),
                secondary_fthora_pass_through_probe(
                    mark_sequence=("dependency", "pass", "secondary_fthora"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.SECONDARY_GORGON,
                            raise_="secondary_gorgon_secondary_fthora",
                        ),
                        probe_mark("pass", MarkSource.PRIMARY_FTHORA),
                        probe_mark("secondary_fthora", MarkSource.SECONDARY_FTHORA),
                    ),
                ),
                secondary_fthora_pass_through_probe(
                    mark_sequence=(
                        "koronis",
                        "primary_gorgon",
                        "dependency",
                        "primary_fthora",
                        "secondary_fthora",
                    ),
                    marks=(
                        probe_mark("koronis", MarkSource.KORONIS, sample=True),
                        probe_mark(
                            "primary_gorgon", MarkSource.PRIMARY_GORGON, sample=True
                        ),
                        probe_mark(
                            "dependency",
                            MarkSource.SECONDARY_GORGON,
                            raise_="secondary_gorgon_secondary_fthora",
                        ),
                        probe_mark(
                            "primary_fthora", MarkSource.PRIMARY_FTHORA, sample=True
                        ),
                        probe_mark("secondary_fthora", MarkSource.SECONDARY_FTHORA),
                    ),
                ),
                secondary_fthora_pass_through_probe(
                    mark_sequence=(
                        "primary_gorgon",
                        "dependency",
                        "primary_fthora",
                        "secondary_fthora",
                    ),
                    marks=(
                        probe_mark(
                            "primary_gorgon", MarkSource.PRIMARY_GORGON, sample=True
                        ),
                        probe_mark(
                            "dependency",
                            MarkSource.SECONDARY_GORGON,
                            raise_="secondary_gorgon_secondary_fthora",
                        ),
                        probe_mark(
                            "primary_fthora", MarkSource.PRIMARY_FTHORA, sample=True
                        ),
                        probe_mark("secondary_fthora", MarkSource.SECONDARY_FTHORA),
                    ),
                ),
            ),
        ),
        probe_group(
            "fthora_probes",
            (
                probe(
                    "fthora",
                    target="fthora",
                    mark_sequence=("dependency", "fthora"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.PRIMARY_GORGON,
                            raise_="gorgon_fthora",
                        ),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                    expected=raise_delta("dependency"),
                ),
                probe(
                    "fthora klasma",
                    target="fthora",
                    mark_sequence=("dependency", "fthora"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.KLASMA,
                            raise_="klasma_fthora",
                        ),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                    expected=raise_delta("dependency"),
                ),
                probe(
                    "fthora klasma gorgon combined",
                    target="fthora",
                    mark_sequence=("first", "second", "fthora"),
                    marks=(
                        probe_mark("first", MarkSource.KLASMA, raise_="klasma_fthora"),
                        probe_mark(
                            "second", MarkSource.PRIMARY_GORGON, raise_="gorgon_fthora"
                        ),
                        probe_mark("fthora", MarkSource.PRIMARY_FTHORA),
                    ),
                    expected=max_delta(raise_delta("first"), raise_delta("second")),
                ),
            ),
        ),
        probe_group(
            "ison_combined_probes",
            (
                probe(
                    "ison combined",
                    target="ison",
                    mark_sequence=("dependency", "fthora", "ison"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.PRIMARY_GORGON,
                            target="gorgon_ison",
                            raise_="gorgon_fthora",
                        ),
                        probe_mark(
                            "fthora", MarkSource.PRIMARY_FTHORA, target="fthora_ison"
                        ),
                    ),
                    expected=(
                        max_delta(target_delta("dependency"), target_delta("fthora"))
                        + raise_delta("dependency")
                    ),
                ),
                probe(
                    "ison klasma combined",
                    target="ison",
                    mark_sequence=("dependency", "fthora", "ison"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.KLASMA,
                            target="klasma_ison",
                            raise_="klasma_fthora",
                        ),
                        probe_mark(
                            "fthora", MarkSource.PRIMARY_FTHORA, target="fthora_ison"
                        ),
                    ),
                    expected=(
                        max_delta(target_delta("dependency"), target_delta("fthora"))
                        + raise_delta("dependency")
                    ),
                ),
                probe(
                    "ison secondary combined",
                    target="ison",
                    mark_sequence=("dependency", "fthora", "ison"),
                    marks=(
                        probe_mark(
                            "dependency",
                            MarkSource.SECONDARY_GORGON,
                            raise_="secondary_gorgon_secondary_fthora",
                        ),
                        probe_mark(
                            "fthora",
                            MarkSource.SECONDARY_FTHORA,
                            target="secondary_fthora_ison",
                        ),
                    ),
                    expected=target_delta("fthora") + raise_delta("dependency"),
                ),
            ),
        ),
    )


def mismatch_labels() -> tuple[str, ...]:
    labels = []
    seen_labels = set()
    for group in contextual_probe_spec_groups():
        for spec in group.specs:
            if spec.label in seen_labels:
                continue
            seen_labels.add(spec.label)
            labels.append(spec.label)
    return tuple(labels)


def contextual_delta_specs() -> tuple[ContextualDeltaSpec, ...]:
    return (
        ContextualDeltaSpec(
            "gorgon_ison",
            frozenset(SBMUFL_ISON_INDICATOR_CODEPOINTS),
            frozenset(SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS),
            expected_y="ison",
        ),
        ContextualDeltaSpec(
            "klasma_ison",
            frozenset(SBMUFL_ISON_INDICATOR_CODEPOINTS),
            frozenset(SBMUFL_KLASMA_ABOVE_CODEPOINTS),
            expected_y="ison",
        ),
        ContextualDeltaSpec(
            "fthora_ison",
            frozenset(SBMUFL_ISON_INDICATOR_CODEPOINTS),
            frozenset(SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS),
            expected_y="ison",
        ),
        ContextualDeltaSpec(
            "secondary_fthora_ison",
            frozenset(SBMUFL_ISON_INDICATOR_CODEPOINTS),
            frozenset(SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS),
            expected_y="ison",
        ),
        ContextualDeltaSpec(
            "tertiary_fthora_ison",
            frozenset(SBMUFL_ISON_INDICATOR_CODEPOINTS),
            frozenset(SBMUFL_FTHORA_TERTIARY_ABOVE_CODEPOINTS),
            expected_y="ison",
        ),
        ContextualDeltaSpec(
            "klasma_koronis",
            frozenset(SBMUFL_KORONIS_CODEPOINTS),
            frozenset(SBMUFL_KLASMA_ABOVE_CODEPOINTS),
        ),
        ContextualDeltaSpec(
            "gorgon_koronis",
            frozenset(SBMUFL_KORONIS_CODEPOINTS),
            frozenset(SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS),
        ),
        ContextualDeltaSpec(
            "fthora_koronis",
            frozenset(SBMUFL_KORONIS_CODEPOINTS),
            frozenset(SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS),
        ),
        ContextualDeltaSpec(
            "gorgon_fthora",
            frozenset(SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS),
            frozenset(SBMUFL_GORGON_PRIMARY_ABOVE_CODEPOINTS),
        ),
        ContextualDeltaSpec(
            "klasma_fthora",
            frozenset(SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS),
            frozenset(SBMUFL_KLASMA_ABOVE_CODEPOINTS),
        ),
        ContextualDeltaSpec(
            "secondary_gorgon_secondary_fthora",
            frozenset(SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS),
            frozenset(SBMUFL_GORGON_SECONDARY_ABOVE_CODEPOINTS),
        ),
    )


def contextual_target_specs() -> tuple[ContextualTargetSpec, ...]:
    return (
        ContextualTargetSpec(
            "ison",
            frozenset(SBMUFL_ISON_INDICATOR_CODEPOINTS),
        ),
        ContextualTargetSpec(
            "koronis",
            frozenset(SBMUFL_KORONIS_CODEPOINTS),
        ),
        ContextualTargetSpec(
            "primary_fthora",
            frozenset(SBMUFL_FTHORA_PRIMARY_ABOVE_CODEPOINTS),
        ),
        ContextualTargetSpec(
            "secondary_fthora",
            frozenset(SBMUFL_FTHORA_SECONDARY_ABOVE_CODEPOINTS),
        ),
    )


def validation_mark_source_specs() -> tuple[ValidationMarkSourceSpec, ...]:
    return (
        ValidationMarkSourceSpec(MarkSource.PRIMARY_GORGON, delta="gorgon_ison"),
        ValidationMarkSourceSpec(MarkSource.KLASMA, delta="klasma_ison"),
        ValidationMarkSourceSpec(MarkSource.KORONIS, target="koronis"),
        ValidationMarkSourceSpec(
            MarkSource.SECONDARY_GORGON,
            delta="secondary_gorgon_secondary_fthora",
        ),
        ValidationMarkSourceSpec(MarkSource.PRIMARY_FTHORA, delta="fthora_ison"),
        ValidationMarkSourceSpec(
            MarkSource.SECONDARY_FTHORA,
            delta="secondary_fthora_ison",
        ),
        ValidationMarkSourceSpec(
            MarkSource.TERTIARY_FTHORA,
            delta="tertiary_fthora_ison",
        ),
        ValidationMarkSourceSpec(MarkSource.KORONIS_KLASMA, delta="klasma_koronis"),
        ValidationMarkSourceSpec(MarkSource.KORONIS_GORGON, delta="gorgon_koronis"),
        ValidationMarkSourceSpec(MarkSource.KORONIS_FTHORA, delta="fthora_koronis"),
    )


def contextual_combined_profile_specs() -> tuple[CombinedProfileSpec, ...]:
    return (
        CombinedProfileSpec(
            "gorgon_combined",
            "gorgon_ison",
            "gorgon_fthora",
            "fthora_ison",
        ),
        CombinedProfileSpec(
            "klasma_combined",
            "klasma_ison",
            "klasma_fthora",
            "fthora_ison",
        ),
        CombinedProfileSpec(
            "secondary_combined",
            None,
            "secondary_gorgon_secondary_fthora",
            "secondary_fthora_ison",
        ),
        CombinedProfileSpec(
            "koronis_gorgon_combined",
            "gorgon_koronis",
            "gorgon_fthora",
            "fthora_koronis",
        ),
        CombinedProfileSpec(
            "koronis_klasma_combined",
            "klasma_koronis",
            "klasma_fthora",
            "fthora_koronis",
        ),
    )


def contextual_pair_profile_specs() -> tuple[PairProfileSpec, ...]:
    return (
        PairProfileSpec(
            "fthora_klasma_gorgon",
            "klasma_fthora",
            "gorgon_fthora",
        ),
        PairProfileSpec(
            "ison_klasma_gorgon",
            "klasma_ison",
            "gorgon_ison",
        ),
        PairProfileSpec(
            "koronis_klasma_gorgon",
            "klasma_koronis",
            "gorgon_koronis",
        ),
    )


def contextual_lookup_delta_group_specs() -> tuple[LookupDeltaGroupSpec, ...]:
    return (
        LookupDeltaGroupSpec(
            "primary_fthora",
            target="primary_fthora",
            label="fthora",
            profiles=("gorgon_fthora", "klasma_fthora"),
            pair_corrections=("fthora_klasma_gorgon",),
        ),
        LookupDeltaGroupSpec(
            "secondary_fthora",
            target="secondary_fthora",
            label="secondary fthora",
            profiles=("secondary_gorgon_secondary_fthora",),
        ),
        LookupDeltaGroupSpec(
            "ison",
            target="ison",
            label="ison",
            profiles=(
                "gorgon_ison",
                "klasma_ison",
                "fthora_ison",
                "secondary_fthora_ison",
                "tertiary_fthora_ison",
            ),
            corrections=(
                "gorgon_combined",
                "klasma_combined",
                "secondary_combined",
            ),
            pair_corrections=("ison_klasma_gorgon",),
        ),
        LookupDeltaGroupSpec(
            "koronis",
            target="koronis",
            label="koronis",
            profiles=(
                "klasma_koronis",
                "gorgon_koronis",
                "fthora_koronis",
            ),
            corrections=(
                "koronis_gorgon_combined",
                "koronis_klasma_combined",
            ),
            pair_corrections=("koronis_klasma_gorgon",),
        ),
    )


def contextual_mark_filter_specs() -> tuple[MarkFilterSpec, ...]:
    return (
        MarkFilterSpec("fthora_gorgon", ("gorgon_ison",), "primary_fthora"),
        MarkFilterSpec("fthora_klasma", ("klasma_ison",), "primary_fthora"),
        MarkFilterSpec(
            "fthora_klasma_gorgon_correction",
            ("klasma_ison", "gorgon_ison"),
            "primary_fthora",
        ),
        MarkFilterSpec(
            "secondary_fthora_secondary_gorgon",
            ("secondary_gorgon_secondary_fthora",),
            "secondary_fthora",
        ),
        MarkFilterSpec("ison_gorgon", ("gorgon_ison",), "ison"),
        MarkFilterSpec("ison_klasma", ("klasma_ison",), "ison"),
        MarkFilterSpec(
            "ison_klasma_gorgon_correction",
            ("klasma_ison", "gorgon_ison"),
            "ison",
        ),
        MarkFilterSpec("ison_fthora", ("fthora_ison",), "ison"),
        MarkFilterSpec(
            "ison_secondary_fthora",
            ("secondary_fthora_ison",),
            "ison",
        ),
        MarkFilterSpec(
            "ison_tertiary_fthora",
            ("tertiary_fthora_ison",),
            "ison",
        ),
        MarkFilterSpec(
            "ison_gorgon_correction",
            ("gorgon_ison", "fthora_ison"),
            "ison",
        ),
        MarkFilterSpec(
            "ison_klasma_correction",
            ("klasma_ison", "fthora_ison"),
            "ison",
        ),
        MarkFilterSpec(
            "ison_secondary_fthora_correction",
            ("secondary_gorgon_secondary_fthora", "secondary_fthora_ison"),
            "ison",
        ),
        MarkFilterSpec("koronis_klasma", ("klasma_ison",), "koronis"),
        MarkFilterSpec("koronis_gorgon", ("gorgon_ison",), "koronis"),
        MarkFilterSpec(
            "koronis_klasma_gorgon_correction",
            ("klasma_ison", "gorgon_ison"),
            "koronis",
        ),
        MarkFilterSpec("koronis_fthora", ("fthora_ison",), "koronis"),
        MarkFilterSpec(
            "koronis_klasma_correction",
            ("klasma_ison", "fthora_ison"),
            "koronis",
        ),
        MarkFilterSpec(
            "koronis_gorgon_correction",
            ("gorgon_ison", "fthora_ison"),
            "koronis",
        ),
    )


def contextual_lookup_specs() -> tuple[ContextLookupSpec, ...]:
    return (
        ContextLookupSpec(
            "fthora_gorgon",
            ContextLookupKind.SIMPLE,
            "gorgon_fthora",
            "primary_fthora",
            "primary_fthora",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "fthora_klasma",
            ContextLookupKind.SIMPLE,
            "klasma_fthora",
            "primary_fthora",
            "primary_fthora",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "secondary_fthora_secondary_gorgon",
            ContextLookupKind.SIMPLE,
            "secondary_gorgon_secondary_fthora",
            "secondary_fthora",
            "secondary_fthora",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "ison_gorgon",
            ContextLookupKind.SIMPLE,
            "gorgon_ison",
            "ison",
            "ison",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "ison_klasma",
            ContextLookupKind.SIMPLE,
            "klasma_ison",
            "ison",
            "ison",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "ison_fthora",
            ContextLookupKind.SIMPLE,
            "fthora_ison",
            "ison",
            "ison",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "ison_secondary_fthora",
            ContextLookupKind.SIMPLE,
            "secondary_fthora_ison",
            "ison",
            "ison",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "ison_tertiary_fthora",
            ContextLookupKind.SIMPLE,
            "tertiary_fthora_ison",
            "ison",
            "ison",
            ContextRuleBuilderKey.SINGLE_AXIS,
        ),
        ContextLookupSpec(
            "ison_gorgon_correction",
            ContextLookupKind.COMBINED,
            "gorgon_combined",
            "ison",
            "ison",
            ContextRuleBuilderKey.COMBINED_CORRECTION,
        ),
        ContextLookupSpec(
            "ison_klasma_correction",
            ContextLookupKind.COMBINED,
            "klasma_combined",
            "ison",
            "ison",
            ContextRuleBuilderKey.COMBINED_CORRECTION,
        ),
        ContextLookupSpec(
            "ison_secondary_fthora_correction",
            ContextLookupKind.COMBINED,
            "secondary_combined",
            "ison",
            "ison",
            ContextRuleBuilderKey.COMBINED_CORRECTION,
        ),
        ContextLookupSpec(
            "fthora_klasma_gorgon_correction",
            ContextLookupKind.PAIR,
            "fthora_klasma_gorgon",
            "primary_fthora",
            "primary_fthora",
            ContextRuleBuilderKey.PAIR_MAX_CORRECTION,
        ),
        ContextLookupSpec(
            "ison_klasma_gorgon_correction",
            ContextLookupKind.PAIR,
            "ison_klasma_gorgon",
            "ison",
            "ison",
            ContextRuleBuilderKey.PAIR_MAX_CORRECTION,
        ),
        ContextLookupSpec(
            "koronis_klasma",
            ContextLookupKind.SIMPLE,
            "klasma_koronis",
            "koronis",
            "koronis",
            ContextRuleBuilderKey.KORONIS_BEFORE_TARGET,
        ),
        ContextLookupSpec(
            "koronis_gorgon",
            ContextLookupKind.SIMPLE,
            "gorgon_koronis",
            "koronis",
            "koronis",
            ContextRuleBuilderKey.KORONIS_AFTER_TARGET,
        ),
        ContextLookupSpec(
            "koronis_fthora",
            ContextLookupKind.SIMPLE,
            "fthora_koronis",
            "koronis",
            "koronis",
            ContextRuleBuilderKey.KORONIS_AFTER_TARGET,
        ),
        ContextLookupSpec(
            "koronis_klasma_correction",
            ContextLookupKind.COMBINED,
            "koronis_klasma_combined",
            "koronis",
            "koronis",
            ContextRuleBuilderKey.KORONIS_DEPENDENCY_BEFORE_TARGET,
        ),
        ContextLookupSpec(
            "koronis_gorgon_correction",
            ContextLookupKind.COMBINED,
            "koronis_gorgon_combined",
            "koronis",
            "koronis",
            ContextRuleBuilderKey.KORONIS_DEPENDENCY_AFTER_TARGET,
        ),
        ContextLookupSpec(
            "koronis_klasma_gorgon_correction",
            ContextLookupKind.PAIR,
            "koronis_klasma_gorgon",
            "koronis",
            "koronis",
            ContextRuleBuilderKey.KORONIS_PAIR_MAX_CORRECTION,
        ),
    )


def contextual_delta_field_names() -> set[str]:
    return {field.name for field in fields(ContextualDeltas)}


def validate_contextual_spec_consistency() -> None:
    problems = []
    delta_names = {spec.name for spec in contextual_delta_specs()}
    delta_field_names = contextual_delta_field_names()
    target_names = {spec.name for spec in contextual_target_specs()}
    combined_profile_names = {spec.name for spec in contextual_combined_profile_specs()}
    pair_profile_names = {spec.name for spec in contextual_pair_profile_specs()}
    lookup_group_names = {spec.name for spec in contextual_lookup_delta_group_specs()}
    lookup_names = {spec.name for spec in contextual_lookup_specs()}
    mark_filter_names = {spec.name for spec in contextual_mark_filter_specs()}
    rule_builder_keys = set(context_rule_builders())

    for name in sorted(delta_names - delta_field_names):
        problems.append(f"contextual delta spec {name!r} has no ContextualDeltas field")
    for name in sorted(delta_field_names - delta_names):
        problems.append(f"ContextualDeltas field {name!r} has no delta spec")

    if mark_filter_names != lookup_names:
        for name in sorted(mark_filter_names - lookup_names):
            problems.append(f"mark filter {name!r} has no context lookup")
        for name in sorted(lookup_names - mark_filter_names):
            problems.append(f"context lookup {name!r} has no mark filter")

    for lookup_spec in contextual_lookup_specs():
        if lookup_spec.lookup_group not in lookup_group_names:
            problems.append(
                f"context lookup {lookup_spec.name!r} references unknown lookup group "
                f"{lookup_spec.lookup_group!r}"
            )
        if lookup_spec.rule_builder not in rule_builder_keys:
            problems.append(
                f"context lookup {lookup_spec.name!r} references unknown rule builder "
                f"{lookup_spec.rule_builder!r}"
            )

        if lookup_spec.kind is ContextLookupKind.SIMPLE:
            valid_profiles = delta_names
            profile_kind = "simple"
        elif lookup_spec.kind is ContextLookupKind.COMBINED:
            valid_profiles = combined_profile_names
            profile_kind = "combined"
        elif lookup_spec.kind is ContextLookupKind.PAIR:
            valid_profiles = pair_profile_names
            profile_kind = "pair"
        else:
            problems.append(
                f"context lookup {lookup_spec.name!r} has unknown kind "
                f"{lookup_spec.kind}"
            )
            continue

        if lookup_spec.profile not in valid_profiles:
            problems.append(
                f"context lookup {lookup_spec.name!r} references unknown "
                f"{profile_kind} profile {lookup_spec.profile!r}"
            )

    for lookup_group_spec in contextual_lookup_delta_group_specs():
        if lookup_group_spec.target not in target_names:
            problems.append(
                f"lookup group {lookup_group_spec.name!r} references unknown target "
                f"{lookup_group_spec.target!r}"
            )
        for name in lookup_group_spec.profiles:
            if name not in delta_names:
                problems.append(
                    f"lookup group {lookup_group_spec.name!r} references unknown "
                    f"simple profile {name!r}"
                )
        for name in lookup_group_spec.corrections:
            if name not in combined_profile_names:
                problems.append(
                    f"lookup group {lookup_group_spec.name!r} references unknown "
                    f"combined profile {name!r}"
                )
        for name in lookup_group_spec.pair_corrections:
            if name not in pair_profile_names:
                problems.append(
                    f"lookup group {lookup_group_spec.name!r} references unknown "
                    f"pair profile {name!r}"
                )

    for mark_source_spec in validation_mark_source_specs():
        if (
            mark_source_spec.delta is not None
            and mark_source_spec.delta not in delta_field_names
        ):
            problems.append(
                f"validation mark source {mark_source_spec.source.name} references "
                f"unknown ContextualDeltas field {mark_source_spec.delta!r}"
            )
        if (
            mark_source_spec.target is not None
            and mark_source_spec.target not in target_names
        ):
            problems.append(
                f"validation mark source {mark_source_spec.source.name} references "
                f"unknown target {mark_source_spec.target!r}"
            )

    for group in contextual_probe_spec_groups():
        for probe_spec in group.specs:
            mark_delta_keys_by_role = {}
            for mark_spec in probe_spec.marks:
                delta_keys = set()
                for delta_key, delta_name in mark_spec.deltas:
                    delta_keys.add(delta_key)
                    if delta_name not in delta_field_names:
                        problems.append(
                            f"probe {probe_spec.label!r} in group {group.name!r} "
                            f"references unknown ContextualDeltas field "
                            f"{delta_name!r}"
                        )
                mark_delta_keys_by_role[mark_spec.role] = delta_keys

            for delta_ref in (
                probe_spec.expected.max_refs + probe_spec.expected.add_refs
            ):
                if delta_ref.role not in mark_delta_keys_by_role:
                    problems.append(
                        f"probe {probe_spec.label!r} in group {group.name!r} "
                        f"expects unknown role {delta_ref.role!r}"
                    )
                    continue
                if delta_ref.key not in mark_delta_keys_by_role[delta_ref.role]:
                    problems.append(
                        f"probe {probe_spec.label!r} in group {group.name!r} "
                        f"expects missing delta key {delta_ref.key!r} on role "
                        f"{delta_ref.role!r}"
                    )

    if problems:
        raise ValueError(
            "contextual spec consistency errors:\n  - " + "\n  - ".join(problems)
        )


class MismatchCollector:
    def __init__(self, labels: Iterable[str], limit: int = 10) -> None:
        self.limit = limit
        self.by_label: dict[str, list[str]] = {label: [] for label in labels}

    def check(
        self,
        label: str,
        context: str,
        actual: int | None,
        expected: int,
    ) -> None:
        mismatches = self.by_label[label]
        if actual != expected and len(mismatches) < self.limit:
            mismatches.append(f"{context}: actual={actual}, expected={expected}")


@dataclass(frozen=True)
class ProbeValue:
    name: str
    codepoint: int
    glyph_name: str
    deltas: dict[str, int]


def glyph_codepoints(glyphs: GlyphIntrospector) -> dict[str, int]:
    return {glyph_name: codepoint for codepoint, glyph_name in glyphs.cmap.items()}


def table_size(ttfont: TTFont, tag: str) -> int:
    reader = ttfont.reader
    if reader is not None and tag in reader.tables:
        entry = reader.tables[tag]
        return entry.length
    if tag not in ttfont:
        return 0
    return len(ttfont[tag].compile(ttfont))


def gpos_lookup_count(ttfont: TTFont) -> int:
    if "GPOS" not in ttfont:
        return 0
    lookup_list = ttfont["GPOS"].table.LookupList
    if lookup_list is None:
        return 0
    return lookup_list.LookupCount


def value_record(delta_y: int) -> ValueRecord:
    value = ValueRecord()
    value.YPlacement = delta_y
    return value


def ensure_mark_glyph_sets(ttfont: TTFont) -> otTables.MarkGlyphSetsDef:
    gdef = ttfont["GDEF"].table
    if not hasattr(gdef, "MarkGlyphSetsDef"):
        gdef.MarkGlyphSetsDef = None
    if gdef.MarkGlyphSetsDef is None:
        gdef.MarkGlyphSetsDef = otTables.MarkGlyphSetsDef()
        gdef.MarkGlyphSetsDef.Format = 1
        gdef.MarkGlyphSetsDef.Coverage = []
        gdef.MarkGlyphSetsDef.MarkSetTableFormat = 1
        gdef.MarkGlyphSetsDef.MarkSetCount = 0
    if gdef.Version < 0x00010002:
        gdef.Version = 0x00010002
    return gdef.MarkGlyphSetsDef


def add_mark_filter_set(ttfont: TTFont, glyph_names: Iterable[str]) -> int:
    mark_sets = ensure_mark_glyph_sets(ttfont)
    coverage = buildCoverage(sorted(set(glyph_names)), ttfont.getReverseGlyphMap())
    mark_sets.Coverage.append(coverage)
    mark_sets.MarkSetCount = len(mark_sets.Coverage)
    return mark_sets.MarkSetCount - 1


def profile_groups(
    base_names: Iterable[str],
    profile_by_base: Mapping[str, Profile],
) -> dict[Profile, list[str]]:
    groups: dict[Profile, list[str]] = defaultdict(list)
    for base_name in base_names:
        groups[profile_by_base[base_name]].append(base_name)
    return groups


def target_anchor_context_deltas(
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
    target_codepoints: set[int],
    context_codepoints: set[int],
    expected_y_by_name: dict[str, int] | None = None,
) -> AxisDeltas:
    encoded_targets = glyphs.encoded_glyph_names(target_codepoints)
    target_anchors = gpos.mark_attachment_anchors(encoded_targets)
    if expected_y_by_name is None:
        expected_y_by_name = target_anchors.base_anchor_y_by_name

    context_marks = glyphs.encoded_glyph_names(context_codepoints)
    context_mark_positions = gpos.mark_to_base_mark_anchor_positions(context_marks)
    context_mark_classes, conflicting_mark_anchors = (
        contextual_positioning.context_mark_classes_by_name(context_mark_positions)
    )
    if conflicting_mark_anchors:
        raise ValueError(
            "conflicting mark anchors: " + "; ".join(conflicting_mark_anchors)
        )

    context_base_positions = gpos.mark_to_base_base_anchor_positions(
        {mark_class for mark_class, _y in context_mark_classes.values()}
    )
    context_ymax_by_name, missing_bounds = contextual_positioning.glyph_ymax_by_name(
        glyphs,
        context_marks,
    )
    if missing_bounds:
        raise ValueError("missing glyph bounds: " + ", ".join(missing_bounds))

    expected = contextual_positioning.expected_contextual_deltas(
        target_anchors.base_anchor_positions,
        expected_y_by_name,
        context_base_positions,
        context_mark_classes,
        context_ymax_by_name,
        (context_marks,),
    )
    return {
        (base_name, context_names[0]): delta
        for (base_name, context_names), delta in expected.items()
        if len(context_names) == 1
    }


def ison_expected_y_by_name(
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
) -> dict[str, int]:
    encoded_ison_indicators = glyphs.encoded_glyph_names(
        SBMUFL_ISON_INDICATOR_CODEPOINTS
    )
    anchors = gpos.mark_attachment_anchors(encoded_ison_indicators)
    reference_positions = anchors.base_anchor_positions["ison"]
    reference_y = next(iter({y for _mark_class, _x, y in reference_positions}))
    glyph_ymax_by_name, missing_bounds = contextual_positioning.glyph_ymax_by_name(
        glyphs,
        set(anchors.base_anchor_positions),
    )
    if missing_bounds:
        raise ValueError("missing ison base bounds: " + ", ".join(missing_bounds))

    compromise_glyph_names = glyphs.encoded_glyph_names(
        set(SBMUFL_ISON_INDICATOR_COMPROMISE_CODEPOINTS)
    )
    return ison.expected_base_y_by_name(
        reference_y,
        glyph_ymax_by_name,
        compromise_glyph_names,
    )


def normalize_ison_base_anchor_y(
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
) -> bool:
    encoded_ison_indicators = glyphs.encoded_glyph_names(
        SBMUFL_ISON_INDICATOR_CODEPOINTS
    )
    anchors = gpos.mark_attachment_anchors(encoded_ison_indicators)
    expected_y_by_name = ison_expected_y_by_name(glyphs, gpos)

    changed = False
    for subtable_index, subtable in gpos.mark_to_base_subtables():
        ison_classes = [
            mark_class
            for class_subtable_index, mark_class in anchors.mark_classes
            if class_subtable_index == subtable_index
        ]
        if not ison_classes:
            continue

        for glyph_name, base_record in zip(
            subtable.BaseCoverage.glyphs,
            subtable.BaseArray.BaseRecord,
            strict=True,
        ):
            expected_y = expected_y_by_name.get(glyph_name)
            if expected_y is None:
                continue

            for mark_class in ison_classes:
                if mark_class >= len(base_record.BaseAnchor):
                    continue

                anchor = base_record.BaseAnchor[mark_class]
                if anchor is not None and anchor.YCoordinate != expected_y:
                    anchor.YCoordinate = expected_y
                    changed = True

    return changed


def collect_contextual_deltas(
    glyphs: GlyphIntrospector,
    gpos: GposIntrospector,
) -> ContextualDeltas:
    expected_ison_y = ison_expected_y_by_name(glyphs, gpos)
    delta_by_name = {
        spec.name: target_anchor_context_deltas(
            glyphs,
            gpos,
            set(spec.target_codepoints),
            set(spec.context_codepoints),
            expected_ison_y if spec.expected_y == "ison" else None,
        )
        for spec in contextual_delta_specs()
    }
    return ContextualDeltas.from_mapping(delta_by_name)


def collect_contextual_targets(
    glyphs: GlyphIntrospector,
    deltas: ContextualDeltas,
) -> ContextualTargets:
    codepoint_by_glyph = glyph_codepoints(glyphs)
    target_by_name = {
        spec.name: sorted(glyphs.encoded_glyph_names(set(spec.codepoints)))
        for spec in contextual_target_specs()
    }
    base_names = sorted(
        base_name
        for base_name in deltas.bases_with_context()
        if codepoint_by_glyph.get(base_name) is not None
    )
    return ContextualTargets.from_mapping(target_by_name, base_names=base_names)


def append_lookup(ttfont: TTFont, lookup: Any, *, feature: str | None) -> Any:
    gpos = ttfont["GPOS"].table
    lookup_list = gpos.LookupList
    lookup.lookup_index = len(lookup_list.Lookup)
    lookup_list.Lookup.append(lookup)
    lookup_list.LookupCount = len(lookup_list.Lookup)

    if feature is not None:
        feature_found = False
        for feature_record in gpos.FeatureList.FeatureRecord:
            if feature_record.FeatureTag != feature:
                continue
            feature_found = True
            feature_record.Feature.LookupListIndex.append(lookup.lookup_index)
            feature_record.Feature.LookupCount = len(
                feature_record.Feature.LookupListIndex
            )
        if not feature_found:
            raise ValueError(f"GPOS feature {feature!r} not found")
    return lookup


def add_single_pos_lookups(
    ttfont: TTFont,
    glyph_names: Iterable[str],
    deltas: Iterable[int],
    label: str,
) -> LookupDict:
    lookups: LookupDict = {}
    for delta_y in sorted(delta for delta in set(deltas) if delta != 0):
        builder = SinglePosBuilder(ttfont, f"contextual {label} {delta_y:+d}")
        for glyph_name in glyph_names:
            builder.add_pos(None, glyph_name, value_record(delta_y))
        lookups[delta_y] = append_lookup(ttfont, builder.build(), feature=None)
    return lookups


def force_format2_lookup(builder: ChainContextPosBuilder) -> object:
    subtables = []
    for ruleset in builder.rulesets():
        classdefs = ruleset.format2ClassDefs()
        if not classdefs:
            raise ValueError(f"{builder.location}: cannot be represented as Format 2")
        subtables.append(
            builder.buildFormat2Subtable(ruleset, classdefs, chaining=True)
        )
    return builder.buildLookup_(subtables)


def add_context_lookup(
    ttfont: TTFont,
    name: str,
    mark_filter_set: int,
    grouped_rules: Iterable[tuple[list[str], list[ChainContextualRule]]],
) -> Any:
    builder = ChainContextPosBuilder(ttfont, f"contextual {name}")
    builder.markFilterSet = mark_filter_set
    first_group = True
    for _base_names, rules in grouped_rules:
        if not rules:
            continue
        if not first_group:
            builder.add_subtable_break(None)
        first_group = False
        builder.rules.extend(rules)
    lookup = force_format2_lookup(builder)
    return append_lookup(ttfont, lookup, feature="mark")


def bucket_simple_profile(
    profile: SimpleProfile,
    *,
    skip_zero_delta: bool = False,
) -> dict[int, list[str]]:
    marks_by_delta: dict[int, list[str]] = defaultdict(list)
    for mark_name, delta_y in profile:
        if skip_zero_delta and delta_y == 0:
            continue
        marks_by_delta[delta_y].append(mark_name)
    return marks_by_delta


def bucket_dependency_profile(
    profile: DependencyProfile,
) -> dict[tuple[int, int], list[str]]:
    marks_by_delta: dict[tuple[int, int], list[str]] = defaultdict(list)
    for mark_name, target_delta, raise_delta_y in profile:
        marks_by_delta[(target_delta, raise_delta_y)].append(mark_name)
    return marks_by_delta


def rule_for_delta(
    *,
    prefix: list[list[str]],
    targets: list[str],
    suffix: list[list[str]],
    delta_y: int,
    lookups_by_delta: LookupDict,
) -> ChainContextualRule:
    return ChainContextualRule(
        prefix=prefix,
        glyphs=[targets],
        suffix=suffix,
        lookups=[[lookups_by_delta[delta_y]]],
    )


def append_rule_for_nonzero_delta(
    rules: list[ChainContextualRule],
    *,
    prefix: list[list[str]],
    targets: list[str],
    suffix: list[list[str]],
    delta_y: int,
    lookups_by_delta: LookupDict,
) -> None:
    if delta_y == 0:
        return
    rules.append(
        rule_for_delta(
            prefix=prefix,
            targets=targets,
            suffix=suffix,
            delta_y=delta_y,
            lookups_by_delta=lookups_by_delta,
        )
    )


def rules_for_single_axis(
    bases: list[str],
    profile: SimpleProfile,
    targets: list[str],
    lookups_by_delta: LookupDict,
) -> list[ChainContextualRule]:
    return [
        rule_for_delta(
            prefix=[bases, sorted(mark_names)],
            targets=targets,
            suffix=[],
            delta_y=delta_y,
            lookups_by_delta=lookups_by_delta,
        )
        for delta_y, mark_names in sorted(
            bucket_simple_profile(profile, skip_zero_delta=True).items()
        )
    ]


def rules_for_combined_correction(
    bases: list[str],
    gorgon_profile: DependencyProfile,
    fthora_profile: SimpleProfile,
    targets: list[str],
    lookups_by_delta: LookupDict,
) -> list[ChainContextualRule]:
    rules: list[ChainContextualRule] = []
    for (g_delta, fthora_raise), gorgon_names in sorted(
        bucket_dependency_profile(gorgon_profile).items()
    ):
        for f_delta, fthora_names in sorted(
            bucket_simple_profile(fthora_profile).items()
        ):
            correction = fthora_raise - min(g_delta, f_delta)
            append_rule_for_nonzero_delta(
                rules,
                prefix=[bases, sorted(gorgon_names), sorted(fthora_names)],
                targets=targets,
                suffix=[],
                delta_y=correction,
                lookups_by_delta=lookups_by_delta,
            )
    return rules


def rules_for_pair_max_correction(
    bases: list[str],
    first_profile: SimpleProfile,
    second_profile: SimpleProfile,
    targets: list[str],
    lookups_by_delta: LookupDict,
) -> list[ChainContextualRule]:
    rules: list[ChainContextualRule] = []
    for first_delta, first_names in sorted(
        bucket_simple_profile(first_profile).items()
    ):
        for second_delta, second_names in sorted(
            bucket_simple_profile(second_profile).items()
        ):
            correction = -min(first_delta, second_delta)
            append_rule_for_nonzero_delta(
                rules,
                prefix=[bases, sorted(first_names), sorted(second_names)],
                targets=targets,
                suffix=[],
                delta_y=correction,
                lookups_by_delta=lookups_by_delta,
            )
    return rules


def rules_for_koronis_single_axis(
    bases: list[str],
    profile: SimpleProfile,
    targets: list[str],
    lookups_by_delta: LookupDict,
    *,
    before_target: bool,
) -> list[ChainContextualRule]:
    rules: list[ChainContextualRule] = []
    for delta_y, mark_names in sorted(
        bucket_simple_profile(profile, skip_zero_delta=True).items()
    ):
        mark_class = sorted(mark_names)
        prefix = [bases, mark_class] if before_target else [bases]
        suffix = [] if before_target else [mark_class]
        rules.append(
            rule_for_delta(
                prefix=prefix,
                targets=targets,
                suffix=suffix,
                delta_y=delta_y,
                lookups_by_delta=lookups_by_delta,
            )
        )
    return rules


def rules_for_koronis_pair_max_correction(
    bases: list[str],
    klasma_profile: SimpleProfile,
    gorgon_profile: SimpleProfile,
    targets: list[str],
    lookups_by_delta: LookupDict,
) -> list[ChainContextualRule]:
    rules: list[ChainContextualRule] = []
    for klasma_delta, klasma_names in sorted(
        bucket_simple_profile(klasma_profile).items()
    ):
        for gorgon_delta, gorgon_names in sorted(
            bucket_simple_profile(gorgon_profile).items()
        ):
            correction = -min(klasma_delta, gorgon_delta)
            append_rule_for_nonzero_delta(
                rules,
                prefix=[bases, sorted(klasma_names)],
                targets=targets,
                suffix=[sorted(gorgon_names)],
                delta_y=correction,
                lookups_by_delta=lookups_by_delta,
            )
    return rules


def rules_for_koronis_combined_correction(
    bases: list[str],
    dependency_profile: DependencyProfile,
    fthora_profile: SimpleProfile,
    targets: list[str],
    lookups_by_delta: LookupDict,
    *,
    dependency_before_target: bool,
) -> list[ChainContextualRule]:
    rules: list[ChainContextualRule] = []
    for (target_delta, fthora_raise), dependency_names in sorted(
        bucket_dependency_profile(dependency_profile).items()
    ):
        for f_delta, fthora_names in sorted(
            bucket_simple_profile(fthora_profile).items()
        ):
            correction = fthora_raise - min(target_delta, f_delta)
            dependency_class = sorted(dependency_names)
            fthora_class = sorted(fthora_names)
            prefix = [bases, dependency_class] if dependency_before_target else [bases]
            suffix = (
                [fthora_class]
                if dependency_before_target
                else [dependency_class, fthora_class]
            )
            append_rule_for_nonzero_delta(
                rules,
                prefix=prefix,
                targets=targets,
                suffix=suffix,
                delta_y=correction,
                lookups_by_delta=lookups_by_delta,
            )
    return rules


def mark_names_for_base(deltas: AxisDeltas, base_name: str) -> list[str]:
    return sorted(
        mark_name
        for delta_base_name, mark_name in deltas
        if delta_base_name == base_name
    )


def add_simple_context_lookup(
    ttfont: TTFont,
    *,
    name: str,
    mark_filter_set: int,
    base_names: list[str],
    profiles: SimpleProfileMap,
    targets: list[str],
    lookups_by_delta: LookupDict,
    rule_builder: SimpleRuleBuilder,
) -> Any:
    return add_context_lookup(
        ttfont,
        name,
        mark_filter_set,
        (
            (
                bases,
                rule_builder.build(
                    bases,
                    profile,
                    targets,
                    lookups_by_delta,
                ),
            )
            for profile, bases in profile_groups(base_names, profiles).items()
        ),
    )


def add_combined_context_lookup(
    ttfont: TTFont,
    *,
    name: str,
    mark_filter_set: int,
    base_names: list[str],
    profiles: CombinedProfileMap,
    targets: list[str],
    lookups_by_delta: LookupDict,
    rule_builder: CombinedRuleBuilder,
) -> Any:
    return add_context_lookup(
        ttfont,
        name,
        mark_filter_set,
        (
            (
                bases,
                rule_builder.build(
                    bases,
                    dependency_profile,
                    fthora_profile,
                    targets,
                    lookups_by_delta,
                ),
            )
            for (dependency_profile, fthora_profile), bases in profile_groups(
                base_names,
                profiles,
            ).items()
        ),
    )


def add_pair_context_lookup(
    ttfont: TTFont,
    *,
    name: str,
    mark_filter_set: int,
    base_names: list[str],
    profiles: PairProfileMap,
    targets: list[str],
    lookups_by_delta: LookupDict,
    rule_builder: PairRuleBuilder,
) -> Any:
    return add_context_lookup(
        ttfont,
        name,
        mark_filter_set,
        (
            (
                bases,
                rule_builder.build(
                    bases,
                    first_profile,
                    second_profile,
                    targets,
                    lookups_by_delta,
                ),
            )
            for (first_profile, second_profile), bases in profile_groups(
                base_names,
                profiles,
            ).items()
        ),
    )


def profile_for_base(deltas: AxisDeltas, base_name: str) -> SimpleProfile:
    return tuple(
        sorted(
            (mark_name, delta)
            for (delta_base_name, mark_name), delta in deltas.items()
            if delta_base_name == base_name
        )
    )


def collect_simple_profiles(
    base_names: Iterable[str],
    deltas: ContextualDeltas,
) -> dict[str, SimpleProfileMap]:
    return {
        spec.name: {
            base_name: profile_for_base(getattr(deltas, spec.name), base_name)
            for base_name in base_names
        }
        for spec in contextual_delta_specs()
    }


def collect_combined_profiles(
    base_names: Iterable[str],
    deltas: ContextualDeltas,
    simple_profiles: Mapping[str, SimpleProfileMap],
) -> dict[str, CombinedProfileMap]:
    profiles: dict[str, CombinedProfileMap] = {}
    for spec in contextual_combined_profile_specs():
        target_deltas = (
            {key: 0 for key in getattr(deltas, spec.raised_mark_delta)}
            if spec.target_delta is None
            else getattr(deltas, spec.target_delta)
        )
        raised_mark_deltas = getattr(deltas, spec.raised_mark_delta)
        profiles[spec.name] = {
            base_name: (
                tuple(
                    (
                        mark_name,
                        target_deltas[(base_name, mark_name)],
                        raised_mark_deltas.get((base_name, mark_name), 0),
                    )
                    for mark_name in sorted(
                        mark_name
                        for delta_base_name, mark_name in target_deltas
                        if delta_base_name == base_name
                    )
                ),
                simple_profiles[spec.target_profile][base_name],
            )
            for base_name in base_names
        }
    return profiles


def collect_pair_profiles(
    base_names: Iterable[str],
    simple_profiles: Mapping[str, SimpleProfileMap],
) -> dict[str, PairProfileMap]:
    return {
        spec.name: {
            base_name: (
                simple_profiles[spec.first_profile][base_name],
                simple_profiles[spec.second_profile][base_name],
            )
            for base_name in base_names
        }
        for spec in contextual_pair_profile_specs()
    }


def lookup_group_deltas(
    spec: LookupDeltaGroupSpec,
    simple_profiles: Mapping[str, SimpleProfileMap],
    combined_profiles: Mapping[str, CombinedProfileMap],
    pair_profiles: Mapping[str, PairProfileMap],
) -> set[int]:
    return (
        {
            delta
            for name in spec.profiles
            for profile in simple_profiles[name].values()
            for _mark_name, delta in profile
        }
        | {
            raised_mark_delta - min(target_delta, fthora_delta)
            for name in spec.corrections
            for dependency_profile, fthora_profile in combined_profiles[name].values()
            for (
                _dependency_name,
                target_delta,
                raised_mark_delta,
            ) in dependency_profile
            for _fthora_name, fthora_delta in fthora_profile
        }
        | {
            -min(first_delta, second_delta)
            for name in spec.pair_corrections
            for first_profile, second_profile in pair_profiles[name].values()
            for _first_name, first_delta in first_profile
            for _second_name, second_delta in second_profile
        }
    )


def target_names_by_spec(targets: ContextualTargets) -> dict[str, list[str]]:
    return {
        spec.name: getattr(targets, spec.name) for spec in contextual_target_specs()
    }


def mark_groups_by_delta(deltas: ContextualDeltas) -> dict[str, set[str]]:
    return {
        spec.name: {mark_name for _base_name, mark_name in getattr(deltas, spec.name)}
        for spec in contextual_delta_specs()
    }


def add_lookup_groups(
    ttfont: TTFont,
    target_names: Mapping[str, list[str]],
    simple_profiles: Mapping[str, SimpleProfileMap],
    combined_profiles: Mapping[str, CombinedProfileMap],
    pair_profiles: Mapping[str, PairProfileMap],
) -> dict[str, LookupDict]:
    return {
        spec.name: add_single_pos_lookups(
            ttfont,
            target_names[spec.target],
            lookup_group_deltas(
                spec,
                simple_profiles,
                combined_profiles,
                pair_profiles,
            ),
            spec.label,
        )
        for spec in contextual_lookup_delta_group_specs()
    }


def add_mark_filters(
    ttfont: TTFont,
    target_names: Mapping[str, list[str]],
    mark_groups: Mapping[str, set[str]],
) -> dict[str, int]:
    filters = {}
    for spec in contextual_mark_filter_specs():
        glyph_names = set(target_names[spec.target])
        for mark_name in spec.marks:
            glyph_names.update(mark_groups[mark_name])
        filters[spec.name] = add_mark_filter_set(ttfont, glyph_names)
    return filters


def context_rule_builders() -> dict[ContextRuleBuilderKey, RuleBuilder]:
    return {
        ContextRuleBuilderKey.SINGLE_AXIS: SimpleRuleBuilder(rules_for_single_axis),
        ContextRuleBuilderKey.COMBINED_CORRECTION: CombinedRuleBuilder(
            rules_for_combined_correction
        ),
        ContextRuleBuilderKey.PAIR_MAX_CORRECTION: PairRuleBuilder(
            rules_for_pair_max_correction
        ),
        ContextRuleBuilderKey.KORONIS_BEFORE_TARGET: SimpleRuleBuilder(
            partial(
                rules_for_koronis_single_axis,
                before_target=True,
            )
        ),
        ContextRuleBuilderKey.KORONIS_AFTER_TARGET: SimpleRuleBuilder(
            partial(
                rules_for_koronis_single_axis,
                before_target=False,
            )
        ),
        ContextRuleBuilderKey.KORONIS_DEPENDENCY_BEFORE_TARGET: CombinedRuleBuilder(
            partial(
                rules_for_koronis_combined_correction,
                dependency_before_target=True,
            )
        ),
        ContextRuleBuilderKey.KORONIS_DEPENDENCY_AFTER_TARGET: CombinedRuleBuilder(
            partial(
                rules_for_koronis_combined_correction,
                dependency_before_target=False,
            )
        ),
        ContextRuleBuilderKey.KORONIS_PAIR_MAX_CORRECTION: PairRuleBuilder(
            rules_for_koronis_pair_max_correction
        ),
    }


def add_context_lookup_from_spec(
    ttfont: TTFont,
    spec: ContextLookupSpec,
    *,
    state: ContextualBuildState,
) -> Any:
    name = spec.name
    mark_filter_set = state.filters[spec.name]
    base_names = state.base_names
    targets = state.target_names[spec.target]
    lookups_by_delta = state.lookup_groups[spec.lookup_group]
    rule_builder = state.rule_builders[spec.rule_builder]
    if spec.kind is ContextLookupKind.SIMPLE:
        if not isinstance(rule_builder, SimpleRuleBuilder):
            raise TypeError(f"{spec.name} requires a simple rule builder")
        return add_simple_context_lookup(
            ttfont,
            name=name,
            mark_filter_set=mark_filter_set,
            base_names=base_names,
            profiles=state.simple_profiles[spec.profile],
            targets=targets,
            lookups_by_delta=lookups_by_delta,
            rule_builder=rule_builder,
        )
    if spec.kind is ContextLookupKind.COMBINED:
        if not isinstance(rule_builder, CombinedRuleBuilder):
            raise TypeError(f"{spec.name} requires a combined rule builder")
        return add_combined_context_lookup(
            ttfont,
            name=name,
            mark_filter_set=mark_filter_set,
            base_names=base_names,
            profiles=state.combined_profiles[spec.profile],
            targets=targets,
            lookups_by_delta=lookups_by_delta,
            rule_builder=rule_builder,
        )
    if spec.kind is ContextLookupKind.PAIR:
        if not isinstance(rule_builder, PairRuleBuilder):
            raise TypeError(f"{spec.name} requires a pair rule builder")
        return add_pair_context_lookup(
            ttfont,
            name=name,
            mark_filter_set=mark_filter_set,
            base_names=base_names,
            profiles=state.pair_profiles[spec.profile],
            targets=targets,
            lookups_by_delta=lookups_by_delta,
            rule_builder=rule_builder,
        )
    raise ValueError(f"unknown contextual lookup kind: {spec.kind}")


def add_filtered_additive_slice(
    ttfont: TTFont,
    *,
    targets: ContextualTargets,
    deltas: ContextualDeltas,
) -> dict[str, list[int]]:
    state = ContextualBuildState.create(ttfont, targets=targets, deltas=deltas)

    lookups = {
        spec.name: add_context_lookup_from_spec(
            ttfont,
            spec,
            state=state,
        )
        for spec in contextual_lookup_specs()
    }

    return {
        name: [subtable.Format for subtable in lookup.SubTable]
        for name, lookup in lookups.items()
    }


def iter_validation_contexts(
    targets: ContextualTargets,
    deltas: ContextualDeltas,
    codepoint_by_glyph: Mapping[str, int],
) -> Iterable[ValidationContext]:
    for base_name in targets.base_names:
        base_codepoint = codepoint_by_glyph.get(base_name)
        if base_codepoint is None:
            continue
        yield ValidationContext.build(
            base_name=base_name,
            base_codepoint=base_codepoint,
            targets=targets,
            deltas=deltas,
            codepoint_by_glyph=codepoint_by_glyph,
        )


def probe_mark_values(
    *,
    spec: ProbeMarkSpec,
    validation_context: ValidationContext,
    deltas: ContextualDeltas,
    codepoint_by_glyph: Mapping[str, int],
) -> list[ProbeValue]:
    mark_names = validation_context.mark_names(spec.mark_source)
    if spec.sample:
        mark_names = mark_names[:1]

    values = []
    for mark_name in mark_names:
        mark_codepoint = codepoint_by_glyph.get(mark_name)
        if mark_codepoint is None:
            continue
        values.append(
            ProbeValue(
                name=mark_name,
                codepoint=mark_codepoint,
                glyph_name=mark_name,
                deltas={
                    delta_key: getattr(deltas, delta_attr).get(
                        (validation_context.base_name, mark_name),
                        0,
                    )
                    for delta_key, delta_attr in spec.deltas
                },
            )
        )
    return values


def iter_probe_contexts(
    spec: ContextualProbeSpec,
    validation_context: ValidationContext,
    deltas: ContextualDeltas,
    codepoint_by_glyph: Mapping[str, int],
    ison_glyph: str,
    koronis_glyph: str,
) -> Iterable[dict[str, ProbeValue]]:
    contexts = [
        {
            "base": ProbeValue(
                validation_context.base_name,
                validation_context.base_codepoint,
                validation_context.base_name,
                {},
            ),
            "ison": ProbeValue(
                "ison",
                SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
                ison_glyph,
                {},
            ),
        }
    ]

    for mark_spec in spec.marks:
        next_contexts = []
        for value in probe_mark_values(
            spec=mark_spec,
            validation_context=validation_context,
            deltas=deltas,
            codepoint_by_glyph=codepoint_by_glyph,
        ):
            for context in contexts:
                next_context = dict(context)
                next_context[mark_spec.role] = value
                next_contexts.append(next_context)
        contexts = next_contexts
        if not contexts:
            return

    if spec.target == "koronis":
        for context in contexts:
            koronis = context["koronis"]
            context["koronis"] = ProbeValue(
                koronis.name,
                koronis.codepoint,
                koronis_glyph,
                koronis.deltas,
            )

    yield from contexts


def expected_probe_delta(
    spec: ContextualProbeSpec,
    context: Mapping[str, ProbeValue],
) -> int:
    expected = spec.expected.constant
    if spec.expected.max_refs:
        expected += max(
            context[delta_ref.role].deltas[delta_ref.key]
            for delta_ref in spec.expected.max_refs
        )
    expected += sum(
        context[delta_ref.role].deltas[delta_ref.key]
        for delta_ref in spec.expected.add_refs
    )
    return expected


def validate_contextual_probes(
    *,
    shaper: Shaper,
    validation_context: ValidationContext,
    deltas: ContextualDeltas,
    codepoint_by_glyph: Mapping[str, int],
    ison_glyph: str,
    koronis_glyph: str,
    mismatches: MismatchCollector,
    specs: Iterable[ContextualProbeSpec],
) -> None:
    for spec in specs:
        for context in iter_probe_contexts(
            spec,
            validation_context,
            deltas,
            codepoint_by_glyph,
            ison_glyph,
            koronis_glyph,
        ):
            target = context[spec.target]
            position = shaper.position_of_codepoints(
                [context[role].codepoint for role in spec.sequence],
                target.glyph_name,
            )
            base_position = shaper.position_of_codepoints(
                [validation_context.base_codepoint, target.codepoint],
                target.glyph_name,
            )
            actual = (
                None
                if position is None or base_position is None
                else position[1] - base_position[1]
            )
            mismatches.check(
                spec.label,
                " + ".join(context[role].name for role in spec.sequence),
                actual,
                expected_probe_delta(spec, context),
            )


def validate_contextual_shaping(
    shaped_font: TTFont,
    targets: ContextualTargets,
    deltas: ContextualDeltas,
) -> dict[str, list[str]]:
    shaped_glyphs = GlyphIntrospector(shaped_font)
    shaper = Shaper.from_ttfont(shaped_font)
    shaped_codepoint_by_glyph = glyph_codepoints(shaped_glyphs)
    ison_glyph = shaped_glyphs.cmap[SBMUFL_ISON_SHAPING_PROBE_CODEPOINT]
    koronis_glyph = shaped_glyphs.cmap[SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT]
    mismatches = MismatchCollector(mismatch_labels())
    probe_spec_groups = contextual_probe_spec_groups()

    for validation_context in iter_validation_contexts(
        targets,
        deltas,
        shaped_codepoint_by_glyph,
    ):
        for probe_group in probe_spec_groups:
            validate_contextual_probes(
                shaper=shaper,
                validation_context=validation_context,
                deltas=deltas,
                codepoint_by_glyph=shaped_codepoint_by_glyph,
                ison_glyph=ison_glyph,
                koronis_glyph=koronis_glyph,
                mismatches=mismatches,
                specs=probe_group.specs,
            )

    return mismatches.by_label


def build_contextual_font(
    font_path: Path,
    output_dir: Path = Path("/tmp"),
    output_prefix: str = "contextual-",
) -> FontGenerationResult:
    validate_contextual_spec_consistency()
    ttfont = TTFont(font_path)
    original_size = font_path.stat().st_size
    original_gpos_size = table_size(ttfont, "GPOS")
    original_lookup_count = gpos_lookup_count(ttfont)
    glyphs = GlyphIntrospector(ttfont)
    gpos = GposIntrospector(ttfont)
    normalize_ison_base_anchor_y(glyphs, gpos)
    deltas = collect_contextual_deltas(glyphs, gpos)
    targets = collect_contextual_targets(glyphs, deltas)

    formats = add_filtered_additive_slice(
        ttfont,
        targets=targets,
        deltas=deltas,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{output_prefix}{font_path.name}"
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        dir=output_dir,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_file.name)
    temp_file.close()

    if "head" in ttfont:
        ttfont.recalcTimestamp = False
        ttfont["head"].modified = ttfont["head"].created
    ttfont.save(temp_path)

    shaped_font = TTFont(temp_path)
    generated_size = temp_path.stat().st_size
    generated_gpos_size = table_size(shaped_font, "GPOS")
    generated_lookup_count = gpos_lookup_count(shaped_font)
    mismatches_by_label = validate_contextual_shaping(shaped_font, targets, deltas)

    result = FontGenerationResult(
        path=output_path,
        original_size=original_size,
        generated_size=generated_size,
        original_gpos_size=original_gpos_size,
        generated_gpos_size=generated_gpos_size,
        original_lookup_count=original_lookup_count,
        generated_lookup_count=generated_lookup_count,
        context_lookup_formats=formats,
        mismatches_by_label=mismatches_by_label,
    )
    failed = any(
        format_ != 2
        for lookup_formats in result.context_lookup_formats.values()
        for format_ in lookup_formats
    ) or any(result.mismatches_by_label[label] for label in mismatch_labels())
    shaped_font.close()
    if failed:
        temp_path.unlink()
    else:
        temp_path.replace(output_path)

    return result


def print_result(font_path: Path, result: FontGenerationResult) -> bool:
    print(font_path.name)
    print(
        "  GPOS lookups: "
        f"{result.original_lookup_count} -> {result.generated_lookup_count} "
        f"({result.generated_lookup_count - result.original_lookup_count:+d})"
    )
    print(
        "  GPOS size: "
        f"{result.original_gpos_size} -> {result.generated_gpos_size} "
        f"({result.generated_gpos_size - result.original_gpos_size:+d})"
    )

    failed = False
    for lookup_name, formats in sorted(result.context_lookup_formats.items()):
        print(f"  {lookup_name} formats: {formats}")
        if any(format_ != 2 for format_ in formats):
            failed = True

    for label in mismatch_labels():
        mismatches = result.mismatches_by_label[label]
        if not mismatches:
            print(f"  {label}: exact")
            continue

        failed = True
        print(f"  {label}: mismatch")
        for mismatch in mismatches:
            print(f"    {mismatch}")

    return failed


def format2_chain_context_lookup_count(font_path: Path) -> int:
    ttfont = TTFont(font_path)
    if "GPOS" not in ttfont:
        return 0

    lookup_list = ttfont["GPOS"].table.LookupList
    if lookup_list is None:
        return 0

    return sum(
        1
        for lookup in lookup_list.Lookup
        if (
            lookup.LookupType == otTables.ChainContextPos.LookupType
            and any(subtable.Format == 2 for subtable in lookup.SubTable)
        )
        or (
            lookup.LookupType == otTables.ExtensionPos.LookupType
            and any(
                subtable.ExtensionLookupType == otTables.ChainContextPos.LookupType
                and subtable.ExtSubTable.Format == 2
                for subtable in lookup.SubTable
            )
        )
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fonts", nargs="*", type=Path)
    args = parser.parse_args(argv)
    font_paths = args.fonts or sorted((REPO_ROOT / "fonts").glob("*.otf"))
    if not font_paths:
        print("No OTF fonts found.")
        return 2

    validate_contextual_spec_consistency()

    failed = False
    for font_path in font_paths:
        existing_lookup_count = format2_chain_context_lookup_count(font_path)
        if existing_lookup_count:
            print(
                f"{font_path.name}: already has {existing_lookup_count} "
                "additive contextual Format 2 lookups; skipping"
            )
            continue

        result = build_contextual_font(
            font_path,
            output_dir=font_path.parent,
            output_prefix="",
        )
        failed = print_result(font_path, result) or failed

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
