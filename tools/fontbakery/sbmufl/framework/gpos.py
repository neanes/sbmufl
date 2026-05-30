from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from functools import cached_property
from typing import Any, NamedTuple

from fontTools.ttLib.tables import otTables

MarkClassRef = tuple[int, int]


class MarkAttachmentAnchors(NamedTuple):
    mark_classes: set[MarkClassRef]
    missing_mark_anchors: list[str]
    base_anchor_positions: dict[str, set[tuple[MarkClassRef, int, int]]]
    base_anchor_y_by_name: dict[str, int]
    conflicting_base_anchors: list[str]


def format_mark_class(mark_class: MarkClassRef) -> str:
    subtable_index, class_id = mark_class
    return f"subtable {subtable_index} class {class_id}"


def single_base_anchor_y_by_name(
    anchor_positions: Mapping[str, set[tuple[MarkClassRef, int, int]]],
) -> tuple[dict[str, int], list[str]]:
    expected_y_by_name: dict[str, int] = {}
    conflicting_positions: list[str] = []

    for glyph_name, positions in sorted(anchor_positions.items()):
        y_positions = {y for _, _, y in positions}
        if len(y_positions) != 1:
            formatted_positions = [
                f"{format_mark_class(mark_class)}, X={x}, Y={y}"
                for mark_class, x, y in sorted(positions)
            ]
            conflicting_positions.append(
                f"{glyph_name}: {', '.join(formatted_positions)}"
            )
            continue

        expected_y_by_name[glyph_name] = next(iter(y_positions))

    return expected_y_by_name, conflicting_positions


def value_record_has_horizontal_adjustment(value_record: Any) -> bool:
    return any(
        (getattr(value_record, field_name, 0) or 0) != 0
        for field_name in ("XPlacement", "XAdvance", "YAdvance")
    )


