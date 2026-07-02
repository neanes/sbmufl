import argparse
import json
import os
import site
import sys
import tempfile
from pathlib import Path

import fontforge
from generate_collision_regions import (
    generate_collision_regions_for_glyph,
    write_debug_svg,
)

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

collision_regions_dir = str(SCRIPT_DIR.parent / "sources" / "collision_regions")

DEFAULT_YPSILI_TOP_TOLERANCE_EM = 0.2
DEFAULT_YPSILI_MIN_HEIGHT_EM = 0.3

YPSILI_TOP_TOLERANCE_BY_FONT = {
    "Neanes": 0.2,
    "NeanesEngraving": 0.2,
    "NeanesRTL": 0.2,
    "NeanesRTLEngraving": 0.2,
    "NeanesStathisSeries": 0.35,
    "NeanesStathisSeriesEngraving": 0.35,
}

YPSILI_MIN_HEIGHT_BY_FONT = {
    "Neanes": 0.3,
    "NeanesEngraving": 0.3,
    "NeanesRTL": 0.3,
    "NeanesRTLEngraving": 0.2,
    "NeanesStathisSeries": 0.35,
    "NeanesStathisSeriesEngraving": 0.35,
}


def get_ypsili_top_tolerance_em(font):
    return YPSILI_TOP_TOLERANCE_BY_FONT.get(
        font.fontname,
        DEFAULT_YPSILI_TOP_TOLERANCE_EM,
    )


def get_ypsili_min_height_em(font):
    return YPSILI_MIN_HEIGHT_BY_FONT.get(
        font.fontname,
        DEFAULT_YPSILI_MIN_HEIGHT_EM,
    )


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


def contour_bbox(contour):
    xs = [p.x for p in contour]
    ys = [p.y for p in contour]

    if not xs:
        return None

    xmin = min(xs)
    ymin = min(ys)
    xmax = max(xs)
    ymax = max(ys)

    if xmin == xmax or ymin == ymax:
        return None

    return xmin, ymin, xmax, ymax


def create_temp_glyph_from_contours(font, source_glyph, contours, name):
    temp_glyph = font.createChar(-1, name)
    temp_glyph.clear()

    for contour in contours:
        temp_glyph.foreground += contour

    temp_glyph.width = source_glyph.width

    return temp_glyph


def get_highest_contours(
    glyph,
    font,
    tolerance_em=None,
    min_height_em=None,
):
    if tolerance_em is None:
        tolerance_em = get_ypsili_top_tolerance_em(font)

    if min_height_em is None:
        min_height_em = get_ypsili_min_height_em(font)

    contour_bboxes = []

    for contour in glyph.foreground:
        bbox = contour_bbox(contour)

        if bbox is None:
            continue

        contour_bboxes.append((contour, bbox))

    if not contour_bboxes:
        return []

    highest_ymax = max(bbox[3] for _, bbox in contour_bboxes)
    tolerance = font.em * tolerance_em
    min_height = font.em * min_height_em

    results = []

    for contour, bbox in contour_bboxes:
        xmin, ymin, xmax, ymax = bbox

        height = ymax - ymin

        near_top = highest_ymax - ymax <= tolerance
        tall_enough = height >= min_height

        if near_top and tall_enough:
            results.append(contour)

    return results


