<link rel="stylesheet" href="tables/tables.css" />

# Ison Indicators (U+E260 - U+E27F)

<table>
<tr>
    <td>
        <span class="neanes">&#xE260;</span>
    </td>
    <td>
        <div class="code-point">
            U+E260
        </div>
        <div class="glyph-name">
            isonIndicatorUnison
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE261;</span>
    </td>
    <td>
        <div class="code-point">
            U+E261
        </div>
        <div class="glyph-name">
            isonIndicatorDiLow
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE262;</span>
    </td>
    <td>
        <div class="code-point">
            U+E262
        </div>
        <div class="glyph-name">
            isonIndicatorKeLow
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE263;</span>
    </td>
    <td>
        <div class="code-point">
            U+E263
        </div>
        <div class="glyph-name">
            isonIndicatorZo
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE264;</span>
    </td>
    <td>
        <div class="code-point">
            U+E264
        </div>
        <div class="glyph-name">
            isonIndicatorNi
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE265;</span>
    </td>
    <td>
        <div class="code-point">
            U+E265
        </div>
        <div class="glyph-name">
            isonIndicatorPa
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE266;</span>
    </td>
    <td>
        <div class="code-point">
            U+E266
        </div>
        <div class="glyph-name">
            isonIndicatorVou
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE267;</span>
    </td>
    <td>
        <div class="code-point">
            U+E267
        </div>
        <div class="glyph-name">
            isonIndicatorGa
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE268;</span>
    </td>
    <td>
        <div class="code-point">
            U+E268
        </div>
        <div class="glyph-name">
            isonIndicatorDi
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE269;</span>
    </td>
    <td>
        <div class="code-point">
            U+E269
        </div>
        <div class="glyph-name">
            isonIndicatorKe
        </div>
    </td>
</tr>
<tr>
    <td>
        <span class="neanes">&#xE26A;</span>
    </td>
    <td>
        <div class="code-point">
            U+E26A
        </div>
        <div class="glyph-name">
            isonIndicatorZoHigh
        </div>
    </td>
</tr>
</table>

## Implementation Details

Ison indicators should be treated as marks and positioned using the Mark-to-Base Attachment Positioning Subtable (GPOS Lookup Type 4). Tall Ypsili bases use a midpoint compromise between the ison reference height and the base-outline clearance height. When stacked after above-attaching gorgon, digorgon, trigorgon, fthora, or chroa marks, later contextual GPOS rules raise only the ison indicator while preserving the base glyph's isonIndicator X anchor. Contextual raises follow the documented mark order, are rounded up to a 20-unit grid, and are grouped so each ordered context applies the maximum required clearance directly.

</body></html>
