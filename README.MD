# Standard Byzantine Music Font Layout (SBMuFL)

SBMuFL is a proposed standard for laying out a font that contains all the characters necessary to compose a score in modern Byzantine notation.

All characters would be mapped into the Private Use Area of the Unicode Basic Multilingual Plane and characters would be positioned using features of modern font technologies such as mark-to-base positioning.

## History and Rationale

There are currently several fonts in existence that were created for composing Byzantine music. Most of them were intended to be used in a word processor and they function by mapping the letter keys on a standard QWERTY keyboard to the musical symbols. Because of the quantity of symbols, this required multiple fonts to encompass all the characters. The exact mappings varied between the different fonts.

Other fonts have opted to use the [Byzantine Music Symbols](https://www.unicode.org/charts/PDF/U1D000.pdf) block range in Unicode. However, the Unicode code points only include the symbols in isolation. In order to compose Byzantine music, the symbols must be combined in various ways. Some fonts have attempted to use ligature substitution to allow users to type in the component symbols that would then be substituted by the font with the composite characters. However, there is no standard or obvious way to the order in which characters must be written in order to properly compose them. The order varies between fonts, and fonts often must resort to OpenType features such as `aalt` to expose the full list of characters.

Because of these inconsistencies, it is difficult to create music composition software that supports different fonts without introducing a cumbersome way of allowing the user to specify a mapping for custom fonts.

With a standard font layout, users would be able to easily interchange fonts.

The Private Use Area of the Unicode Basic Multilingual Plane contains 4096 code points, which is plenty of space to support all the characters used in Byzantine chant, including character combinations.

## Organization

Each category contains extra unused space to allow for future expansion.

| Category                            | Start  | End    |
| ----------------------------------- | ------ | ------ |
| Characters of Quantity              | U+E000 | U+E09F |
| Characters of Quality               | U+E0A0 | U+E0CF |
| Characters of Temporal Augmentation | U+E0D0 | U+E0EF |
| Characters of Temporal Division     | U+E0F0 | U+E11F |
| Characters of Tempo                 | U+E120 | U+E12F |
| Martyria of the Notes               | U+E130 | U+E18F |
| Signs of Alteration                 | U+E190 | U+E20F |
| Characters of Rhythm                | U+E210 | U+E24F |
| Note Indicators                     | U+E250 | U+E25F |
| Ison Indicators                     | U+E260 | U+E27F |
| Letters                             | U+E280 | U+E29F |
| Martyria of the Tones               | U+E2A0 | U+E42F |
| Reserved for Future Use             | U+E430 | U+EFFF |
| Free Space                          | U+F000 | U+FFFF |

## List of Glyphs

See the [full list of glyphs](./docs/glyph_table.md). This list does not currently render correctly within Github's website. TODO: move this table to a separate webpage.

## Example

An example font is included in the `fonts` directory.

## Guidelines

This section contains guidelines on how to implement a SBMuFL-compatible OpenType font.

UNDER CONSTRUCTION

### Characters of Quality

Characters of quality should be treated as marks and positioned using the Mark-to-Base Attachment Positioning Subtable (GPOS Lookup Type 4).

Certain qualitative characters may either appear below a single quantitative character, or appear between two quantative characters, functioning as a tie. These characters should be implemented as separate glyphs with separate anchor points.

### Characters of Temporal Augmentation

Characters of temporal augmentation should be treated as marks and positioned using the Mark-to-Base Attachment Positioning Subtable (GPOS Lookup Type 4).

Some signs can appear both above and a below a quantitative character, and so two versions of the signs must be included in the layout.

### Characters of Temporal Division

Characters of temporal division should be treated as marks and positioned using the Mark-to-Base Attachment Positioning Subtable (GPOS Lookup Type 4).

Some signs can appear both above and a below a quantitative character, and so two versions of the signs must be included in the layout.

### Martyria of the Notes

A martyrium consists of two signs: a letter indicating the note and a martyrical sign.

The note letter should be treated as a normal glyph, while the martyrical sign should be treated as a mark and positioned using the Mark-to-Base Attachment Positioning Subtable (GPOS Lookup Type 4).

Since the note letter may appear on either the top or the bottom of the martyrium, the layout contains both top and bottom version of the notes, as well as top and bottom versions of the martyrial signs.
