# SBMuFl Metadata

Several metadata files are available in JSON format [here](https://github.com/danielgarthur/sbmufl/tree/master/metadata).

## glyphnames.json

This file contains the canonical list of glyph names and their codepoints. Glyphs that have a counterpart in the Byzantine Music Symbols block range contain an `alternateCodepoint` indicating the official Unicode codepoint.

```js
{
    "ison": {
        "alternateCodepoint": "U+1D046",
        "codepoint": "U+E000"
    },
    "oligon": {
        "alternateCodepoint": "U+1D047",
        "codepoint": "U+E001"
    },
    ...
}
```

## classes.json

This file groups glyphs into various classes by type, function, base neume, orthographic rules, etc.

```js
{
    "acceptsGorgonBelow": [
        "ison",
        "oligon",
        "kentimata",
        "apostrofos",
        "elafron",
        "chamili"
    ],
    "kentimata": [
        "kentima",
        "kentimata",
        "oligonKentimataBelow",
        "oligonKentimataAbove",
        "oligonIsonKentimata",
        "oligonKentimataYpsiliLeft",
        "oligonKentimataYpsiliRight",
        "oligonApostrofosKentimata",
        "oligonYporroiKentimata",
        "oligonElafronKentimata",
        "oligonRunningElafronKentimata",
        "oligonElafronApostrofosKentimata",
        "oligonChamiliKentimata"
    ],
    ...
}
```

### Classes

This is a work in progress.

| Name                 | Description                                             |
| -------------------- | ------------------------------------------------------- |
| acceptsGorgonBelow   | Contains all glyphs that accept a gorgon below          |
| charactersOfAscent   | Contains all characters of ascent                       |
| charactersOfDescent  | Contains all characters of descent                      |
| charactersOfEquality | Contains all characters of equality                     |
| kentimata            | Contains all characters that contain kentimata          |
| oligon               | Contains all characters that have an oligon as the base |
| petasti              | Contains all characters that have a petasti as the base |

## ranges.json

This file defines the distinct ranges into which groups are organized.

```js
{
    ...
    "charactersOfTemporalDivision": {
        "description": "Characters of Temporal Division",
        "glyphs": [
            "gorgonAbove",
            "gorgonBelow",
            "gorgonDottedLeft",
            "gorgonDottedRight",
            "digorgon",
            "digorgonDottedLeftBelow",
            "digorgonDottedLeftAbove",
            "digorgonDottedRight",
            "trigorgon",
            "trigorgonDottedLeftBelow",
            "trigorgonDottedLeftAbove",
            "trigorgonDottedRight",
            "argon",
            "diargon",
            "triargon",
            "gorgonYporroi"
        ],
        "rangeStart": "U+E0F0",
        "rangeEnd": "U+E11F"
    },
    "charactersOfTempo": {
        "description": "Characters of Tempo",
        "glyphs": [
            "agogiPoliArgi",
            "agogiArgoteri",
            "agogiArgi",
            "agogiMetria",
            "agogiMesi",
            "agogiGorgi",
            "agogiGorgoteri",
            "agogiPoliGorgi"
        ],
        "rangeStart": "U+E120",
        "rangeEnd": "U+E12F"
    },
    ...
}
```
