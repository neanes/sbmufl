import fontforge
import json


def format_codepoint(unicode_):
    return 'U+' + hex(unicode_)[2:].upper()


def canonical_glyphname(codepoint_to_name, glyph, fallback=True):
    codepoint = format_codepoint(glyph.unicode)
    try:
        return codepoint_to_name[codepoint]
    except KeyError:
        if fallback:
            return glyph.glyphname
        raise ValueError(
            f'There''s no SBMuFL character defined at codepoint {codepoint}.')


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "USAGE: ffpython generate-font-metadata.py <relative/path/to/input.sfd> <relative/path/to/output.otf> <relative/path/to/output.sfd> [relative/path/to/glyphnames.json]")
        exit(1)

    infile = sys.argv[1]
    outfile_otf = sys.argv[2]
    outfile_sfd = sys.argv[3]
    glyphnames_filepath = sys.argv[4] if len(
        sys.argv) >= 4 else 'glyphnames.json'

    codepoint_to_name = {}

    with open(glyphnames_filepath) as glyphnames:
        glyphnames = json.load(glyphnames)
        codepoint_to_name = {
            data['codepoint']: name for name, data in glyphnames.items()
        }

    font = fontforge.open(infile)

    for char in (char for char in font.glyphs() if 57344 <= char.unicode <= 63743):
        if char.width != 0:
            print('Trimming ', canonical_glyphname(codepoint_to_name, char))
            font.selection.select(char)
            font.autoWidth(0)

    font.generate(outfile_otf)

    font.fontname = "NeanesZeroSpace"

    font.save(outfile_sfd)
