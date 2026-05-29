"""Bake ison base anchors and gorgon-triggered contextual raises into SFDs.

This script intentionally mutates the checked-in FontForge sources. It is a
source-regeneration step to run when the ison positioning rules change, not a
normal build step.

Usage:
    fontforge -script scripts/update-ison-positioning.py
    cd scripts
    ./build.sh

Commit the regenerated sources and build artifacts together.
"""

import math
from collections import defaultdict
from itertools import product
from pathlib import Path

import fontforge

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = REPO_ROOT / "sources"

ISON_ANCHOR = "isonIndicator"
ISON_ABOVE_MARK_ANCHOR = "isonIndicatorAboveMark"
GORGON_TOP_ANCHOR = "gorgonTop"
GORGON_SECONDARY_ANCHOR = "gorgonSecondary"
MARK_LOOKUP = "'mark' Mark Positioning lookup 0"
ISON_RAISE_LOOKUP_PREFIX = "isonGorgonRaise"
ISON_RAISE_CONTEXT_LOOKUP = "isonGorgonRaiseContext"
ISON_GORGON_CONTEXT_MARK_CLASS = "isonGorgonContextMarks"
MODIFICATION_TIME_PREFIX = "ModificationTime: "
MARK_FEATURES = (
    (
        "mark",
        (
            ("DFLT", ("dflt",)),
            ("byzm", ("dflt",)),
            ("latn", ("dflt",)),
        ),
    ),
)
ISON_CLEARANCE = 120
ISON_CONTEXTUAL_RAISE_GRID = 20
ISON_INDICATOR_CODEPOINTS = range(0xE260, 0xE26B)
GORGON_ABOVE_CODEPOINTS = [
    0xE0F0,
    0xE0F2,
    0xE0F3,
    0xE0F4,
    0xE0F6,
    0xE0F7,
    0xE0F8,
    0xE0FA,
    0xE0FB,
]
GORGON_SECONDARY_ABOVE_CODEPOINTS = [
    0xE100,  # gorgonSecondary
    0xE101,  # gorgonDottedLeftSecondary
    0xE102,  # gorgonDottedRightSecondary
    0xE103,  # digorgonSecondary
    0xE105,  # digorgonDottedRightSecondary
    0xE106,  # trigorgonSecondary
    0xE108,  # trigorgonDottedRightSecondary
    0xE109,  # digorgonDottedLeftSecondary
    0xE10A,  # trigorgonDottedLeftSecondary
]
GORGON_ANCHOR_GROUPS = [
    (GORGON_TOP_ANCHOR, GORGON_ABOVE_CODEPOINTS),
    (GORGON_SECONDARY_ANCHOR, GORGON_SECONDARY_ABOVE_CODEPOINTS),
]
ISON_COMPROMISE_CODEPOINTS = {
    0xE005,  # oligonYpsiliRight
    0xE006,  # oligonYpsiliLeft
    0xE007,  # oligonKentimaYpsiliRight
    0xE044,  # petastiYpsiliRight
    0xE046,  # petastiKentimaYpsiliRight
    0xE086,  # oligonYpsiliRightKentimata
    0xE087,  # oligonYpsiliLeftKentimata
}


def reference_ison_y(font):
    ison_anchor = get_anchor(font["ison"], ISON_ANCHOR, "base")
    if ison_anchor is None:
        raise ValueError("ison is missing an isonIndicator base anchor")
    return ison_anchor[1]


def expected_ison_y(glyph, reference_y):
    if glyph.glyphname == "ison":
        return reference_y

    full_y = max(reference_y, math.ceil(glyph.boundingBox()[3] + ISON_CLEARANCE))
    if glyph.unicode in ISON_COMPROMISE_CODEPOINTS:
        return math.ceil((reference_y + full_y) / 2)

    return full_y


def get_anchor(glyph, name, kind):
    for anchor_name, anchor_kind, x, y in glyph.anchorPoints:
        if anchor_name == name and anchor_kind == kind:
            return x, y
    return None


def has_glyph(font, glyph_name):
    return any(glyph.glyphname == glyph_name for glyph in font.glyphs())


def has_ison_positioning_model(font):
    return has_glyph(font, "ison") and get_anchor(font["ison"], ISON_ANCHOR, "base")


