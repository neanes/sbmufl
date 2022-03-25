# Font-specific Metadata

Each font can optionally provide a metadata file containing information that can help software use the font when OpenType features are not available.

All positions and widths are specified in ems.

## glyphsWithAnchors

This section contains the anchor points for all glyphs that contain anchors. If mark-to-base positioning is not available, marks can be positioned using the data in this section.

```js
{
  "glyphsWithAnchors": {
    "ison": {
      "measureNumber": [
        0.172,
        0.753
      ],
      "isonIndicator": [
        0.792,
        0.913
      ],
      "gorgonBottom": [
        0.713,
        0.173
      ],
      "heteron": [
        1.027,
        0.207
      ],
      "omalonConnecting": [
        1.471,
        0.133
      ],
      "omalon": [
        1.031,
        0.133
      ],
      "apli": [
        0.803,
        0.013
      ],
      "antikenoma": [
        0.82,
        0.165
      ],
      "noteTop": [
        0.314,
        0.676
      ],
      "fthoraBottom": [
        0.789,
        0.209
      ],
      "fthoraTop": [
        0.788,
        0.507
      ],
      "diesis": [
        0.4,
        0.133
      ],
      "yfesis": [
        1.316,
        0.619
      ],
      "psifiston": [
        0.84,
        0.113
      ],
      "klasmaTop": [
        0.793,
        0.487
      ],
      "gorgonTop": [
        0.786,
        0.505
      ]
    },
    ...
  },
  ...
}
```

## glyphsWithAlternates

This section lists the stylistic alternatives for each glyph that are available in the font.

```js
{
  ...
  "glyphsWithAlternates": {
    "modeFourth": {
      "alternates": [
        {
          "codepoint": "U+F004",
          "name": "modeFourth.salt01"
        }
      ]
    },
    "modeFirst": {
      "alternates": [
        {
          "codepoint": "U+F003",
          "name": "modeFirst.salt01"
        }
      ]
    },
    ...
  },
  ...
}
```

## glyphAdvanceWidths

This section contains the advance widths of all the glyphs.

```js
{
  ...
  "glyphAdvanceWidths": {
    "ison": 1.524,
    "oligonKentimaBelow": 1.515,
    "oligon": 1.515,
    "oligonKentimaAbove": 1.515,
    "oligonYpsiliRight": 1.515,
    "oligonYpsiliLeft": 1.515,
    "oligonYpsiliKentimaRight": 1.515,
    "oligonYpsiliKentimaMiddle": 1.515,
    "oligonDoubleYpsili": 1.515,
    "oligonDoubleYpsiliKentimata": 1.596,
    ...
  },
  ...
}
```

## glyphBBoxes

This section contains the bounding box of each glyph.

```js
{
    ...
    "glyphBBoxes": {
        "ison": {
            "bBoxNE": [
                1.438,
                0.6144705882351141
            ],
            "bBoxSW": [
                0.08198198198190983,
                0.219
            ]
        },
        ...
    },
    ...
}
```

## ligatures

This section contains the ligatures in the font and the component glyphs in the ligature. If OpenType ligature support is unavailable, this section can be used to implement ligatures.

```js
{
  ...
  "ligatures": {
    "oligonKentimaMiddle": {
      "codepoint": "U+E002",
      "componentGlyphs": [
        "oligon",
        "kentima"
      ]
    },
    "martyriaNoteNiHigh": {
      "codepoint": "U+E13F",
      "componentGlyphs": [
        "martyriaNoteNi",
        "martyriaTick"
      ]
    },
    ...
  },
  ...
}
```
