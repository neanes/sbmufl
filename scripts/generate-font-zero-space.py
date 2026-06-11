import argparse
import json

import fontforge
import psMat

BARLINE_THESEOS_CODEPOINTS = {
    0xE212,  # barlineTheseos
    0xE215,  # barlineShortTheseos
}


def format_codepoint(unicode_):
    return "U+" + hex(unicode_)[2:].upper()


def canonical_glyphname(codepoint_to_name, glyph, fallback=True):
    codepoint = format_codepoint(glyph.unicode)
    try:
        return codepoint_to_name[codepoint]
    except KeyError:
        if fallback:
            return glyph.glyphname
        raise ValueError(
            f"There" "s no SBMuFL character defined at codepoint {codepoint}."
        )


def get_anchor_position(glyph, anchor_name, anchor_types):
    for anchor in glyph.anchorPoints:
        if anchor[0] == anchor_name and anchor[1] in anchor_types:
            return anchor[2], anchor[3]

    raise ValueError(f"{glyph.glyphname} is missing a {anchor_name} anchor.")


def get_lowest_contour_bbox(glyph):
    contour_bboxes = []

    for contour in glyph.foreground:
        xs = [p.x for p in contour]
        ys = [p.y for p in contour]

        if not xs:
            continue

        xmin = min(xs)
        ymin = min(ys)
        xmax = max(xs)
        ymax = max(ys)

        if xmin == xmax or ymin == ymax:
            continue

        contour_bboxes.append((xmin, ymin, xmax, ymax))

    if not contour_bboxes:
        return None

    return min(contour_bboxes, key=lambda bbox: bbox[1])  # lowest ymin


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate zero-space font")
    parser.add_argument("infile", help="Relative path to input.sfd")
    parser.add_argument("outfile_otf", help="Relative path to output.otf")
    parser.add_argument("outfile_sfd", help="Relative path to output.sfd")
    parser.add_argument("glyphnames_path", help="Relative path to glyphnames.json")
    args = parser.parse_args()

    codepoint_to_name = {}

    with open(args.glyphnames_path) as glyphnames:
        glyphnames = json.load(glyphnames)
        codepoint_to_name = {
            data["codepoint"]: name for name, data in glyphnames.items()
        }

    font = fontforge.open(args.infile)

    TEMP_GLYPH_NAME = ".__temp_autowidth_measure"

    for char in (char for char in font.glyphs() if 57344 <= char.unicode <= 63743):
        if (
            char.width != 0
            and not (0xE2A0 <= char.unicode <= 0xE42F)
            and not (0xF003 <= char.unicode <= 0xF004)
        ):
            while char.references:
                char.unlinkRef()

            if char.unicode in BARLINE_THESEOS_CODEPOINTS:
                barline_bbox = get_lowest_contour_bbox(char)

                if barline_bbox is None:
                    font.selection.select(char)
                    font.autoWidth(0)
                else:
                    xmin, ymin, xmax, ymax = barline_bbox
                    barline_width = round(xmax - xmin)

                    # Move the glyph so the barline contour starts at x=0.
                    # The yfen may remain outside the advance width.
                    char.transform(psMat.translate(-xmin, 0))
                    char.width = barline_width
            else:
                font.selection.select(char)
                font.autoWidth(0)

    font.generate(args.outfile_otf)

    font.fontname += "Engraving"

    font.save(args.outfile_sfd)
