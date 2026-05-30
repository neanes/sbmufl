from __future__ import annotations

import math
from collections.abc import Iterable, Iterator, Mapping
from itertools import combinations, product
from typing import Any, cast

from ..constants import (
    SBMUFL_APOSTROFOS_SHAPING_PROBE_CODEPOINT,
    SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT,
    SBMUFL_DOUBLE_CHAMILI_SHAPING_PROBE_CODEPOINT,
    SBMUFL_ELAFRON_SHAPING_PROBE_CODEPOINT,
    SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
    SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT,
    SBMUFL_ISON_CONTEXTUAL_RAISE_GRID,
    SBMUFL_ISON_INDICATOR_CLEARANCE,
    SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
    SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
    SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
    SBMUFL_SECONDARY_FTHORA_SHAPING_PROBE_CODEPOINT,
    SBMUFL_SECONDARY_GORGON_SHAPING_PROBE_CODEPOINT,
    SBMUFL_TRIGORGON_SHAPING_PROBE_CODEPOINT,
)
from ..framework.glyphs import GlyphIntrospector
from ..framework.gpos import GposIntrospector, MarkClassRef, format_mark_class
from ..framework.shaping import Shaper

RaiseSubtable = tuple[int, Iterable[Any], set[str], list[set[str]], set[str]]


def glyph_ymax_by_name(
    glyphs: GlyphIntrospector, glyph_names: set[str]
) -> tuple[dict[str, float], list[str]]:
    ymax_by_name: dict[str, float] = {}
    missing_bounds: list[str] = []
    for glyph_name in sorted(glyph_names):
        glyph_ymax = glyphs.glyph_ymax(glyph_name)
        if glyph_ymax is None:
            missing_bounds.append(glyph_name)
        else:
            ymax_by_name[glyph_name] = glyph_ymax
    return ymax_by_name, missing_bounds


def context_mark_classes_by_name(
    context_mark_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]],
) -> tuple[dict[str, tuple[MarkClassRef, int]], list[str]]:
    mark_classes_by_name: dict[str, tuple[MarkClassRef, int]] = {}
    conflicting_mark_anchors: list[str] = []
    for glyph_name, positions in sorted(context_mark_positions.items()):
        mark_positions = {(mark_class, y) for mark_class, _, y in sorted(positions)}
        if len(mark_positions) != 1:
            formatted_positions = [
                f"{format_mark_class(mark_class)}, X={x}, Y={y}"
                for mark_class, x, y in sorted(positions)
            ]
            conflicting_mark_anchors.append(
                f"{glyph_name}: {', '.join(formatted_positions)}"
            )
            continue

        mark_class, y = next(iter(mark_positions))
        mark_classes_by_name[glyph_name] = (mark_class, y)

    return mark_classes_by_name, conflicting_mark_anchors


def contextual_mark_sequences(
    base_name: str,
    single_expected_shaping_deltas: Mapping[tuple[str, str], int],
    encoded_context_mark_groups: Iterable[set[str]],
) -> Iterator[tuple[str, ...]]:
    available_context_marks = {
        context_name
        for pair_base_name, context_name in single_expected_shaping_deltas
        if pair_base_name == base_name
    }
    context_groups = [
        sorted(context_group.intersection(available_context_marks))
        for context_group in encoded_context_mark_groups
    ]

    for group_count in range(1, len(context_groups) + 1):
        for group_combination in combinations(context_groups, group_count):
            if not all(group_combination):
                continue
            yield from product(*group_combination)


