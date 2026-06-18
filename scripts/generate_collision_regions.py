#!/usr/bin/env fontforge
# generate-collision-regions.py

import argparse
import json
import sys
import webbrowser
from pathlib import Path

import fontforge

MIN_REGION_AREA = 1
MERGE_GAP = 2


def rect_to_region(font, rect, name=None):
    xmin, ymin, xmax, ymax = rect

    region = {
        "bBoxNE": [round(xmax / font.em, 4), round(ymax / font.em, 4)],
        "bBoxSW": [round(xmin / font.em, 4), round(ymin / font.em, 4)],
    }

    if name is not None:
        region["name"] = name

    return region


def segment_x_at_y(x1, y1, x2, y2, y):
    if y1 == y2:
        return None

    t = (y - y1) / (y2 - y1)

    if t < 0 or t > 1:
        return None

    return x1 + t * (x2 - x1)


def collect_slice_xs(glyph, slice_ymin, slice_ymax):
    xs = []

    for contour in glyph.foreground:
        points = list(contour)

        if len(points) < 2:
            continue

        for i, p1 in enumerate(points):
            p2 = points[(i + 1) % len(points)]

            x1, y1 = p1.x, p1.y
            x2, y2 = p2.x, p2.y

            # Points inside the slice.
            if slice_ymin <= y1 <= slice_ymax:
                xs.append(x1)

            if slice_ymin <= y2 <= slice_ymax:
                xs.append(x2)

            seg_ymin = min(y1, y2)
            seg_ymax = max(y1, y2)

            # Segment does not touch this slice.
            if seg_ymax < slice_ymin or seg_ymin > slice_ymax:
                continue

            # Horizontal segment inside/touching the slice.
            if y1 == y2:
                if slice_ymin <= y1 <= slice_ymax:
                    xs.extend([x1, x2])
                continue

            # Intersections with slice boundaries.
            x_at_min = segment_x_at_y(x1, y1, x2, y2, slice_ymin)
            x_at_max = segment_x_at_y(x1, y1, x2, y2, slice_ymax)

            if x_at_min is not None:
                xs.append(x_at_min)

            if x_at_max is not None:
                xs.append(x_at_max)

            # Intersection with slice midpoint helps with diagonal/curvy-ish shapes.
            y_mid = (slice_ymin + slice_ymax) / 2
            x_at_mid = segment_x_at_y(x1, y1, x2, y2, y_mid)

            if x_at_mid is not None:
                xs.append(x_at_mid)

    return xs


def merge_similar_rects(rects, gap=MERGE_GAP):
    if not rects:
        return []

    rects = sorted(rects, key=lambda r: (r[1], r[0]))
    merged = [rects[0]]

    for rect in rects[1:]:
        x0, y0, x1, y1 = rect
        px0, py0, px1, py1 = merged[-1]

        vertically_touching = y0 <= py1 + gap
        similar_left = abs(x0 - px0) <= gap
        similar_right = abs(x1 - px1) <= gap

        if vertically_touching and similar_left and similar_right:
            merged[-1] = (
                min(px0, x0),
                min(py0, y0),
                max(px1, x1),
                max(py1, y1),
            )
        else:
            merged.append(rect)

    return merged


