import argparse
import fontforge
import json


class SbmuflFont(object):
    valid_anchor_names = (
        'agogi',
        'agogiAboveFthora',
        'antikenoma',
        'apli',
        'barline',
        'diesis',
        'endofonon',
        'fthoraTop',
        'fthoraTopSecondary',
        'fthoraTopTertiary',
        'fthoraBottom',
        'gorgonTop',
        'gorgonBottom',
        'gorgonSecondary',
        'isonIndicator',
        'heteron',
        'heteronConnecting',
        'klasmaTop',
        'klasmaBottom',
        'koronis',
        'martyriaTop',
        'martyriaBottom',
        'measureNumber',
        'modeTop',
        'noteTop',
        'omalon',
        'omalonConnecting',
        'psifiston',
        'yfenAbove',
        'yfenBelow',
        'yfesis',
        'yfesisSecondary',
        'yfesisTertiary',
    )

    @ staticmethod
    def format_codepoint(unicode_):
        return 'U+' + hex(unicode_)[2:].upper()

    def canonical_glyphname(self, glyph, fallback=True):
        codepoint = SbmuflFont.format_codepoint(glyph.unicode)
        try:
            return self.codepoint_to_name[codepoint]
        except KeyError:
            if fallback:
                return glyph.glyphname
            raise ValueError(
                f'There''s no SBMuFL character defined at codepoint {codepoint}.')

    def __init__(self, font_filepath, glyphnames_filepath='glyphnames.json', mode='w'):
        self.font = fontforge.open(font_filepath)
        self.read_only = (mode == 'r')

        with open(glyphnames_filepath) as infile:
            glyphnames = json.load(infile)
            self.codepoint_to_name = {
                data['codepoint']: name for name, data in glyphnames.items()}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.font:
            self.font.close()
        return False

    def __iter__(self):
        # Standard SBMuFL characters are encoded from U+E000 to U+F8FF.
        return (char for char in self.font.glyphs() if 57344 <= char.unicode <= 63743)

    def __getitem__(self, glyphname):
        return self.font[glyphname]

    def save(self, *args):
        if self.read_only and not args:
            raise PermissionError('Font is opened in read-only mode.')
        self.font.save(*args)

    def close(self):
        self.font.close()

    def export_font(self, filename=None, *args, **kwargs):
        filename = filename or self.font.fontname + '.otf'
        self.font.generate(filename, *args, **kwargs)

    def export_metadata(self, filename=None, indent=2, **kwargs):
        filename = filename or self.font.fontname + '.metadata.json'

        with open(filename, 'w') as outfile:
            json.dump(self.generate_metadata(),
                      outfile, indent=indent, **kwargs)

    def generate_metadata(self):
        return _SbmuflMetadata(self).asdict()

    def rename_glyphs(self, warning=True):
        if warning:
            print("SbmuflFont.rename_glyphs()\n"
                  "Warning: Batch renaming glyphs can mess up your font files. "
                  "Be sure to have a backup before using this method. "
                  "You can disable this warning by adding `warning=False` to the argument list of this method:\n"
                  "    `<your_font>.rename_glyphs(warning=False)`\n")
            choice = input("Do you want to rename glyphs now anyway? (Y/N) > ")
            if not choice.upper() == "Y":
                print("Renaming aborted. Returning to call site.")
                return
            else:
                print("Continuing to rename glyphs.")

        for glyph in self:
            glyph.glyphname = self.canonical_glyphname(glyph)

    @ property
    def fontname(self):
        return self.font.fontname

    @ property
    def version(self):
        return self.font.version

    @ property
    def em(self):
        return self.font.em

    @ property
    def os2_winascent(self):
        return self.font.os2_winascent

    @ property
    def os2_windescent(self):
        return self.font.os2_windescent