def expected_contextual_deltas(
    anchor_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]],
    expected_y_by_name: Mapping[str, int],
    context_base_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]],
    context_mark_classes: Mapping[str, tuple[MarkClassRef, int]],
    context_ymax_by_name: Mapping[str, float],
    encoded_context_mark_groups: Iterable[set[str]],
    clearance: int = SBMUFL_ISON_INDICATOR_CLEARANCE,
    grid: int = SBMUFL_ISON_CONTEXTUAL_RAISE_GRID,
) -> dict[tuple[str, tuple[str, ...]], int]:
    context_mark_groups = tuple(encoded_context_mark_groups)
    context_base_positions_by_name = {
        glyph_name: {mark_class: (x, y) for mark_class, x, y in positions}
        for glyph_name, positions in context_base_positions.items()
    }

    single_expected_shaping_deltas: dict[tuple[str, str], int] = {}
    expected_shaping_deltas: dict[tuple[str, tuple[str, ...]], int] = {}
    for base_name, _base_positions in sorted(anchor_positions.items()):
        if base_name not in expected_y_by_name:
            continue

        context_base_anchors = context_base_positions_by_name.get(base_name, {})
        for context_name, (
            context_mark_class,
            context_mark_y,
        ) in context_mark_classes.items():
            context_base_anchor = context_base_anchors.get(context_mark_class)
            if context_base_anchor is None or context_name not in context_ymax_by_name:
                continue

            _, context_base_y = context_base_anchor
            mark_top_y = (
                context_base_y - context_mark_y + context_ymax_by_name[context_name]
            )
            target_y = max(
                expected_y_by_name[base_name],
                math.ceil(mark_top_y + clearance),
            )
            delta_y = target_y - expected_y_by_name[base_name]
            if delta_y > 0:
                delta_y = math.ceil(delta_y / grid) * grid
            else:
                delta_y = 0
            single_expected_shaping_deltas[(base_name, context_name)] = delta_y

        for context_sequence in contextual_mark_sequences(
            base_name,
            single_expected_shaping_deltas,
            context_mark_groups,
        ):
            delta_y = max(
                single_expected_shaping_deltas[(base_name, context_name)]
                for context_name in context_sequence
            )
            expected_shaping_deltas[(base_name, context_sequence)] = delta_y

    return expected_shaping_deltas


def _append_position_problem(
    problems: list[str],
    label: str,
    position: tuple[int, int] | None,
) -> bool:
    if position is None:
        problems.append(f"{label}: did not shape")
        return True
    return False


def _expect_same_x_positive_y_raise(
    problems: list[str],
    *,
    label: str,
    target_label: str,
    base_position: tuple[int, int],
    actual_position: tuple[int, int],
) -> None:
    actual_delta = actual_position[1] - base_position[1]
    if actual_position[0] != base_position[0] or actual_delta <= 0:
        problems.append(
            f"{label}: shaped {target_label} offset X={actual_position[0]} "
            f"Y={actual_position[1]}; without context X={base_position[0]} "
            f"Y={base_position[1]}; expected same X and positive Y raise"
        )


