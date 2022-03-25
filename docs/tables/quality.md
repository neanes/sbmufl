<link rel="stylesheet" href="tables/tables.css" />

# Characters of Quality (U+E0A0 - U+E0CF)

These characters are sometimes referred to as hypostases or mutes.

<table>
<tr>
    <td>
        <span class="neanes">&#xE0A0</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A0
        </div>
        <div class="glyph-name">
            vareia
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0A1</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A1
        </div>
        <div class="glyph-name">
            psifiston
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0A2</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A2
        </div>
        <div class="glyph-name">
            antikenoma
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0A3</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A3
        </div>
        <div class="glyph-name">
            omalon
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0A4</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A4
        </div>
        <div class="glyph-name">
            omalonConnecting
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0A5</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A5
        </div>
        <div class="glyph-name">
            heteron
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0A6</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A6
        </div>
        <div class="glyph-name">
            heteronConnecting
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0A7</span>
    </td>
    <td>
        <div class="code-point">
            U+E0A7
        </div>
        <div class="glyph-name">
            endofonon
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0B0</span>
    </td>
    <td>
        <div class="code-point">
            U+E0B0
        </div>
        <div class="glyph-name">
            yfenAbove
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0B1</span>
    </td>
    <td>
        <div class="code-point">
            U+E0B1
        </div>
        <div class="glyph-name">
            yfenBelow
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0C0</span>
    </td>
    <td>
        <div class="code-point">
            U+E0C0
        </div>
        <div class="glyph-name">
            stavros
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE0C1</span>
    </td>
    <td>
        <div class="code-point">
            U+E0C1
        </div>
        <div class="glyph-name">
            breath
        </div>
    </td>
</tr>
</table>

## Implementation Details

Characters of quality should be treated as marks and positioned using the Mark-to-Base Attachment Positioning Subtable (GPOS Lookup Type 4).

Certain qualitative characters may either appear below a single quantitative character, or appear between two quantative characters, functioning as a tie. These characters should be implemented as separate glyphs with separate anchor points.

Ties should be written between the characters that are being tied.

`ison` + `omalonConnecting` + `ison`

</body></html>
