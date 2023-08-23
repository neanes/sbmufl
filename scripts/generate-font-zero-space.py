import argparse
import fontforge
import json


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

    for char in (char for char in font.glyphs() if 57344 <= char.unicode <= 63743):
        if char.width != 0:
            print("Trimming ", canonical_glyphname(codepoint_to_name, char))
            font.selection.select(char)
            font.autoWidth(0)

    font.generate(args.outfile_otf)

    font.fontname = "NeanesZeroSpace"

    font.save(args.outfile_sfd)
