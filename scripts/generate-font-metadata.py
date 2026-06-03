import argparse
import json
import os
import site
import sys
import tempfile
from pathlib import Path

import fontforge

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VENV_DIR = REPO_ROOT / ".venv"

site_packages = (
    VENV_DIR
    / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages"
)

if site_packages.exists():
    site.addsitedir(str(site_packages))

from fontTools.feaLib import ast
from fontTools.feaLib.parser import Parser


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
        with tempfile.NamedTemporaryFile(suffix=".fea", delete=False) as tmp:
            fea_path = tmp.name

        try:
            self.font.font.generateFeatureFile(fea_path)
            feature_file = Parser(fea_path).parse()
        finally:
            os.unlink(fea_path)

        substitutions_by_lookup = self._substitutions_by_lookup(feature_file)
        contextual_substitutions = []

        for statement in self._walk_statements(feature_file):
            if isinstance(statement, ast.ChainContextSubstStatement):
                input_glyphs = [self._glyph_set(g) for g in statement.glyphs]
                backtrack_glyphs = [self._glyph_set(g) for g in statement.prefix]
                lookahead_glyphs = [self._glyph_set(g) for g in statement.suffix]

                substitutions = []

                for index, lookups in enumerate(statement.lookups):
                    if not lookups:
                        continue

                    for lookup in lookups:
                        substitutions.extend(
                            self._substitutions_for_rule(
                                substitutions_by_lookup,
                                input_glyphs,
                                index,
                                lookup.name,
                            )
                        )

            elif isinstance(statement, ast.SingleSubstStatement):
                if not (statement.prefix or statement.suffix):
                    continue

                input_glyphs = [self._glyph_set(g) for g in statement.glyphs]
                backtrack_glyphs = [self._glyph_set(g) for g in statement.prefix]
                lookahead_glyphs = [self._glyph_set(g) for g in statement.suffix]
                substitutions = []

                for index, replacement in enumerate(statement.replacements):
                    from_glyphs = input_glyphs[index]
                    to_glyphs = self._glyph_set(replacement)

                    for from_glyph, to_glyph in zip(from_glyphs, to_glyphs):
                        substitutions.append(
                            {
                                "index": index,
                                "from": from_glyph,
                                "to": to_glyph,
                            }
                        )
            else:
                continue

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

    def _substitutions_by_lookup(self, node):
        substitutions_by_lookup = {}

        for statement in self._walk_statements(node):
            if not isinstance(statement, ast.LookupBlock):
                continue

            substitutions = []

            for lookup_statement in statement.statements:
                if not isinstance(lookup_statement, ast.SingleSubstStatement):
                    continue

                if lookup_statement.prefix or lookup_statement.suffix:
                    continue

                for index, replacement in enumerate(lookup_statement.replacements):
                    from_glyphs = self._glyph_set(lookup_statement.glyphs[index])
                    to_glyphs = self._glyph_set(replacement)

                    for from_glyph, to_glyph in zip(from_glyphs, to_glyphs):
                        substitutions.append(
                            {
                                "from": from_glyph,
                                "to": to_glyph,
                            }
                        )

            if substitutions:
                substitutions_by_lookup.setdefault(statement.name, []).extend(
                    substitutions
                )

        return substitutions_by_lookup

    def _walk_statements(self, node):
        for statement in getattr(node, "statements", []):
            yield statement
            yield from self._walk_statements(statement)

    @staticmethod
    def _glyph_set(glyph_expr):
        return sorted(glyph_expr.glyphSet())

    @staticmethod
    def _substitutions_for_rule(substitutions_by_lookup, input_glyphs, index, lookup):
        return [
            {
                "index": index,
                **substitution,
            }
            for substitution in substitutions_by_lookup.get(lookup, [])
            if substitution["from"] in input_glyphs[index]
        ]

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

        martyria_tick = self.font[0xE145]
        xmin, ymin, xmax, ymax = martyria_tick.boundingBox()
        martyria_tick_width = xmax - xmin

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

            # Hack to make the space to the left and right of martyria equal
            if char_name.startswith("martyriaNote"):
                before *= 0.80
                after = before

                if char_name.endswith("High"):
                    after -= martyria_tick_width

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
