import fontforge
from pathlib import Path

font = fontforge.open("../fonts/Neanes.otf")


for glyph in (char for char in font.glyphs() if 57344 <= char.unicode <= 63743):
    name = glyph.glyphname
    filename = f"images/{name}/{name}_image_1.png"

    Path(f"images/{name}").mkdir(parents=True, exist_ok=True)

    font[name].export(filename, 28)