def generate_collision_regions_for_glyph(
    font,
    glyph,
    slice_count=3,
    name=None,
    output_svg_path=None,
):
    """
    Import this from another FontForge script.

    Example:
        from generate_collision_regions import generate_collision_regions_for_glyph

        regions = generate_collision_regions_for_glyph(
            self.font,
            self.font["trigorgon"],
            slice_count=3,
            name="gorgon",
        )
    """
    xmin, ymin, xmax, ymax = glyph.boundingBox()

    if xmin == xmax or ymin == ymax:
        return []

    height = ymax - ymin
    slice_height = height / slice_count

    rects = []

    for i in range(slice_count):
        slice_ymin = ymin + i * slice_height
        slice_ymax = ymax if i == slice_count - 1 else ymin + (i + 1) * slice_height

        xs = collect_slice_xs(glyph, slice_ymin, slice_ymax)

        if not xs:
            continue

        rxmin = min(xs)
        rxmax = max(xs)

        if rxmin == rxmax:
            continue

        area = (rxmax - rxmin) * (slice_ymax - slice_ymin)

        if area < MIN_REGION_AREA:
            continue

        rects.append((rxmin, slice_ymin, rxmax, slice_ymax))

    rects = merge_similar_rects(rects)

    regions = []

    for i, rect in enumerate(rects):
        region_name = None

        if name is not None:
            region_name = name if len(rects) == 1 else f"{name}{i + 1}"

        regions.append(rect_to_region(font, rect, region_name))

    if output_svg_path:
        write_debug_svg(font, glyph, regions, Path(output_svg_path) / f"{name}.svg")

    return regions


def generate_collision_regions(
    font,
    glyph_name,
    slice_count=3,
    name=None,
    output_svg_path=None,
):
    return generate_collision_regions_for_glyph(
        font,
        font[glyph_name],
        slice_count=slice_count,
        name=name,
        output_svg_path=output_svg_path,
    )


def write_debug_svg(font, glyph, regions, output_path):
    xmin, ymin, xmax, ymax = glyph.boundingBox()
    width = xmax - xmin
    height = ymax - ymin
    pad = font.em * 0.05

    view_x = xmin - pad
    view_y = -ymax - pad
    view_width = width + pad * 2
    view_height = height + pad * 2

    def svg_y(y):
        return -y

    path_parts = []

    for contour in glyph.foreground:
        points = list(contour)

        if not points:
            continue

        first = points[0]
        path_parts.append(f"M {first.x} {svg_y(first.y)}")

        for p in points[1:]:
            path_parts.append(f"L {p.x} {svg_y(p.y)}")

        path_parts.append("Z")

    path_data = " ".join(path_parts)

    region_rects = []

    for region in regions:
        sw_x, sw_y = region["bBoxSW"]
        ne_x, ne_y = region["bBoxNE"]

        rx = sw_x * font.em
        ry = ne_y * font.em
        rw = (ne_x - sw_x) * font.em
        rh = (ne_y - sw_y) * font.em

        region_rects.append(
            f'<rect x="{rx}" y="{svg_y(ry)}" '
            f'width="{rw}" height="{rh}" '
            f'fill="none" stroke="red" stroke-width="{font.em * 0.01}" />'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
  viewBox="{view_x} {view_y} {view_width} {view_height}">
  <rect x="{view_x}" y="{view_y}" width="{view_width}" height="{view_height}" fill="white"/>
  <path d="{path_data}" fill="black" fill-opacity="0.25" stroke="black" stroke-width="{font.em * 0.004}"/>
  {''.join(region_rects)}
</svg>
"""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("font_path")
    parser.add_argument("glyph_name")
    parser.add_argument("slice_count", nargs="?", type=int, default=3)

    parser.add_argument("--name", default=None)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--out", help="Write debug SVG to this path.")

    return parser.parse_args()


def main():
    args = parse_args()

    font = fontforge.open(args.font_path)

    if args.glyph_name not in font:
        print(f"Glyph not found: {args.glyph_name}", file=sys.stderr)
        sys.exit(1)

    glyph = font[args.glyph_name]

    regions = generate_collision_regions_for_glyph(
        font,
        glyph,
        slice_count=args.slice_count,
        name=args.name,
    )

    print(
        json.dumps(
            {"collisionRegions": {args.glyph_name: regions}},
            indent=2,
        )
    )

    if args.out or args.show:
        output_path = args.out or f"{args.glyph_name}-collision-regions.svg"
        write_debug_svg(font, glyph, regions, output_path)

        print(f"Wrote debug SVG: {output_path}", file=sys.stderr)

        if args.show:
            webbrowser.open(Path(output_path).resolve().as_uri())


if __name__ == "__main__":
    main()