class GposIntrospector:
    def __init__(self, ttfont: Any) -> None:
        self.ttfont = ttfont

    @cached_property
    def lookups(self) -> Sequence[Any]:
        if "GPOS" not in self.ttfont:
            return []

        lookup_list = self.ttfont["GPOS"].table.LookupList
        if lookup_list is None:
            return []

        return lookup_list.Lookup

    def lookup_types(self) -> set[int]:
        lookup_types: set[int] = set()
        for lookup in self.lookups:
            if lookup.LookupType == otTables.ExtensionPos.LookupType:
                lookup_types.update(
                    subtable.ExtensionLookupType for subtable in lookup.SubTable
                )
            else:
                lookup_types.add(lookup.LookupType)

        return lookup_types

    def iter_lookup_subtables(self, lookup_type: int) -> Iterator[tuple[int, Any]]:
        for lookup_index, lookup in enumerate(self.lookups):
            if lookup.LookupType == lookup_type:
                for subtable in lookup.SubTable:
                    yield lookup_index, subtable
            elif lookup.LookupType == otTables.ExtensionPos.LookupType:
                for subtable in lookup.SubTable:
                    if subtable.ExtensionLookupType == lookup_type:
                        yield lookup_index, subtable.ExtSubTable

    def mark_to_base_subtables(self) -> Iterator[tuple[int, Any]]:
        for index, (_lookup_index, subtable) in enumerate(
            self.iter_lookup_subtables(otTables.MarkBasePos.LookupType)
        ):
            yield index, subtable

    def mark_coverages(self) -> tuple[set[str], set[str]]:
        mark_to_base_glyphs: set[str] = set()
        mark_to_mark_glyphs: set[str] = set()

        for _lookup_index, subtable in self.iter_lookup_subtables(
            otTables.MarkBasePos.LookupType
        ):
            mark_to_base_glyphs.update(subtable.MarkCoverage.glyphs)
        for _lookup_index, subtable in self.iter_lookup_subtables(
            otTables.MarkMarkPos.LookupType
        ):
            mark_to_mark_glyphs.update(subtable.Mark1Coverage.glyphs)

        return mark_to_base_glyphs, mark_to_mark_glyphs

    def mark_to_base_mark_classes(self, glyph_names: set[str]) -> set[MarkClassRef]:
        mark_classes: set[MarkClassRef] = set()

        for subtable_index, subtable in self.mark_to_base_subtables():
            for glyph_name, mark_record in zip(
                subtable.MarkCoverage.glyphs,
                subtable.MarkArray.MarkRecord,
                strict=True,
            ):
                if glyph_name in glyph_names:
                    mark_classes.add((subtable_index, mark_record.Class))

        return mark_classes

    def mark_to_base_mark_anchor_positions(
        self, glyph_names: set[str]
    ) -> dict[str, set[tuple[MarkClassRef, int, int]]]:
        positions: dict[str, set[tuple[MarkClassRef, int, int]]] = {}

        for subtable_index, subtable in self.mark_to_base_subtables():
            for glyph_name, mark_record in zip(
                subtable.MarkCoverage.glyphs,
                subtable.MarkArray.MarkRecord,
                strict=True,
            ):
                if glyph_name in glyph_names and mark_record.MarkAnchor is not None:
                    positions.setdefault(glyph_name, set()).add(
                        (
                            (subtable_index, mark_record.Class),
                            mark_record.MarkAnchor.XCoordinate,
                            mark_record.MarkAnchor.YCoordinate,
                        )
                    )

        return positions

    def mark_to_base_base_anchor_positions(
        self, mark_classes: set[MarkClassRef]
    ) -> dict[str, set[tuple[MarkClassRef, int, int]]]:
        positions: dict[str, set[tuple[MarkClassRef, int, int]]] = {}

        for subtable_index, subtable in self.mark_to_base_subtables():
            subtable_mark_classes = {
                mark_class
                for class_subtable_index, mark_class in mark_classes
                if class_subtable_index == subtable_index
            }
            if not subtable_mark_classes:
                continue

            for glyph_name, base_record in zip(
                subtable.BaseCoverage.glyphs,
                subtable.BaseArray.BaseRecord,
                strict=True,
            ):
                for mark_class in subtable_mark_classes:
                    if mark_class >= len(base_record.BaseAnchor):
                        continue

                    anchor = base_record.BaseAnchor[mark_class]
                    if anchor is not None:
                        positions.setdefault(glyph_name, set()).add(
                            (
                                (subtable_index, mark_class),
                                anchor.XCoordinate,
                                anchor.YCoordinate,
                            )
                        )

        return positions

    def mark_attachment_anchors(self, glyph_names: set[str]) -> MarkAttachmentAnchors:
        mark_classes = self.mark_to_base_mark_classes(glyph_names)
        mark_anchor_positions = self.mark_to_base_mark_anchor_positions(glyph_names)
        base_anchor_positions = self.mark_to_base_base_anchor_positions(mark_classes)
        base_anchor_y_by_name, conflicting_base_anchors = single_base_anchor_y_by_name(
            base_anchor_positions
        )

        return MarkAttachmentAnchors(
            mark_classes=mark_classes,
            missing_mark_anchors=sorted(glyph_names - mark_anchor_positions.keys()),
            base_anchor_positions=base_anchor_positions,
            base_anchor_y_by_name=base_anchor_y_by_name,
            conflicting_base_anchors=conflicting_base_anchors,
        )

    def single_pos_y_placements(
        self, lookup: Any, glyph_names: set[str]
    ) -> tuple[dict[str, int], list[str]]:
        positions: dict[str, int] = {}
        problems: list[str] = []

        if lookup.LookupType not in {
            otTables.SinglePos.LookupType,
            otTables.ExtensionPos.LookupType,
        }:
            return positions, [f"lookup type {lookup.LookupType} is not SinglePos"]

        subtables = lookup.SubTable
        if lookup.LookupType == otTables.ExtensionPos.LookupType:
            subtables = [
                subtable.ExtSubTable
                for subtable in lookup.SubTable
                if subtable.ExtensionLookupType == otTables.SinglePos.LookupType
            ]

        for subtable in subtables:
            if subtable.Format == 1:
                value_record = subtable.Value
                if value_record_has_horizontal_adjustment(value_record):
                    problems.append("SinglePos format 1 has non-YPlacement adjustments")
                for glyph_name in set(subtable.Coverage.glyphs).intersection(
                    glyph_names
                ):
                    positions[glyph_name] = getattr(value_record, "YPlacement", 0) or 0
            elif subtable.Format == 2:
                for glyph_name, value_record in zip(
                    subtable.Coverage.glyphs,
                    subtable.Value,
                    strict=True,
                ):
                    if glyph_name not in glyph_names:
                        continue
                    if value_record_has_horizontal_adjustment(value_record):
                        problems.append(
                            f"{glyph_name}: SinglePos format 2 has "
                            "non-YPlacement adjustments"
                        )
                    positions[glyph_name] = getattr(value_record, "YPlacement", 0) or 0
            else:
                problems.append(f"unsupported SinglePos format {subtable.Format}")

        return positions, problems

    def iter_chain_context_pos_subtables(self) -> Iterator[tuple[int, Any]]:
        for lookup_index, subtable in self.iter_lookup_subtables(
            otTables.ChainContextPos.LookupType
        ):
            if subtable.Format == 3:
                yield lookup_index, subtable

    def chain_context_pos_subtable_counts_by_lookup(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        for lookup_index, _subtable in self.iter_chain_context_pos_subtables():
            counts[lookup_index] = counts.get(lookup_index, 0) + 1
        return counts
