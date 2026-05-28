# Standard Byzantine Music Font Layout (SBMuFL)

SBMuFL is a proposed standard for laying out a font that contains all the characters necessary to compose a score in modern Byzantine notation.

All characters would be mapped into the Private Use Area of the Unicode Basic Multilingual Plane and characters would be positioned using features of modern font technologies such as mark-to-base positioning.

## History and Rationale

There are currently several fonts in existence that were created for composing Byzantine music. Most of them were intended to be used in a word processor and they function by mapping the letter keys on a standard QWERTY keyboard to the musical symbols. Because of the quantity of symbols, this required multiple fonts to encompass all the characters. The exact mappings varied between the different fonts.

Other fonts have opted to use the [Byzantine Music Symbols](https://www.unicode.org/charts/PDF/U1D000.pdf) block range in Unicode. However, the Unicode code points only include the symbols in isolation. In order to compose Byzantine music, the symbols must be combined in various ways. Some fonts have attempted to use ligature substitution to allow users to type in the component symbols that would then be substituted by the font with the composite characters. However, there is no standard or obvious way to the order in which characters must be written in order to properly compose them. The order varies between fonts, and fonts often must resort to OpenType features such as `aalt` to expose the full list of characters.

Because of these inconsistencies, it is difficult to create music composition software that supports different fonts without introducing a cumbersome way of allowing the user to specify a mapping for custom fonts.

With a standard font layout, users would be able to easily interchange fonts.

The Private Use Area of the Unicode Basic Multilingual Plane contains 4096 code points, which is plenty of space to support all the characters used in Byzantine chant, including character combinations.

## Documentation

See the full documentation [here](https://neanes.github.io/sbmufl).

## Example

Example fonts are included in the `fonts` directory.

## Development

### Developing the Documentation

1. Install docsify.

```bash
npm i docsify-cli -g
```

2. Start docsify.

```bash
docsify serve docs
```

3. Navigate to http://localhost:3000 to view the docs.

4. Edit the Markdown files in the docs directory. The web page will automatically refresh as you make changes.
