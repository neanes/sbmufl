import argparse
import json

import fontforge

STANDARD_GLUE_WIDTH = 130  # TODO this should be read from the metadata

YPORROI_GORGON_MARKS = {
    0xF009: "gorgonAbove",
    0xF00A: "digorgon",
    0xF00B: "trigorgon",
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
            mark_name = YPORROI_GORGON_MARKS.get(char.unicode)

            if mark_name is not None:
                if TEMP_GLYPH_NAME in font:
                    font.removeGlyph(TEMP_GLYPH_NAME)

                temp = font.createChar(-1, TEMP_GLYPH_NAME)
                temp.addReference(char.glyphname)
                temp.addReference(mark_name)

                while temp.references:
                    temp.unlinkRef()

                combined_xmin, ymin, combined_xmax, ymax = temp.boundingBox()
                combined_xmin = int(round(combined_xmin))
                combined_xmax = int(round(combined_xmax))

                while char.references:
                    char.unlinkRef()

                base_xmin, ymin, base_xmax, ymax = char.boundingBox()
                base_xmin = int(round(base_xmin))
                base_xmax = int(round(base_xmax))

                char.left_side_bearing = combined_xmax - base_xmax
                char.right_side_bearing = (
                    base_xmin - combined_xmin - STANDARD_GLUE_WIDTH
                )

                font.removeGlyph(TEMP_GLYPH_NAME)
                continue

            while char.references:
                char.unlinkRef()

            if mark_name is None:
                font.selection.select(char)
                font.autoWidth(0)

    font.generate(args.outfile_otf)

    font.fontname += "Engraving"

    font.save(args.outfile_sfd)
