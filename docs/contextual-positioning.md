# Contextual Mark Positioning

Some marks share the space directly above a base glyph. When a target mark, such
as an ison indicator, koronis, or primary/secondary fthora/chroa, sits above the
same syllable as one or more _stacking_ marks, the target must be raised far
enough to clear the tallest mark already present. For independent lower marks,
that means using the maximum of the single-mark raises. If one lower mark is
itself contextually raised, later targets must also account for that raised
position.

These raises are added to the generated OTFs by
`scripts/generate-contextual-positioning.py`, which is run from
`scripts/build.sh` after the SFD-to-OTF FontForge step. This page documents the
production contextual GPOS behavior, how it uses additive lookups and
corrections to express those raises, and what it assumes.

## Supported targets

The contextual positioning pass currently covers these above-mark collisions:

- Primary fthora/chroa marks are raised above klasma and primary gorgon-family
  marks.
- Secondary fthora/chroa marks are raised above secondary gorgon-family marks.
- Ison indicators are raised above klasma, primary gorgon-family,
  primary/secondary/tertiary fthora/chroa, and supported dependent fthora/chroa
  stacks.
- Koronis is raised above klasma, primary gorgon-family, primary fthora/chroa,
  and supported dependent fthora/chroa stacks.

Other neume and mark combinations continue to use the existing mark-to-base and
mark-to-mark positioning data. They are not claimed by this contextual pass
unless one of the target groups above is involved.

## Additive contextual rules

OpenType GPOS contextual rules are static pattern-action pairs. They cannot
compute `max()` at shape time, and mark-to-mark positioning cannot express these
collisions for all supported stacks. The generator therefore emits one
contextual lookup per supported axis, plus correction lookups for combined
cases. Because YPlacement from separate GPOS lookups is additive, the final
raise is the sum of every lookup that matches the glyph stream.

For a given base glyph, the generator computes the raise that each context mark
would require on its own, quantized upward onto a fixed 20-unit grid. The
rounding is always toward more clearance. It then groups marks with the same
computed raise and emits compact chained contextual GPOS Format 2 rules that
apply a shared SinglePos YPlacement to the target.

For ison indicators, the direct single-axis contexts list the base, one
supported context mark, and the target:

```text
[base] [klasma] | [ison indicator] @<klasma_ison_raise> |
[base] [gorgon] | [ison indicator] @<gorgon_ison_raise> |
[base] [fthora/chroa] | [ison indicator] @<fthora_ison_raise> |
```

For primary and secondary fthora/chroa marks, the target is also last:

```text
[base] [klasma] | [primary fthora/chroa] @<klasma_fthora_raise> |
[base] [gorgon] | [primary fthora/chroa] @<gorgon_fthora_raise> |
[base] [secondary gorgon] | [secondary fthora/chroa] @<secondary_gorgon_secondary_fthora_raise> |
```

For koronis, klasma precedes the target, while gorgon and fthora/chroa marks
follow the target:

```text
[base] [klasma] | [koronis] @<klasma_koronis_raise> |
[base] | [koronis] @<gorgon_koronis_raise> [gorgon] |
[base] | [koronis] @<fthora_koronis_raise> [fthora/chroa] |
```

Each contextual lookup uses a mark filtering set that contains only the marks
relevant to that lookup and its target. That lets the rule match through
unrelated marks that appear between the base and target in the normal rendering
order, while still requiring the relevant marks to be in that documented order.

## Independent max corrections

When two independent lower marks can both raise the same target, the single-axis
lookups intentionally both match. A correction lookup for the full stack then
subtracts the smaller raise:

```text
correction = -min(first_raise, second_raise)
```

The additive total is therefore the promised maximum:

```text
first_raise + second_raise + correction
= max(first_raise, second_raise)
```

The production generator applies this correction to the supported
klasma-plus-gorgon stacks for primary fthora/chroa marks, ison indicators, and
koronis.

## Combined corrections

Primary and secondary fthora/chroa marks are both targets and stacking marks. If
a fthora/chroa mark is raised above a preceding dependency mark, a later ison
indicator or koronis must clear the fthora/chroa mark at its raised position,
not its base-attached position.

The direct single-axis lookups would otherwise add independent raises:

```text
target_raise = dependency_target_raise + fthora_target_raise
```

For a dependency such as gorgon or klasma followed by a primary fthora/chroa
mark, the desired target raise is:

```text
target_raise = max(dependency_target_raise, fthora_target_raise) + fthora_raise
```

The generator reaches that value by adding a correction lookup:

```text
correction = fthora_raise - min(dependency_target_raise, fthora_target_raise)
```

So the additive total becomes:

```text
dependency_target_raise + fthora_target_raise + correction
= max(dependency_target_raise, fthora_target_raise) + fthora_raise
```

When the fthora/chroa mark is not itself raised, `fthora_raise` is zero and the
correction is negative; this is the case that turns two independent raises into
the maximum of the two. When the fthora/chroa mark is raised by the dependency,
the same formula also accounts for the fthora/chroa mark's new height.

Secondary fthora/chroa with secondary gorgon is simpler for ison indicators: the
secondary gorgon does not directly raise the ison indicator, so the combined
ison raise is:

```text
secondary_fthora_ison_raise + secondary_gorgon_secondary_fthora_raise
```

## Accuracy and assumptions

The generated rules are exact for the supported formulas above within the
quantized model validated by the build script. Upward grid quantization only
adds clearance. This is not a general-purpose collision engine for arbitrary
neume combinations; the implementation is limited to the target and dependency
sets listed on this page. The remaining assumptions bound which inputs are
supported:

- At most one primary gorgon, one secondary gorgon, and so on, as the notation
  requires.
- Matching depends on marks arriving in the order given by
  [Mark Rendering Order](README.md#mark-rendering-order). Fonts are not required
  to support alternate orderings for contextual collision handling; if a shaper
  emits marks out of order, no rule matches and the target is not raised.

## Build validation

The generator validates the generated OTF before saving it. It checks that each
contextual group shapes to the expected Y placement, that generated contextual
lookups use chained contextual GPOS Format 2, and that an already-processed font
is skipped instead of receiving duplicate lookups. The FontBakery profile run by
`test.sh` also exercises representative contextual shaping stacks across the
built fonts.
