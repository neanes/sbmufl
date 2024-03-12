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
    parser = argparse.ArgumentParser(description="Mirror RTL anchors")
    parser.add_argument("infile", help="Relative path to input.sfd")
    parser.add_argument(
        "--glyphnames_path", "-g", help="Relative path to glyphnames.json"
    )
    args = parser.parse_args()

    codepoint_to_name = {}

    anchors_to_mirror = (
        "heteronConnecting",
        "omalonConnecting",
        "yfenAbove",
        "yfenBelow",
    )

    with open(args.glyphnames_path) as glyphnames:
        glyphnames = json.load(glyphnames)
        codepoint_to_name = {
            data["codepoint"]: name for name, data in glyphnames.items()
        }

    font = fontforge.open(args.infile)

    for char in (char for char in font.glyphs() if 57344 <= char.unicode <= 63743):
        updated_anchorPoints = list()
        for i, anchor in enumerate(char.anchorPoints):
            anchor_name = anchor[0]
            updated_anchor = anchor
            if anchor_name in anchors_to_mirror:
                temp = list(anchor)
                # mirror the x coordinate
                temp[2] = char.width - anchor[2]
                updated_anchor = tuple(temp)

                print(
                    f"Mirroring {canonical_glyphname(codepoint_to_name, char)} : {anchor_name}"
                )

            updated_anchorPoints.append(updated_anchor)

        char.anchorPoints = tuple(updated_anchorPoints)

    # font.generate(args.outfile_otf)

    font.save(args.infile)
