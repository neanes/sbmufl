import argparse
import json
import re

import fontforge


def find_midpoint(glyph):
    min_y = float("inf")
    max_y = float("-inf")

    for contour in glyph.foreground:
        for point in contour:
            y = point.y
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y

    if min_y == float("inf") or max_y == float("-inf"):
        return None

    return (min_y + max_y) / 2


class SbmuflFont(object):
    valid_anchor_names = (
        "agogi",
        "agogiAboveFthora",
        "antikenoma",
        "apli",
        "barline",
        "barlineAboveFthora",
        "diesis",
        "diesisSecondary",
        "diesisTertiary",
        "endofonon",
        "fthoraTop",
        "fthoraTopSecondary",
        "fthoraTopTertiary",
        "fthoraBottom",
        "gorgonTop",
        "gorgonBottom",
        "gorgonSecondary",
        "isonIndicator",
        "heteron",
        "heteronConnecting",
        "klasmaTop",
        "klasmaBottom",
        "koronis",
        "martyriaTop",
        "martyriaBottom",
        "measureNumber",
        "modeTop",
        "noteTop",
        "omalon",
        "omalonConnecting",
        "psifiston",
        "stavros",
        "yfenAbove",
        "yfenBelow",
        "yfesis",
        "yfesisSecondary",
        "yfesisTertiary",
    )

    @staticmethod
    def format_codepoint(unicode_):
        return "U+" + hex(unicode_)[2:].upper()

    def canonical_glyphname(self, glyph, fallback=True):
        codepoint = SbmuflFont.format_codepoint(glyph.unicode)
        try:
            return self.codepoint_to_name[codepoint]
        except KeyError:
            if fallback:
                return glyph.glyphname
            raise ValueError(
                f"There's no SBMuFL character defined at codepoint {codepoint}."
            )

    def __init__(self, font_filepath, glyphnames_filepath="glyphnames.json", mode="w"):
        self.filepath = font_filepath
        self.font = fontforge.open(font_filepath)
        self.read_only = mode == "r"

        with open(glyphnames_filepath) as infile:
            glyphnames = json.load(infile)
            self.codepoint_to_name = {
                data["codepoint"]: name for name, data in glyphnames.items()
            }

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
            raise PermissionError("Font is opened in read-only mode.")
        self.font.save(*args)

    def close(self):
        self.font.close()

    def export_font(self, filename=None, *args, **kwargs):
        filename = filename or self.font.fontname + ".otf"
        self.font.generate(filename, *args, **kwargs)

    def export_metadata(self, filename=None, indent=2, **kwargs):
        filename = filename or (self.font.fontname + ".metadata.json").lower()

        with open(filename, "w") as outfile:
            json.dump(self.generate_metadata(), outfile, indent=indent, **kwargs)

    def generate_metadata(self):
        return _SbmuflMetadata(self).asdict()

    def rename_glyphs(self, warning=True):
        if warning:
            print(
                "SbmuflFont.rename_glyphs()\n"
                "Warning: Batch renaming glyphs can mess up your font files. "
                "Be sure to have a backup before using this method. "
                "You can disable this warning by adding `warning=False` to the argument list of this method:\n"
                "    `<your_font>.rename_glyphs(warning=False)`\n"
            )
            choice = input("Do you want to rename glyphs now anyway? (Y/N) > ")
            if not choice.upper() == "Y":
                print("Renaming aborted. Returning to call site.")
                return
            else:
                print("Continuing to rename glyphs.")

        for glyph in self:
            glyph.glyphname = self.canonical_glyphname(glyph)

    @property
    def fontname(self):
        return self.font.fontname

    @property
    def version(self):
        return self.font.version

    @property
    def em(self):
        return self.font.em

    @property
    def os2_winascent(self):
        return self.font.os2_winascent

    @property
    def os2_windescent(self):
        return self.font.os2_windescent

    @property
    def oligon_midpoint(self):
        return find_midpoint(self.font[0xE001])


