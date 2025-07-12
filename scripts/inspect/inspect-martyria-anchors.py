import fontforge
import sys

# --- Settings ---
sfd_path = "../../sources/Neanes.sfd"
glyph_names = [
    "martyriaNoteZo",
    "martyriaNoteNi",
    "martyriaNotePa",
    "martyriaNoteVou",
    "martyriaNoteGa",
    "martyriaNoteDi",
    "martyriaNoteKe",
    # "martyriaNoteZoHigh",
    # "martyriaNoteNiHigh",
    # "martyriaNotePaHigh",
    # "martyriaNoteVouHigh",
    # "martyriaNoteGaHigh",
    # "martyriaNoteDiHigh",
    # "martyriaNoteKeHigh",
]
anchor_name = "fthoraTop"


def toDisplay(value, em):
    return round((value / em), 3)


# --- Load font ---
font = fontforge.open(sfd_path)

for glyph_name in glyph_names:
    if glyph_name not in font:
        print(f"Glyph '{glyph_name}' not found in the font.")
        sys.exit(1)

    glyph = font[glyph_name]

    # --- Find highest Y point in contours ---
    highest_y = None

    print(len(glyph.foreground))

    for contour in glyph.foreground:
        for point in contour:
            if highest_y is None or point.y > highest_y:
                highest_y = point.y

    if highest_y is None:
        print("No contours found in the glyph.")
        sys.exit(1)

    # --- Find anchor position ---
    anchor_found = False
    for anchor in glyph.anchorPoints:
        name, anchor_type, x, y = anchor
        if name == anchor_name:
            anchor_found = True
            anchor_x = x
            anchor_y = y
            break

    if not anchor_found:
        print(f"Anchor '{anchor_name}' not found in glyph '{glyph_name}'.")
        sys.exit(1)

    # --- Compute vertical distance ---
    vertical_distance = anchor_y - highest_y

    print(f"Glyph: {glyph_name}")
    print(f"Highest point Y: {toDisplay(highest_y, font.em)}")
    print(f"Anchor '{anchor_name}' Y: {toDisplay(anchor_y, font.em)}")
    print(
        f"Vertical distance (anchor - highest): {toDisplay(vertical_distance, font.em)}"
    )
