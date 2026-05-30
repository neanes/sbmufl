# Contextual Mark Positioning

Some marks share the space directly above a base glyph. When a target mark, such
as an ison indicator, koronis, or primary/secondary fthora/chroa, sits above the
same syllable as one or more _stacking_ marks, the target must be raised far
enough to clear the tallest mark already present. The correct raise is the
maximum of the raises that each present mark would require on its own; clearing
the tallest stack clears them all.

These raises are baked into the font sources as contextual GPOS rules by
`scripts/generate-contextual-positioning.py`. This page documents how those
rules express the maximum, and what they assume.

## Why static rules

OpenType GPOS contextual rules are static pattern-action pairs. They cannot
compute `max()` at shape time, and mark-to-mark positioning cannot express it
either. Instead, the generator enumerates winner rules such that, for ordinary
combinations of independent marks, exactly one rule fires and it carries the
correct maximum raise.

## Winner rules

Each stacking mark belongs to an _axis_. Ison indicators and koronis use klasma,
primary gorgon, primary fthora/chroa, secondary fthora/chroa, and tertiary
fthora/chroa as raising axes, with secondary gorgon as a pass-through axis.
Primary fthora/chroa marks use klasma and primary gorgon as raising axes, with
koronis and secondary gorgon as pass-through axes. Secondary fthora/chroa marks
use secondary gorgon as a raising axis, with koronis, primary gorgon, and
primary fthora/chroa as pass-through axes. Pass-through axes keep the contextual
pattern consecutive; they contribute a zero raise and cannot win.

For a given base glyph, the generator computes the raise that each candidate
mark would require on its own, quantized upward onto a fixed grid (so any
rounding is toward _more_ clearance, never less).

It then emits one rule per situation:

1. For each subset of axes that may be present together.
2. For each axis in that subset chosen as the winner.
3. For each raise value the winner axis can produce.

The subsets are sparse, not prefix-only: for example, a tertiary fthora/chroa
axis may appear without the primary or secondary axis. The rendering order
contract lets the generator emit each subset once, in canonical order, without
also generating alternate permutations.

A rule matches when:

- The winner axis carries a mark requiring _exactly_ that raise, and
- Every other axis in the subset carries a mark requiring _no more_ than that
  raise.

Ties are broken by mark order: among axes tied at the maximum raise, the first
one in rendering order wins. Axes earlier than the winner are required to be
_strictly_ below the maximum (otherwise they would be the winner); axes later
than the winner may equal it. This makes the rules mutually exclusive (no two
can match the same glyph sequence) so the result is the true maximum, never an
additive sum.

For ison indicators, the emitted context lists the base, then each axis's mark
glyphs in rendering order, then the target:

```text
[base] [klasma] [gorgon...] [fthora...] | [ison indicator] @<raise> |
```

For primary and secondary fthora/chroa marks, the emitted context follows the
same target-last pattern. Primary targets may include klasma, koronis, primary
gorgon, and secondary gorgon before the target; secondary targets may include
koronis, primary gorgon, secondary gorgon, and primary fthora/chroa before the
target:

```text
[base] [klasma] [koronis] [gorgon...] | [primary fthora/chroa] @<raise> |
[base] [koronis] [gorgon...] [primary fthora/chroa] | [secondary fthora/chroa] @<raise> |
```

For koronis, the target splits the context. Klasma precedes koronis and is
therefore backtrack context; gorgon and fthora/chroa marks follow koronis and
are input/lookahead context:

```text
[base] [klasma] | [koronis] @<raise> [gorgon...] [fthora...] |
```

Because a GPOS chain matches a consecutive run of glyphs, the rules are
self-selecting: a stream containing both a gorgon and an fthora matches only the
"{gorgon, fthora}" rule. The gorgon-only rule does not match, because the fthora
sits between the gorgon and the target. This is why every present-axis subset
must be represented explicitly, even though each subset is emitted only in
canonical order. There is no double application within a winner lookup.

## Dependent fthora correction

Primary and secondary fthora/chroa marks are both targets and stacking marks. If
a fthora/chroa mark is raised above a preceding dependency mark, a later ison
indicator or koronis must clear the fthora/chroa mark at its raised position,
not its base-attached position.

The normal winner rule still handles the independent stack, including
pass-through axes so contexts remain consecutive when non-raising marks sit
between a raising dependency and the target. The generator then adds a
correction lookup for contexts of the form:

```text
[base] [dependency marks...] [fthora/chroa] | [ison indicator] @<correction> |
[base] [dependencies before koronis] | [koronis] @<correction> [dependencies after koronis] [fthora/chroa] |
```

The correction lookup uses the same winner-rule construction over the fthora
dependency axes, then adds the winning fthora/chroa raise after the ordinary
target raise. For every valid dependency subset, the dependency that raises the
fthora/chroa target the most is the winner; earlier dependency axes must be
strictly below that raise and later axes may tie it. Pass-through axes, such as
secondary gorgon before a primary fthora/chroa mark, are emitted as zero-raise
non-winners so valid streams like "primary gorgon + secondary gorgon + primary
fthora" still match without allowing secondary gorgon to raise the primary
fthora/chroa mark. This additive correction guarantees clearance for supported
dependent fthora stacks, but it is not recomputed as a single max over the
already-raised fthora and every other independent axis. When another independent
axis already forced a larger ordinary raise, the dependent correction can leave
extra clearance.

## Accuracy and assumptions

For independent winner lookups, the raise value is exact within the quantized
model, not a heuristic: the winner construction always applies the true maximum
of the quantized per-mark requirements, and upward grid quantization only ever
adds clearance. Dependent fthora correction lookups are intentionally additive,
as described above. The remaining assumptions bound _which inputs are
supported_:

- At most one primary gorgon, one secondary gorgon, and so on, as the notation
  requires.
- Matching depends on marks arriving in the order given by
  [Mark Rendering Order](README.md#mark-rendering-order). Fonts are not required
  to support alternate orderings for contextual collision handling; if a shaper
  emits marks out of order, no rule matches and the target is not raised.