class _SbmuflMetadata(object):
    def __init__(self, font):
        self.font = font

    def asdict(self):
        d = {}
        d["fontName"] = self.font.fontname
        d["fontVersion"] = self.font.version

        d["metrics"] = {
            "winAscent": round(self.font.os2_winascent / self.font.em, 3),
            "winDescent": round(self.font.os2_windescent / self.font.em, 3),
            "oligonMidpoint": round(self.font.oligon_midpoint / self.font.em, 3),
        }

        anchors = self.anchors()
        if anchors:
            d["glyphsWithAnchors"] = anchors

        alternates = self.alternates()
        if alternates:
            d["glyphsWithAlternates"] = alternates

        contextual_substitutions = self.contextual_substitutions()
        if contextual_substitutions:
            d["contextualSubstitutions"] = contextual_substitutions

        advance_widths = self.advance_widths()
        if advance_widths:
            d["glyphAdvanceWidths"] = advance_widths

        spacing = self.spacing()
        if spacing:
            d["glyphSpacing"] = spacing

        optional_glyphs = self.optional_glyphs()
        if optional_glyphs:
            d["optionalGlyphs"] = optional_glyphs

        bounding_boxes = self.bounding_boxes()
        if bounding_boxes:
            d["glyphBBoxes"] = bounding_boxes

        ligatures = self.ligatures()
        if ligatures:
            d["ligatures"] = ligatures

        return d

    def anchors(self):
        all_anchors = {}

        for char in self.font:
            char_anchors = {}

            for anchor in char.anchorPoints:
                anchor_name = anchor[0]
                if anchor_name in SbmuflFont.valid_anchor_names:
                    x, y = (round((value / self.font.em), 3) for value in anchor[2:4])
                    char_anchors[anchor_name] = (x, y)

            if char_anchors:
                char_name = self.font.canonical_glyphname(char)
                all_anchors[char_name] = char_anchors

        return all_anchors

    def alternates(self):
        all_alternates = {}

        for char in self.font:
            char_alternates = []

            for table in (
                table for table in char.getPosSub("*") if table[1] == "AltSubs"
            ):
                substitute_names = table[2:]
                for name in substitute_names:
                    substitute_char = self.font[name]
                    codepoint = SbmuflFont.format_codepoint(substitute_char.unicode)
                    name = self.font.canonical_glyphname(substitute_char)

                    char_alternates.append(
                        {
                            "codepoint": codepoint,
                            "name": name,
                        }
                    )

            if char_alternates:
                char_name = self.font.canonical_glyphname(char)
                char_alternates = {"alternates": char_alternates}
                all_alternates[char_name] = char_alternates

        return all_alternates

    def contextual_substitutions(self):
        with open(self.font.filepath) as infile:
            source = infile.read()

        subtable_to_lookup = {}
        for lookup in self.font.font.gsub_lookups:
            for subtable in self.font.font.getLookupSubtables(lookup):
                subtable_to_lookup[subtable] = lookup

        substitutions_by_lookup = {}
        for char in self.font.font.glyphs():
            for table in (
                table for table in char.getPosSub("*") if table[1] == "Substitution"
            ):
                lookup = subtable_to_lookup[table[0]]
                substitutions_by_lookup.setdefault(lookup, []).append(
                    {
                        "from": char.glyphname,
                        "to": table[2],
                    }
                )

        contextual_substitutions = []
        for match in re.finditer(
            r'^ChainSub2: class "[^"]+".*?^EndFPST$', source, re.MULTILINE | re.DOTALL
        ):
            block = match.group()
            input_classes = self._classes(block, "Class")
            backtrack_classes = self._classes(block, "BClass")
            lookahead_classes = self._classes(block, "FClass")

            for rule_match in re.finditer(
                r"^ \d+ \d+ \d+\n"
                r"  ClsList:(.*)\n"
                r"  BClsList:(.*)\n"
                r"  FClsList:(.*)\n"
                r" \d+\n"
                r"((?:  SeqLookup:.*\n)+)",
                block,
                re.MULTILINE,
            ):
                input_glyphs = self._glyphs_for_class_list(
                    input_classes, rule_match.group(1)
                )
                backtrack_glyphs = self._glyphs_for_class_list(
                    backtrack_classes, rule_match.group(2)
                )
                lookahead_glyphs = self._glyphs_for_class_list(
                    lookahead_classes, rule_match.group(3)
                )
                substitutions = []

                for index, lookup in re.findall(
                    r'^  SeqLookup: (\d+) "([^"]+)"$', rule_match.group(4), re.MULTILINE
                ):
                    substitutions.extend(
                        self._substitutions_for_rule(
                            substitutions_by_lookup, input_glyphs, index, lookup
                        )
                    )

                if substitutions:
                    contextual_substitutions.append(
                        {
                            "inputGlyphs": input_glyphs,
                            "backtrackGlyphs": backtrack_glyphs,
                            "lookaheadGlyphs": lookahead_glyphs,
                            "substitutions": substitutions,
                        }
                    )

        for match in re.finditer(
            r'^ContextSub2: glyph .*?(?=^(?:ContextSub2:|ChainSub2:|MarkAttachClasses:|DEI:)|\Z)',
            source,
            re.MULTILINE | re.DOTALL,
        ):
            block = match.group()

            for rule_match in re.finditer(
                r"^ String: \d+(.*)\n"
                r" BString: \d+(.*)\n"
                r" FString: \d+(.*)\n"
                r" \d+\n"
                r"((?:  SeqLookup:.*\n)+)",
                block,
                re.MULTILINE,
            ):
                input_glyphs = self._glyphs_for_glyph_list(rule_match.group(1))
                backtrack_glyphs = self._glyphs_for_glyph_list(rule_match.group(2))
                lookahead_glyphs = self._glyphs_for_glyph_list(rule_match.group(3))
                substitutions = []

                for index, lookup in re.findall(
                    r'^  SeqLookup: (\d+) "([^"]+)"$', rule_match.group(4), re.MULTILINE
                ):
                    substitutions.extend(
                        self._substitutions_for_rule(
                            substitutions_by_lookup, input_glyphs, index, lookup
                        )
                    )

                if substitutions:
                    contextual_substitutions.append(
                        {
                            "inputGlyphs": input_glyphs,
                            "backtrackGlyphs": backtrack_glyphs,
                            "lookaheadGlyphs": lookahead_glyphs,
                            "substitutions": substitutions,
                        }
                    )

        return contextual_substitutions

    @staticmethod
    def _substitutions_for_rule(substitutions_by_lookup, input_glyphs, index, lookup):
        index = int(index)
        return [
            {
                "index": index,
                **substitution,
            }
            for substitution in substitutions_by_lookup.get(lookup, [])
            if substitution["from"] in input_glyphs[index]
        ]

    @staticmethod
    def _classes(block, prefix):
        return [[]] + [
            line.split()[2:]
            for line in re.findall(rf"^  {prefix}:.*$", block, re.MULTILINE)
        ]

    @staticmethod
    def _glyphs_for_class_list(classes, class_list):
        return [classes[int(index)] for index in class_list.split()]

    @staticmethod
    def _glyphs_for_glyph_list(glyph_list):
        return [[glyph] for glyph in glyph_list.split()]

    def bounding_boxes(self):
        all_bounding_boxes = {}
        for char in self.font:
            char_name = self.font.canonical_glyphname(char)
            xmin, ymin, xmax, ymax = (
                round((value / self.font.em), 3) for value in char.boundingBox()
            )
            bounding_box = {"bBoxNE": (xmax, ymax), "bBoxSW": (xmin, ymin)}
            all_bounding_boxes[char_name] = bounding_box

        return all_bounding_boxes

    def ligatures(self):
        all_ligatures = {}
        for char in self.font:
            char_name = self.font.canonical_glyphname(char)

            for table in (
                table for table in char.getPosSub("*") if table[1] == "Ligature"
            ):
                component_names = [name for name in table[2:]]
                all_ligatures[char_name] = {
                    "codepoint": SbmuflFont.format_codepoint(char.unicode),
                    "componentGlyphs": component_names,
                }

        return all_ligatures

    def advance_widths(self):
        all_advance_widths = {}
        for char in self.font:
            char_name = self.font.canonical_glyphname(char)
            all_advance_widths[char_name] = round(char.width / self.font.em, 3)

        return all_advance_widths

    def spacing(self):
        spacing = {}

        for char in self.font:
            char_name = self.font.canonical_glyphname(char)

            # boundingBox returns:
            # (xmin, ymin, xmax, ymax)
            bbox = char.boundingBox()

            xmin, ymin, xmax, ymax = bbox

            # If there are no contours, skip
            if xmin == xmax and ymin == ymax:
                continue

            # Left whitespace:
            # distance from glyph origin (0) to leftmost contour
            before = xmin

            # Right whitespace:
            # distance from rightmost contour to glyph width
            after = char.width - xmax

            spacing[char_name] = {
                "leading": round(before / self.font.em, 3),
                "trailing": round(after / self.font.em, 3),
            }

        return spacing

    def optional_glyphs(self):
        all_optional_glyphs = {}
        for char in self.font:
            if char.unicode >= 61439:
                char_name = self.font.canonical_glyphname(char)
                all_optional_glyphs[char_name] = {
                    "codepoint": SbmuflFont.format_codepoint(char.unicode),
                }

        return all_optional_glyphs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate font metadata")
    parser.add_argument("font_path", help="Relative path to font.sfd")
    parser.add_argument("glyphnames_path", help="Relative path to glyphnames.json")
    args = parser.parse_args()
    with SbmuflFont(args.font_path, args.glyphnames_path) as font:
        font.export_metadata()