class _SbmuflMetadata(object):
    def __init__(self, font):
        self.font = font

    def asdict(self):
        d = {}
        d['fontName'] = self.font.fontname
        d['fontVersion'] = self.font.version

        d['metrics'] = {
            'winAscent': round(self.font.os2_winascent / self.font.em, 3),
            'winDescent': round(self.font.os2_windescent / self.font.em, 3)
        }

        anchors = self.anchors()
        if anchors:
            d['glyphsWithAnchors'] = anchors

        alternates = self.alternates()
        if alternates:
            d['glyphsWithAlternates'] = alternates

        advance_widths = self.advance_widths()
        if advance_widths:
            d['glyphAdvanceWidths'] = advance_widths

        optional_glyphs = self.optional_glyphs()
        if optional_glyphs:
            d['optionalGlyphs'] = optional_glyphs

        bounding_boxes = self.bounding_boxes()
        if bounding_boxes:
            d['glyphBBoxes'] = bounding_boxes

        ligatures = self.ligatures()
        if ligatures:
            d['ligatures'] = ligatures

        return d

    def anchors(self):
        all_anchors = {}

        for char in self.font:
            char_anchors = {}

            for anchor in char.anchorPoints:
                anchor_name = anchor[0]
                if anchor_name in SbmuflFont.valid_anchor_names:
                    x, y = (round((value / self.font.em), 3)
                            for value in anchor[2:4])
                    char_anchors[anchor_name] = (x, y)

            if char_anchors:
                char_name = self.font.canonical_glyphname(char)
                all_anchors[char_name] = char_anchors

        return all_anchors

    def alternates(self):
        all_alternates = {}

        for char in self.font:
            char_alternates = []

            for table in (table for table in char.getPosSub('*') if table[1] == 'AltSubs'):
                substitute_names = table[2:]
                for name in substitute_names:
                    substitute_char = self.font[name]
                    codepoint = SbmuflFont.format_codepoint(
                        substitute_char.unicode)
                    name = self.font.canonical_glyphname(
                        substitute_char)

                    char_alternates.append({
                        'codepoint': codepoint,
                        'name': name,
                    })

            if char_alternates:
                char_name = self.font.canonical_glyphname(char)
                char_alternates = {'alternates': char_alternates}
                all_alternates[char_name] = char_alternates

        return all_alternates

    def bounding_boxes(self):
        all_bounding_boxes = {}
        for char in self.font:
            char_name = self.font.canonical_glyphname(char)
            xmin, ymin, xmax, ymax = (
                round((value / self.font.em), 3) for value in char.boundingBox())
            bounding_box = {'bBoxNE': (xmax, ymax), 'bBoxSW': (xmin, ymin)}
            all_bounding_boxes[char_name] = bounding_box

        return all_bounding_boxes

    def ligatures(self):
        all_ligatures = {}
        for char in self.font:
            char_name = self.font.canonical_glyphname(char)

            for table in (table for table in char.getPosSub('*') if table[1] == 'Ligature'):
                component_names = [name for name in table[2:]]
                all_ligatures[char_name] = {
                    'codepoint': SbmuflFont.format_codepoint(char.unicode),
                    'componentGlyphs': component_names,
                }

        return all_ligatures

    def advance_widths(self):
        all_advance_widths = {}
        for char in self.font:
            char_name = self.font.canonical_glyphname(char)
            all_advance_widths[char_name] = round(char.width / self.font.em, 3)

        return all_advance_widths

    def optional_glyphs(self):
        all_optional_glyphs = {}
        for char in self.font:
            if (char.unicode >= 61439):
                char_name = self.font.canonical_glyphname(char)
                all_optional_glyphs[char_name] = {
                    'codepoint': SbmuflFont.format_codepoint(char.unicode),
                }

        return all_optional_glyphs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate font metadata")
    parser.add_argument("font_path", help="Relative path to font.sfd")
    parser.add_argument("glyphnames_path",
                        help="Relative path to glyphnames.json")
    args = parser.parse_args()
    with SbmuflFont(args.font_path, args.glyphnames_path) as font:
        font.export_metadata()