def generate_regions_for_ypsili_contours(font, source_glyph, contours):
    regions = []

    for index, contour in enumerate(contours, start=1):
        temp_name = f"{source_glyph.glyphname}.ypsiliCollisionTemp{index}"

        temp_glyph = create_temp_glyph_from_contours(
            font,
            source_glyph,
            [contour],
            temp_name,
        )

        contour_regions = generate_collision_regions_for_glyph(
            font,
            temp_glyph,
            slice_count=3,
            name=f"ypsili{index}",
        )

        regions.extend(contour_regions)

        font.removeGlyph(temp_name)

    return regions


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

        metadata = self.generate_metadata()

        font_dir = os.path.dirname(os.path.abspath(self.filepath))
        extra_filename = os.path.join(
            font_dir,
            f"{self.font.fontname.lower()}.extra.json",
        )
        if os.path.exists(extra_filename):
            with open(extra_filename, "r", encoding="utf-8") as infile:
                extra_metadata = json.load(infile)

            metadata.update(extra_metadata)

        with open(filename, "w", encoding="utf-8") as outfile:
            json.dump(metadata, outfile, indent=indent, **kwargs)

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
    def ascent(self):
        return self.font.ascent

    @property
    def descent(self):
        return self.font.descent

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
            "ascent": round(self.font.ascent / self.font.em, 3),
            "descent": round(self.font.descent / self.font.em, 3),
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

        optional_glyphs = self.optional_glyphs()
        if optional_glyphs:
            d["optionalGlyphs"] = optional_glyphs

        bounding_boxes = self.bounding_boxes()
        if bounding_boxes:
            d["glyphBBoxes"] = bounding_boxes

        collision_regions = self.collision_regions()
        if collision_regions:
            d["collisionRegions"] = collision_regions

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

    def collision_regions(self):
        all_regions = {}

        output_path = Path(collision_regions_dir) / self.font.fontname

        barline_region_glyphs = (
            "barlineTheseos",
            "barlineShortTheseos",
        )

        numbered_region_glyphs = (
            "oligon",
            "oligonKentimaMiddle",
            "oligonKentimaBelow",
            "oligonKentimaAbove",
            "oligonYpsiliRight",
            "oligonYpsiliLeft",
            "oligonKentimaYpsiliRight",
            "oligonKentimaYpsiliMiddle",
            "oligonDoubleYpsili",
            "oligonKentimataDoubleYpsili",
            "oligonKentimaDoubleYpsiliRight",
            "oligonKentimaDoubleYpsiliLeft",
            "oligonTripleYpsili",
            "oligonKentimataTripleYpsili",
            "oligonKentimaTripleYpsili",
            "oligonIson",
            "oligonApostrofos",
            "oligonYporroi",
            "oligonElafron",
            "oligonElafronApostrofos",
            "oligonChamili",
            "isonApostrofos",
            "apostrofos",
            "apostrofosSyndesmos",
            "yporroi",
            "elafron",
            "runningElafron",
            "elafronApostrofos",
            "chamili",
            "chamiliApostrofos",
            "chamiliElafron",
            "chamiliElafronApostrofos",
            "doubleChamili",
            "doubleChamiliApostrofos",
            "doubleChamiliElafron",
            "doubleChamiliElafronApostrofos",
            "tripleChamili",
            "petastiIson",
            "petasti",
            "petastiOligon",
            "petastiKentima",
            "petastiYpsiliRight",
            "petastiYpsiliLeft",
            "petastiKentimaYpsiliRight",
            "petastiKentimaYpsiliMiddle",
            "petastiDoubleYpsili",
            "petastiKentimataDoubleYpsili",
            "petastiKentimaDoubleYpsiliRight",
            "petastiKentimaDoubleYpsiliLeft",
            "petastiTripleYpsili",
            "petastiKentimataTripleYpsili",
            "petastiKentimaTripleYpsili",
            "petastiApostrofos",
            "petastiYporroi",
            "petastiElafron",
            "petastiRunningElafron",
            "petastiElafronApostrofos",
            "petastiChamili",
            "petastiChamiliApostrofos",
            "petastiChamiliElafron",
            "petastiChamiliElafronApostrofos",
            "petastiDoubleChamili",
            "petastiDoubleChamiliApostrofos",
            "kentima",
            "kentimata",
            "oligonKentimataBelow",
            "oligonKentimataAbove",
            "oligonIsonKentimata",
            "oligonKentimaMiddleKentimata",
            "oligonYpsiliRightKentimata",
            "oligonYpsiliLeftKentimata",
            "oligonApostrofosKentimata",
            "oligonYporroiKentimata",
            "oligonElafronKentimata",
            "oligonRunningElafronKentimata",
            "oligonElafronApostrofosKentimata",
            "oligonChamiliKentimata",
            "oligonKentimataBelow.alt01",
            "oligonKentimataAbove.alt01",
            "oligonKentimataBelow.alt02",
        )

        for char in self.font:
            char_name = self.font.canonical_glyphname(char)

            if (
                char_name not in barline_region_glyphs
                and char_name not in numbered_region_glyphs
            ):
                continue

            contour_bboxes = []

            for contour in char.foreground:
                xs = [p.x for p in contour]
                ys = [p.y for p in contour]

                if not xs:
                    continue

                xmin = min(xs)
                ymin = min(ys)
                xmax = max(xs)
                ymax = max(ys)

                # Skip degenerate regions
                if xmin == xmax or ymin == ymax:
                    continue

                contour_bboxes.append((contour, xmin, ymin, xmax, ymax))

            if not contour_bboxes:
                continue

            regions = []

            if char_name in barline_region_glyphs:
                highest_ymax = max(bbox[4] for bbox in contour_bboxes)

                for contour, xmin, ymin, xmax, ymax in contour_bboxes:
                    name = "yfen" if ymax == highest_ymax else "barline"

                    regions.append(
                        {
                            "name": name,
                            "bBoxNE": (
                                round(xmax / self.font.em, 3),
                                round(ymax / self.font.em, 3),
                            ),
                            "bBoxSW": (
                                round(xmin / self.font.em, 3),
                                round(ymin / self.font.em, 3),
                            ),
                        }
                    )

            else:
                ypsili_contours = []

                if "Ypsili" in char_name or "ypsili" in char_name:
                    ypsili_contours = get_highest_contours(char, self.font)

                region_index = 1

                for contour, xmin, ymin, xmax, ymax in contour_bboxes:
                    if contour in ypsili_contours:
                        continue

                    regions.append(
                        {
                            "name": f"{char_name}{region_index}",
                            "bBoxNE": (
                                round(xmax / self.font.em, 3),
                                round(ymax / self.font.em, 3),
                            ),
                            "bBoxSW": (
                                round(xmin / self.font.em, 3),
                                round(ymin / self.font.em, 3),
                            ),
                        }
                    )

                    region_index += 1

                if ypsili_contours:
                    ypsili_regions = generate_regions_for_ypsili_contours(
                        self.font.font,
                        char,
                        ypsili_contours,
                    )

                    regions.extend(ypsili_regions)

            all_regions[char_name] = regions

            svg_path = Path(output_path) / f"{char_name}.svg"

            write_debug_svg(
                self.font,
                char,
                regions,
                svg_path,
            )

        for glyph in [
            "digorgon",
            "digorgonDottedLeftBelow",
            "digorgonDottedLeftAbove",
            "digorgonDottedRight",
            "digorgonSecondary",
            "digorgonDottedLeftBelowSecondary",
            "digorgonDottedRightSecondary",
        ]:
            all_regions[glyph] = generate_collision_regions_for_glyph(
                self.font,
                self.font[glyph],
                slice_count=2,
                name=glyph,
                output_svg_path=output_path,
            )

        for glyph in [
            "trigorgon",
            "trigorgonDottedLeftBelow",
            "trigorgonDottedLeftAbove",
            "trigorgonDottedRight",
            "trigorgonSecondary",
            "trigorgonDottedLeftBelowSecondary",
            "trigorgonDottedRightSecondary",
        ]:
            all_regions[glyph] = generate_collision_regions_for_glyph(
                self.font,
                self.font[glyph],
                slice_count=3,
                name=glyph,
                output_svg_path=output_path,
            )

        return all_regions

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