def contextual_prompt_probe_problems(
    glyphs: GlyphIntrospector,
    shaper: Shaper,
) -> list[str]:
    problems: list[str] = []
    base_codepoint = glyphs.codepoint_for_glyph_name("ison")
    ison_glyph = glyphs.cmap.get(SBMUFL_ISON_SHAPING_PROBE_CODEPOINT)
    koronis_glyph = glyphs.cmap.get(SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT)
    fthora_glyph = glyphs.cmap.get(SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT)
    secondary_fthora_glyph = glyphs.cmap.get(
        SBMUFL_SECONDARY_FTHORA_SHAPING_PROBE_CODEPOINT
    )
    if (
        base_codepoint is None
        or ison_glyph is None
        or koronis_glyph is None
        or fthora_glyph is None
        or secondary_fthora_glyph is None
    ):
        return problems

    # These bases are the first glyphs in glyph order with the secondary
    # anchors needed by the concrete stack probes.
    secondary_gorgon_base = glyphs.codepoint_for_glyph_name("oligonIsonKentimata")
    secondary_fthora_base = glyphs.codepoint_for_glyph_name("runningElafron")

    base_ison = shaper.position_of_codepoints(
        [base_codepoint, SBMUFL_ISON_SHAPING_PROBE_CODEPOINT], ison_glyph
    )
    base_koronis = shaper.position_of_codepoints(
        [base_codepoint, SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT], koronis_glyph
    )
    base_fthora = shaper.position_of_codepoints(
        [base_codepoint, SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT], fthora_glyph
    )
    required_positions = {
        "base + ison": base_ison,
        "base + koronis": base_koronis,
        "base + fthora": base_fthora,
    }
    if any(
        _append_position_problem(problems, label, position)
        for label, position in required_positions.items()
    ):
        return problems

    assert base_ison is not None
    assert base_koronis is not None
    assert base_fthora is not None

    def check_pair_max_probe(
        *,
        label: str,
        base_name: str,
        target_codepoint: int,
        target_glyph: str,
        target_label: str,
        first_sequence: list[int],
        second_sequence: list[int],
        combined_sequence: list[int],
    ) -> None:
        probe_base_codepoint = glyphs.codepoint_for_glyph_name(base_name)
        if probe_base_codepoint is None:
            return

        base_position = shaper.position_of_codepoints(
            [probe_base_codepoint, target_codepoint],
            target_glyph,
        )
        first_position = shaper.position_of_codepoints(first_sequence, target_glyph)
        second_position = shaper.position_of_codepoints(second_sequence, target_glyph)
        combined_position = shaper.position_of_codepoints(
            combined_sequence,
            target_glyph,
        )
        for position_label, position in (
            (f"{label} base", base_position),
            (f"{label} first dependency", first_position),
            (f"{label} second dependency", second_position),
            (label, combined_position),
        ):
            if _append_position_problem(problems, position_label, position):
                return

        assert base_position is not None
        assert first_position is not None
        assert second_position is not None
        assert combined_position is not None
        first_delta = first_position[1] - base_position[1]
        second_delta = second_position[1] - base_position[1]
        expected_y = base_position[1] + max(first_delta, second_delta)
        if (
            combined_position[0] != base_position[0]
            or combined_position[1] != expected_y
        ):
            problems.append(
                f"{label}: shaped {target_label} offset X={combined_position[0]} "
                f"Y={combined_position[1]}; without context X={base_position[0]} "
                f"Y={base_position[1]}; expected X={base_position[0]} Y={expected_y}"
            )

    check_pair_max_probe(
        label="klasma + digorgon + ison",
        base_name="elafron",
        target_codepoint=SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        target_glyph=ison_glyph,
        target_label="ison",
        first_sequence=[
            SBMUFL_ELAFRON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
        second_sequence=[
            SBMUFL_ELAFRON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
        combined_sequence=[
            SBMUFL_ELAFRON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
    )
    check_pair_max_probe(
        label="klasma + digorgon + fthora",
        base_name="apostrofos",
        target_codepoint=SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        target_glyph=fthora_glyph,
        target_label="fthora",
        first_sequence=[
            SBMUFL_APOSTROFOS_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
        second_sequence=[
            SBMUFL_APOSTROFOS_SHAPING_PROBE_CODEPOINT,
            SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
        combined_sequence=[
            SBMUFL_APOSTROFOS_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
    )
    check_pair_max_probe(
        label="klasma + koronis + digorgon",
        base_name="doubleChamili",
        target_codepoint=SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
        target_glyph=koronis_glyph,
        target_label="koronis",
        first_sequence=[
            SBMUFL_DOUBLE_CHAMILI_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
        ],
        second_sequence=[
            SBMUFL_DOUBLE_CHAMILI_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
            SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT,
        ],
        combined_sequence=[
            SBMUFL_DOUBLE_CHAMILI_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
            SBMUFL_DIGORGON_SHAPING_PROBE_CODEPOINT,
        ],
    )

    fthora_ison = shaper.position_of_codepoints(
        [
            base_codepoint,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
        ison_glyph,
    )
    trigorgon_ison = shaper.position_of_codepoints(
        [
            base_codepoint,
            SBMUFL_TRIGORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
        ison_glyph,
    )
    if _append_position_problem(problems, "fthora + ison", fthora_ison):
        return problems
    if _append_position_problem(problems, "trigorgon + ison", trigorgon_ison):
        return problems
    assert fthora_ison is not None
    assert trigorgon_ison is not None

    _expect_same_x_positive_y_raise(
        problems,
        label="fthora + ison",
        target_label="ison",
        base_position=base_ison,
        actual_position=fthora_ison,
    )
    _expect_same_x_positive_y_raise(
        problems,
        label="trigorgon + ison",
        target_label="ison",
        base_position=base_ison,
        actual_position=trigorgon_ison,
    )

    fthora_raise_by_label: dict[str, int] = {}
    for label, dependency_codepoint in (
        ("klasma + fthora", SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT),
        ("gorgon + fthora", SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT),
    ):
        fthora_position = shaper.position_of_codepoints(
            [
                base_codepoint,
                dependency_codepoint,
                SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
            ],
            fthora_glyph,
        )
        if _append_position_problem(problems, label, fthora_position):
            continue
        assert fthora_position is not None
        fthora_raise_by_label[label] = fthora_position[1] - base_fthora[1]
        _expect_same_x_positive_y_raise(
            problems,
            label=label,
            target_label="fthora",
            base_position=base_fthora,
            actual_position=fthora_position,
        )

    if secondary_gorgon_base is not None:
        _check_secondary_gorgon_prompt_probes(
            problems,
            shaper,
            secondary_gorgon_base,
            SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_SECONDARY_GORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_SECONDARY_FTHORA_SHAPING_PROBE_CODEPOINT,
            fthora_glyph,
            ison_glyph,
            secondary_fthora_glyph,
        )

    koronis_gorgon_fthora = shaper.position_of_codepoints(
        [
            base_codepoint,
            SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
            SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
        fthora_glyph,
    )
    if not _append_position_problem(
        problems, "koronis + gorgon + primary fthora", koronis_gorgon_fthora
    ):
        assert koronis_gorgon_fthora is not None
        expected_y = base_fthora[1] + fthora_raise_by_label.get("gorgon + fthora", 0)
        if (
            koronis_gorgon_fthora[0] != base_fthora[0]
            or koronis_gorgon_fthora[1] != expected_y
        ):
            problems.append(
                "koronis + gorgon + primary fthora: shaped primary fthora "
                f"offset X={koronis_gorgon_fthora[0]} Y={koronis_gorgon_fthora[1]}; "
                f"without context X={base_fthora[0]} Y={base_fthora[1]}; "
                f"expected X={base_fthora[0]} Y={expected_y}"
            )

    fthora_ison_delta = fthora_ison[1] - base_ison[1]
    fthora_koronis = shaper.position_of_codepoints(
        [
            base_codepoint,
            SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
        koronis_glyph,
    )
    if _append_position_problem(problems, "fthora + koronis", fthora_koronis):
        return problems
    assert fthora_koronis is not None
    fthora_koronis_delta = fthora_koronis[1] - base_koronis[1]

    if secondary_fthora_base is not None:
        _check_secondary_fthora_prompt_probes(
            problems,
            shaper,
            secondary_fthora_base,
            SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT,
            SBMUFL_SECONDARY_FTHORA_SHAPING_PROBE_CODEPOINT,
            secondary_fthora_glyph,
            ison_glyph,
            koronis_glyph,
        )

    mixed_cases = [
        (
            "gorgon + fthora + ison",
            [
                base_codepoint,
                SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT,
                SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
                SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
            ],
            ison_glyph,
            base_ison,
            fthora_ison_delta,
            fthora_raise_by_label.get("gorgon + fthora"),
            "ison",
        ),
        (
            "gorgon + fthora + koronis",
            [
                base_codepoint,
                SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
                SBMUFL_GORGON_SHAPING_PROBE_CODEPOINT,
                SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
            ],
            koronis_glyph,
            base_koronis,
            fthora_koronis_delta,
            fthora_raise_by_label.get("gorgon + fthora"),
            "koronis",
        ),
        (
            "klasma + fthora + ison",
            [
                base_codepoint,
                SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
                SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
                SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
            ],
            ison_glyph,
            base_ison,
            fthora_ison_delta,
            fthora_raise_by_label.get("klasma + fthora"),
            "ison",
        ),
        (
            "klasma + fthora + koronis",
            [
                base_codepoint,
                SBMUFL_KLASMA_SHAPING_PROBE_CODEPOINT,
                SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
                SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
            ],
            koronis_glyph,
            base_koronis,
            fthora_koronis_delta,
            fthora_raise_by_label.get("klasma + fthora"),
            "koronis",
        ),
    ]
    for (
        label,
        sequence,
        target_glyph,
        base_position,
        fthora_target_delta,
        fthora_raise_delta,
        target_label,
    ) in mixed_cases:
        if fthora_raise_delta is None:
            continue
        mixed_position = shaper.position_of_codepoints(sequence, target_glyph)
        if _append_position_problem(problems, label, mixed_position):
            continue
        assert mixed_position is not None
        expected_y = base_position[1] + fthora_target_delta + fthora_raise_delta
        if mixed_position[0] != base_position[0] or mixed_position[1] != expected_y:
            problems.append(
                f"{label}: shaped {target_label} offset X={mixed_position[0]} "
                f"Y={mixed_position[1]}; without context X={base_position[0]} "
                f"Y={base_position[1]}; expected X={base_position[0]} Y={expected_y}"
            )

    return problems


def _check_secondary_gorgon_prompt_probes(
    problems: list[str],
    shaper: Shaper,
    secondary_gorgon_base: int,
    gorgon_codepoint: int,
    secondary_gorgon_codepoint: int,
    secondary_fthora_codepoint: int,
    fthora_glyph: str,
    ison_glyph: str,
    secondary_fthora_glyph: str,
) -> None:
    sg_base_fthora = shaper.position_of_codepoints(
        [secondary_gorgon_base, SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT],
        fthora_glyph,
    )
    sg_base_ison = shaper.position_of_codepoints(
        [secondary_gorgon_base, SBMUFL_ISON_SHAPING_PROBE_CODEPOINT],
        ison_glyph,
    )
    sg_gorgon_fthora = shaper.position_of_codepoints(
        [
            secondary_gorgon_base,
            gorgon_codepoint,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
        fthora_glyph,
    )
    sg_fthora_ison = shaper.position_of_codepoints(
        [
            secondary_gorgon_base,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
        ison_glyph,
    )
    required_positions = (
        ("secondary-gorgon base + fthora", sg_base_fthora),
        ("secondary-gorgon base + ison", sg_base_ison),
        ("secondary-gorgon gorgon + fthora", sg_gorgon_fthora),
        ("secondary-gorgon fthora + ison", sg_fthora_ison),
    )
    if any(
        _append_position_problem(problems, label, position)
        for label, position in required_positions
    ):
        return

    assert sg_base_fthora is not None
    assert sg_base_ison is not None
    assert sg_gorgon_fthora is not None
    assert sg_fthora_ison is not None
    sg_gorgon_fthora_raise = sg_gorgon_fthora[1] - sg_base_fthora[1]
    sg_fthora_ison_delta = sg_fthora_ison[1] - sg_base_ison[1]

    secondary_gorgon_fthora = shaper.position_of_codepoints(
        [
            secondary_gorgon_base,
            secondary_gorgon_codepoint,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
        fthora_glyph,
    )
    if not _append_position_problem(
        problems,
        "secondary gorgon + primary fthora",
        secondary_gorgon_fthora,
    ):
        assert secondary_gorgon_fthora is not None
        if secondary_gorgon_fthora != sg_base_fthora:
            problems.append(
                "secondary gorgon + primary fthora: shaped primary fthora "
                f"offset X={secondary_gorgon_fthora[0]} "
                f"Y={secondary_gorgon_fthora[1]}; without context "
                f"X={sg_base_fthora[0]} Y={sg_base_fthora[1]}; "
                "expected no raise"
            )

    primary_secondary_gorgon_fthora = shaper.position_of_codepoints(
        [
            secondary_gorgon_base,
            gorgon_codepoint,
            secondary_gorgon_codepoint,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
        ],
        fthora_glyph,
    )
    if not _append_position_problem(
        problems,
        "primary + secondary gorgon + primary fthora",
        primary_secondary_gorgon_fthora,
    ):
        assert primary_secondary_gorgon_fthora is not None
        expected_y = sg_base_fthora[1] + sg_gorgon_fthora_raise
        if (
            primary_secondary_gorgon_fthora[0] != sg_base_fthora[0]
            or primary_secondary_gorgon_fthora[1] != expected_y
        ):
            problems.append(
                "primary + secondary gorgon + primary fthora: shaped primary "
                f"fthora offset X={primary_secondary_gorgon_fthora[0]} "
                f"Y={primary_secondary_gorgon_fthora[1]}; without context "
                f"X={sg_base_fthora[0]} Y={sg_base_fthora[1]}; expected "
                f"X={sg_base_fthora[0]} Y={expected_y}"
            )

    primary_secondary_gorgon_fthora_ison = shaper.position_of_codepoints(
        [
            secondary_gorgon_base,
            gorgon_codepoint,
            secondary_gorgon_codepoint,
            SBMUFL_FTHORA_SHAPING_PROBE_CODEPOINT,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
        ison_glyph,
    )
    if not _append_position_problem(
        problems,
        "primary + secondary gorgon + primary fthora + ison",
        primary_secondary_gorgon_fthora_ison,
    ):
        assert primary_secondary_gorgon_fthora_ison is not None
        expected_y = sg_base_ison[1] + sg_fthora_ison_delta + sg_gorgon_fthora_raise
        if (
            primary_secondary_gorgon_fthora_ison[0] != sg_base_ison[0]
            or primary_secondary_gorgon_fthora_ison[1] != expected_y
        ):
            problems.append(
                "primary + secondary gorgon + primary fthora + ison: shaped "
                f"ison offset X={primary_secondary_gorgon_fthora_ison[0]} "
                f"Y={primary_secondary_gorgon_fthora_ison[1]}; without "
                f"context X={sg_base_ison[0]} Y={sg_base_ison[1]}; expected "
                f"X={sg_base_ison[0]} Y={expected_y}"
            )

    sg_base_secondary_fthora = shaper.position_of_codepoints(
        [secondary_gorgon_base, secondary_fthora_codepoint],
        secondary_fthora_glyph,
    )
    secondary_gorgon_secondary_fthora = shaper.position_of_codepoints(
        [
            secondary_gorgon_base,
            secondary_gorgon_codepoint,
            secondary_fthora_codepoint,
        ],
        secondary_fthora_glyph,
    )
    if any(
        _append_position_problem(problems, label, position)
        for label, position in (
            ("secondary-gorgon base + secondary fthora", sg_base_secondary_fthora),
            ("secondary gorgon + secondary fthora", secondary_gorgon_secondary_fthora),
        )
    ):
        return

    assert sg_base_secondary_fthora is not None
    assert secondary_gorgon_secondary_fthora is not None
    _expect_same_x_positive_y_raise(
        problems,
        label="secondary gorgon + secondary fthora",
        target_label="secondary fthora",
        base_position=sg_base_secondary_fthora,
        actual_position=secondary_gorgon_secondary_fthora,
    )


def _check_secondary_fthora_prompt_probes(
    problems: list[str],
    shaper: Shaper,
    secondary_fthora_base: int,
    gorgon_codepoint: int,
    secondary_fthora_codepoint: int,
    secondary_fthora_glyph: str,
    ison_glyph: str,
    koronis_glyph: str,
) -> None:
    base_secondary_fthora = shaper.position_of_codepoints(
        [secondary_fthora_base, secondary_fthora_codepoint],
        secondary_fthora_glyph,
    )
    secondary_fthora_ison = shaper.position_of_codepoints(
        [
            secondary_fthora_base,
            secondary_fthora_codepoint,
            SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
        ],
        ison_glyph,
    )
    secondary_fthora_koronis = shaper.position_of_codepoints(
        [
            secondary_fthora_base,
            SBMUFL_KORONIS_SHAPING_PROBE_CODEPOINT,
            secondary_fthora_codepoint,
        ],
        koronis_glyph,
    )
    if any(
        _append_position_problem(problems, label, position)
        for label, position in (
            ("secondary fthora + ison", secondary_fthora_ison),
            ("secondary fthora + koronis", secondary_fthora_koronis),
            ("secondary-fthora base + secondary fthora", base_secondary_fthora),
        )
    ):
        return

    assert base_secondary_fthora is not None
    secondary_fthora_position = shaper.position_of_codepoints(
        [
            secondary_fthora_base,
            gorgon_codepoint,
            secondary_fthora_codepoint,
        ],
        secondary_fthora_glyph,
    )
    label = "primary gorgon + secondary fthora"
    if _append_position_problem(problems, label, secondary_fthora_position):
        return
    assert secondary_fthora_position is not None
    if secondary_fthora_position != base_secondary_fthora:
        problems.append(
            f"{label}: shaped secondary fthora offset "
            f"X={secondary_fthora_position[0]} "
            f"Y={secondary_fthora_position[1]}; without context "
            f"X={base_secondary_fthora[0]} "
            f"Y={base_secondary_fthora[1]}; expected no raise"
        )


def _iter_ison_raise_subtables(
    gpos: GposIntrospector,
    encoded_ison_indicators: set[str],
    encoded_gorgon_above_marks: set[str],
) -> Iterator[RaiseSubtable]:
    for lookup_index, subtable in gpos.iter_chain_context_pos_subtables():
        for (
            pos_lookup_records,
            backtrack_coverages,
            input_coverages,
            lookahead_coverages,
        ) in _iter_chain_context_rules(subtable):
            if lookahead_coverages or len(input_coverages) != 1:
                continue
            if len(backtrack_coverages) < 2:
                continue

            base_glyphs = backtrack_coverages[0]
            gorgon_coverages = [
                coverage.intersection(encoded_gorgon_above_marks)
                for coverage in backtrack_coverages[1:]
            ]
            ison_glyphs = input_coverages[0]

            if not all(gorgon_coverages) or not ison_glyphs.intersection(
                encoded_ison_indicators
            ):
                continue

            yield lookup_index, pos_lookup_records, base_glyphs, gorgon_coverages, ison_glyphs


def _iter_target_first_raise_subtables(
    gpos: GposIntrospector,
    encoded_targets: set[str],
    encoded_context_marks: set[str],
) -> Iterator[RaiseSubtable]:
    for lookup_index, subtable in gpos.iter_chain_context_pos_subtables():
        for (
            pos_lookup_records,
            backtrack_coverages,
            input_coverages,
            lookahead_coverages,
        ) in _iter_chain_context_rules(subtable):
            if len(backtrack_coverages) != 1 or not input_coverages:
                continue

            base_glyphs = backtrack_coverages[0]
            target_glyphs = input_coverages[0]
            context_coverages = [
                coverage.intersection(encoded_context_marks)
                for coverage in (*input_coverages[1:], *lookahead_coverages)
            ]

            if not all(context_coverages) or not target_glyphs.intersection(
                encoded_targets
            ):
                continue

            yield (
                lookup_index,
                pos_lookup_records,
                base_glyphs,
                context_coverages,
                target_glyphs,
            )


def _iter_chain_context_rules(
    subtable: Any,
) -> Iterator[tuple[Iterable[Any], list[set[str]], list[set[str]], list[set[str]]]]:
    if subtable.Format == 3:
        # FontForge stores backtrack coverage nearest to the input first.
        yield (
            subtable.PosLookupRecord,
            [set(coverage.glyphs) for coverage in reversed(subtable.BacktrackCoverage)],
            [set(coverage.glyphs) for coverage in subtable.InputCoverage],
            [set(coverage.glyphs) for coverage in subtable.LookAheadCoverage],
        )
        return

    if subtable.Format != 2:
        return

    coverage_glyphs = set(subtable.Coverage.glyphs)
    for input_class, rule_set in enumerate(subtable.ChainPosClassSet):
        if rule_set is None:
            continue

        input_glyphs = _class_glyphs(
            subtable.InputClassDef,
            input_class,
            coverage_glyphs,
        )
        if not input_glyphs:
            continue

        for rule in rule_set.ChainPosClassRule:
            backtrack_coverages = [
                _class_glyphs(subtable.BacktrackClassDef, class_id)
                for class_id in reversed(rule.Backtrack)
            ]
            input_coverages = [
                input_glyphs,
                *(
                    _class_glyphs(subtable.InputClassDef, class_id)
                    for class_id in rule.Input
                ),
            ]
            lookahead_coverages = [
                _class_glyphs(subtable.LookAheadClassDef, class_id)
                for class_id in rule.LookAhead
            ]
            yield (
                rule.PosLookupRecord,
                backtrack_coverages,
                input_coverages,
                lookahead_coverages,
            )


def _class_glyphs(
    class_def: Any,
    class_id: int,
    coverage_glyphs: set[str] | None = None,
) -> set[str]:
    class_defs = class_def.classDefs if class_def is not None else {}
    if class_id == 0:
        if coverage_glyphs is None:
            return set()
        return coverage_glyphs - set(class_defs)

    glyphs = {
        glyph_name
        for glyph_name, glyph_class in class_defs.items()
        if glyph_class == class_id
    }
    if coverage_glyphs is not None:
        glyphs &= coverage_glyphs
    return glyphs


def contextual_ison_raise_rules(
    gpos: GposIntrospector,
    encoded_ison_indicators: set[str],
    encoded_gorgon_above_marks: set[str],
    target_label: str = "ison indicators",
) -> tuple[dict[tuple[str, tuple[str, ...]], int], list[str]]:
    return _contextual_raise_rules(
        gpos,
        encoded_ison_indicators,
        target_label,
        _iter_ison_raise_subtables(
            gpos,
            encoded_ison_indicators,
            encoded_gorgon_above_marks,
        ),
    )


def contextual_target_first_raise_rules(
    gpos: GposIntrospector,
    encoded_targets: set[str],
    encoded_context_marks: set[str],
    target_label: str,
) -> tuple[dict[tuple[str, tuple[str, ...]], int], list[str]]:
    return _contextual_raise_rules(
        gpos,
        encoded_targets,
        target_label,
        _iter_target_first_raise_subtables(
            gpos,
            encoded_targets,
            encoded_context_marks,
        ),
    )


def _contextual_raise_rules(
    gpos: GposIntrospector,
    encoded_targets: set[str],
    target_label: str,
    subtables: Iterable[RaiseSubtable],
) -> tuple[dict[tuple[str, tuple[str, ...]], int], list[str]]:
    rules: dict[tuple[str, tuple[str, ...]], int] = {}
    problems: list[str] = []
    lookups = gpos.lookups

    for (
        lookup_index,
        pos_lookup_records,
        base_glyphs,
        context_coverages,
        target_glyphs,
    ) in subtables:
        missing_target_glyphs = sorted(encoded_targets - target_glyphs)
        if missing_target_glyphs:
            problems.append(
                f"lookup {lookup_index}: context omits {target_label} "
                f"{', '.join(missing_target_glyphs)}"
            )

        for lookup_record in pos_lookup_records:
            if lookup_record.SequenceIndex != 0:
                continue
            if lookup_record.LookupListIndex >= len(lookups):
                problems.append(
                    f"lookup {lookup_index}: referenced lookup "
                    f"{lookup_record.LookupListIndex} is out of range"
                )
                continue

            y_placements, placement_problems = gpos.single_pos_y_placements(
                lookups[lookup_record.LookupListIndex],
                encoded_targets,
            )
            problems.extend(
                f"lookup {lookup_record.LookupListIndex}: {problem}"
                for problem in placement_problems
            )

            missing_placements = sorted(encoded_targets - y_placements.keys())
            if missing_placements:
                problems.append(
                    f"lookup {lookup_record.LookupListIndex}: missing "
                    f"YPlacement for {', '.join(missing_placements)}"
                )
                continue

            deltas = set(y_placements.values())
            if len(deltas) != 1:
                problems.append(
                    f"lookup {lookup_record.LookupListIndex}: inconsistent "
                    f"{target_label} YPlacement values"
                )
                continue

            delta_y = next(iter(deltas))
            for base_glyph in base_glyphs:
                for context_glyphs in product(*context_coverages):
                    key = (base_glyph, context_glyphs)
                    rules[key] = rules.get(key, 0) + delta_y

    return rules, problems


def contextual_shaping_problems(
    glyphs: GlyphIntrospector,
    shaper: Shaper,
    expected_deltas: Mapping[tuple[str, tuple[str, ...]], int],
    target_codepoint: int = SBMUFL_ISON_SHAPING_PROBE_CODEPOINT,
    target_label: str = "ison",
) -> list[str]:
    return _contextual_shaping_problems(
        glyphs,
        shaper,
        expected_deltas,
        target_codepoint,
        target_label,
        target_first=False,
    )


def target_first_contextual_shaping_problems(
    glyphs: GlyphIntrospector,
    shaper: Shaper,
    expected_deltas: Mapping[tuple[str, tuple[str, ...]], int],
    target_codepoint: int,
    target_label: str,
) -> list[str]:
    return _contextual_shaping_problems(
        glyphs,
        shaper,
        expected_deltas,
        target_codepoint,
        target_label,
        target_first=True,
    )


def _contextual_shaping_problems(
    glyphs: GlyphIntrospector,
    shaper: Shaper,
    expected_deltas: Mapping[tuple[str, tuple[str, ...]], int],
    target_codepoint: int,
    target_label: str,
    *,
    target_first: bool,
) -> list[str]:
    codepoint_by_glyph = {
        glyph_name: codepoint for codepoint, glyph_name in glyphs.cmap.items()
    }
    target_glyph = glyphs.cmap.get(target_codepoint)
    if target_glyph is None:
        return [f"U+{target_codepoint:04X} {target_label} is not encoded"]

    problems: list[str] = []
    target_text = chr(target_codepoint)
    for (base_name, context_names), expected_delta in sorted(expected_deltas.items()):
        base_codepoint = codepoint_by_glyph.get(base_name)
        context_codepoints = [
            codepoint_by_glyph.get(context_name) for context_name in context_names
        ]
        if base_codepoint is None or any(
            context_codepoint is None for context_codepoint in context_codepoints
        ):
            continue

        base_text = chr(base_codepoint)
        context_text = "".join(
            chr(cast(int, context_codepoint))
            for context_codepoint in context_codepoints
        )
        base_target_position = shaper.position_of(base_text + target_text, target_glyph)
        if base_target_position is None:
            problems.append(f"{base_name}: {target_label} did not shape")
            continue

        context_label = " + ".join(context_names)
        if target_first:
            sequence_label = f"{base_name} + {target_label} + {context_label}"
            sequence_text = base_text + target_text + context_text
        else:
            sequence_label = f"{base_name} + {context_label} + {target_label}"
            sequence_text = base_text + context_text + target_text
        context_target_position = shaper.position_of(sequence_text, target_glyph)
        if context_target_position is None:
            problems.append(f"{sequence_label}: {target_label} did not shape")
            continue

        base_x, base_y = base_target_position
        context_x, context_y = context_target_position
        actual_delta = context_y - base_y
        if context_x != base_x or actual_delta != expected_delta:
            problems.append(
                f"{sequence_label}: shaped {target_label} offset "
                f"X={context_x} Y={context_y}; without context X={base_x} "
                f"Y={base_y}; expected X={base_x} Y={base_y + expected_delta}"
            )

    return problems