def source_paths():
    return sorted(SOURCES_DIR.glob("*.sfd"))


def replace_anchor(glyph, name, kind, x, y):
    glyph.anchorPoints = tuple(
        anchor
        for anchor in glyph.anchorPoints
        if not (anchor[0] == name and anchor[1] == kind)
    )
    glyph.addAnchorPoint(name, kind, x, y)


def read_modification_time(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(MODIFICATION_TIME_PREFIX):
            return line
    return None


def restore_modification_time(path, modification_time):
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


def glyph_names_for_codepoints(font, codepoints):
    glyph_names = []
    for codepoint in codepoints:
        try:
            glyph = font[codepoint]
        except TypeError:
            continue
        glyph_names.append(glyph.glyphname)
    return glyph_names


def glyph_list(glyph_names):
    return "[" + " ".join(glyph_names) + "]"


def remove_ison_raise_lookups(font):
    for lookup in list(font.gpos_lookups):
        if lookup.startswith(ISON_RAISE_LOOKUP_PREFIX):
            font.removeLookup(lookup)


def quantize_raise(delta_y):
    return math.ceil(delta_y / ISON_CONTEXTUAL_RAISE_GRID) * ISON_CONTEXTUAL_RAISE_GRID


def gorgon_marks_by_anchor(font):
    marks_by_anchor = {}
    for anchor_name, codepoints in GORGON_ANCHOR_GROUPS:
        gorgon_names = glyph_names_for_codepoints(font, codepoints)
        if not gorgon_names:
            continue

        gorgon_mark_anchors = {}
        for gorgon_name in gorgon_names:
            gorgon = font[gorgon_name]
            mark_anchor = get_anchor(gorgon, anchor_name, "mark")
            if mark_anchor is None:
                raise ValueError(
                    f"{gorgon_name} is missing a {anchor_name} mark anchor"
                )
            gorgon_mark_anchors[gorgon_name] = mark_anchor

        marks_by_anchor[anchor_name] = gorgon_mark_anchors

    return marks_by_anchor


def calculate_raise_delta(base_y, gorgon_base_y, gorgon_mark_y, gorgon_ymax):
    mark_top_y = gorgon_base_y - gorgon_mark_y + gorgon_ymax
    target_y = max(base_y, math.ceil(mark_top_y + ISON_CLEARANCE))
    delta_y = target_y - base_y
    if delta_y <= 0:
        return 0
    return quantize_raise(delta_y)


def build_contextual_raise_rules(font, marks_by_anchor):
    rules = defaultdict(list)
    for base in font.glyphs():
        ison_anchor = get_anchor(base, ISON_ANCHOR, "base")
        if ison_anchor is None:
            continue

        _, base_y = ison_anchor
        deltas_by_anchor = {}
        for anchor_name, gorgon_mark_anchors in marks_by_anchor.items():
            gorgon_base_anchor = get_anchor(base, anchor_name, "base")
            if gorgon_base_anchor is None:
                continue

            _, gorgon_base_y = gorgon_base_anchor
            deltas_by_gorgon = {}
            for gorgon_name, (_, gorgon_mark_y) in gorgon_mark_anchors.items():
                gorgon_ymax = font[gorgon_name].boundingBox()[3]
                delta_y = calculate_raise_delta(
                    base_y,
                    gorgon_base_y,
                    gorgon_mark_y,
                    gorgon_ymax,
                )
                deltas_by_gorgon[gorgon_name] = delta_y
                if delta_y > 0:
                    rules[((gorgon_name,), delta_y)].append(base.glyphname)
            deltas_by_anchor[anchor_name] = deltas_by_gorgon

        primary_deltas = deltas_by_anchor.get(GORGON_TOP_ANCHOR, {})
        secondary_deltas = deltas_by_anchor.get(GORGON_SECONDARY_ANCHOR, {})
        for primary_name, secondary_name in product(primary_deltas, secondary_deltas):
            delta_y = max(
                primary_deltas[primary_name], secondary_deltas[secondary_name]
            )
            if delta_y <= 0:
                continue
            rules[((primary_name, secondary_name), delta_y)].append(base.glyphname)
            rules[((secondary_name, primary_name), delta_y)].append(base.glyphname)

    return rules


def contextual_raise_rule(
    base_names,
    gorgon_names,
    ison_class,
    delta_lookup,
):
    gorgon_context = " ".join(f"[{gorgon_name}]" for gorgon_name in gorgon_names)
    return (
        f"{glyph_list(sorted(base_names))} {gorgon_context} | "
        f"{ison_class} @<{delta_lookup}> |"
    )


def set_mark_class(font, class_name, glyph_names):
    font.markClasses = tuple(
        (name, names) for name, names in font.markClasses if name != class_name
    ) + ((class_name, tuple(sorted(glyph_names))),)


def add_contextual_raise_lookups(font, rules, ison_indicator_names, context_mark_names):
    if not rules:
        return

    set_mark_class(font, ISON_GORGON_CONTEXT_MARK_CLASS, context_mark_names)

    previous_lookup = MARK_LOOKUP
    delta_lookup_names = {}
    for delta_y in sorted({delta_y for _, delta_y in rules}):
        lookup = f"{ISON_RAISE_LOOKUP_PREFIX}_{delta_y:03d}"
        subtable = f"{lookup}-1"
        font.addLookup(lookup, "gpos_single", (), (), previous_lookup)
        font.addLookupSubtable(lookup, subtable)
        for ison_name in ison_indicator_names:
            font[ison_name].addPosSub(subtable, 0, delta_y, 0, 0)
        delta_lookup_names[delta_y] = lookup
        previous_lookup = lookup

    font.addLookup(
        ISON_RAISE_CONTEXT_LOOKUP,
        "gpos_contextchain",
        (ISON_GORGON_CONTEXT_MARK_CLASS,),
        MARK_FEATURES,
        previous_lookup,
    )
    previous_subtable = None
    ison_class = glyph_list(ison_indicator_names)

    for subtable_index, ((gorgon_names, delta_y), base_names) in enumerate(
        sorted(rules.items(), key=lambda item: (item[0][1], item[0][0])),
        start=1,
    ):
        subtable = f"{ISON_RAISE_CONTEXT_LOOKUP}-{subtable_index}"
        rule = contextual_raise_rule(
            base_names,
            gorgon_names,
            ison_class,
            delta_lookup_names[delta_y],
        )
        if previous_subtable is None:
            font.addContextualSubtable(
                ISON_RAISE_CONTEXT_LOOKUP,
                subtable,
                "coverage",
                rule,
            )
        else:
            font.addContextualSubtable(
                ISON_RAISE_CONTEXT_LOOKUP,
                subtable,
                "coverage",
                rule,
                previous_subtable,
            )
        previous_subtable = subtable


def update_font(path):
    modification_time = read_modification_time(path)
    font = fontforge.open(str(path))
    if not has_ison_positioning_model(font):
        font.close()
        return False

    remove_ison_raise_lookups(font)
    try:
        font.removeAnchorClass(ISON_ABOVE_MARK_ANCHOR)
    except EnvironmentError:
        pass

    reference_y = reference_ison_y(font)
    for glyph in font.glyphs():
        anchor = get_anchor(glyph, ISON_ANCHOR, "base")
        if anchor is None:
            continue

        replace_anchor(
            glyph,
            ISON_ANCHOR,
            "base",
            anchor[0],
            expected_ison_y(glyph, reference_y),
        )

    ison_indicator_names = glyph_names_for_codepoints(font, ISON_INDICATOR_CODEPOINTS)
    marks_by_anchor = gorgon_marks_by_anchor(font)
    if not ison_indicator_names:
        raise ValueError(f"{path} does not encode any ison indicators")
    if not marks_by_anchor:
        raise ValueError(f"{path} does not encode any gorgon-family marks")

    rules = build_contextual_raise_rules(font, marks_by_anchor)
    context_mark_names = set(ison_indicator_names)
    for gorgon_mark_anchors in marks_by_anchor.values():
        context_mark_names.update(gorgon_mark_anchors)
    add_contextual_raise_lookups(font, rules, ison_indicator_names, context_mark_names)

    font.save(str(path))
    font.close()
    restore_modification_time(path, modification_time)
    return True


if __name__ == "__main__":
    for source_path in source_paths():
        update_font(source_path)
