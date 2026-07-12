#!/usr/bin/env fontforge
import fontforge
from statistics import mean, stdev
import sys

if len(sys.argv) < 2:
    print("Usage: fontforge -script antikenoma_apli.py <font.sfd|font.otf> <newY>")
    sys.exit(1)

new_y = int(sys.argv[2]) if len(sys.argv) > 2 else None

font = fontforge.open(sys.argv[1])

glyph_spacings = {}
if new_y is not None:
    for glyph in font.glyphs():
        anchors = list(glyph.anchorPoints)

        antikenoma = None
        for anchor in anchors:
            if anchor[0] == "antikenoma":
                antikenoma = anchor
                break

        if antikenoma is None:
            continue

        modified = False

        for i, (name, anchor_type, x, y) in enumerate(anchors):
            if name != "apli":
                continue

            # Make the relative Y distance equal to new_y.
            y = antikenoma[3] + new_y

            anchors[i] = (name, anchor_type, x, y)
            modified = True

        if modified:
            glyph.anchorPoints = tuple(anchors)
            glyph.changed = True

    font.save()
else:
    for glyph in font.glyphs():
        anchors = {anchor[0]: (anchor[2], anchor[3]) for anchor in glyph.anchorPoints}

        if "antikenoma" not in anchors or "apli" not in anchors:
            continue

        antikenoma_x, antikenoma_y = anchors["antikenoma"]
        apli_x, apli_y = anchors["apli"]

        relative_x = apli_x - antikenoma_x
        relative_y = apli_y - antikenoma_y

        print(f"({relative_x}, {relative_y})\t" f"{glyph.glyphname}")
