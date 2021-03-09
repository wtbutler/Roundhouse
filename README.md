# Roundhouse
Even more superior dice bot for Discord

It's basically
(Sidekick)[https://github.com/ArtemGr/Sidekick],
except it actually works *and* it's open source

## How to install

Follow this link:
www.google.com

Or, because this is open source, feel free to clone the repo and create your own version of it!

## Usage

### Basic Roll

`/r 2d6` - Roll two hexahedrons and sum them.

`/r 1d20` - Roll a 20 sided die.

`/r 1d20+5` - Roll with a modifier.

### Multiroll

Separate multiple rolls with a comma, each roll will appear on its own line.

`/r 1d20, 1d6` - Roll a 20 sided die and a 6 sided die separately.

`/r 1d20+5, 1d8+3` - Roll to hit, and roll damage at the same time.


### Repeat

The syntax for this one works both as `/r repeat(<rolls>, <X>)`, or `/r rpX <rolls>`,
and will roll `<rolls>` `<X>` times. Each roll will appear on its own line. If used in combination
with Multiroll, each cluster of rolls will be separated by a blank line.

`/r repeat (1d20+5, 2)` - Roll D&D 5e multiattack with a +5 modifier.

`/r rp2 1d20+5` - Roll D&D 5e multiattack with a +5 modifier.

`/r repeat (1d20+5, 2d6+3, 2)` - Roll D&D 5e multiattack and damage.

`/r rp2 1d20+5, 2d6+3` - Roll D&D 5e multiattack and damage.

### Drop dice

The syntax to drop dice is a basic roll followed by `k` (for keep) or `kl` (for keep lowest) or `kh`
(for keep highest, same as keep), followed by a number.

`/r 2d20k1 + 5` - Roll D&D 5e advantage.

`/r 2d20kl1 + 5` - Roll D&D 5e disadvantage.

`/r 4d6k3` - Roll 4d6 and keep the highest 3 (D&D 5e ability score roll).

`/r rp6 4d6k3` - Roll D&D 5e ability score 6 times (to generate a new character).

### Explode dice

Appending a `!` to a basic roll will cause it to explode when it rolls its max value. Exploding
means that it will keep that value, and roll another die as well. Exploding dice can continue
indefinitely if you're lucky enough. If you need to explode on more values, instead append either
`eXeN...` to explode on X or N, or append `e>N` to explode if the rolled value is greater than N.

`/r 7d10!` - Roll 7 10 sided dice, and roll another die for each ten that you roll.

`/r 5d6!` - Roll 5 6 sided dice, and roll another die for each six that you roll.

`/r 7d10e>=9` - Roll 7 10 sided dice, and roll another die for each nine or ten that you roll.

### Reroll dice

Appending a `r1` or `r<3` to a basic roll will cause it to reroll once if the first roll meets
the criteria. `r1r2r4` will reroll if the roll has a value of 1, 2, or 4. `r<3` will reroll if the
die has a value less than three.

`/r 1d20r1` - Roll a 20 sided die (because halflings are lucky)

`/r 2d6r<3+3` - Roll 2 six sided dice and reroll 1s and 2s, for example the D&D 5e Great Weapon
Fighting fighting style

`/r 8d6r<=2` - Roll 8 six sided dice and reroll 1s and 2s, for example casting D&D 5e Fireball
with the Elemental Adept (fire) feat

### Fate dice

`/r 4dF` - Roll [Fudge/Fate dice](http://rpg.stackexchange.com/questions/1765/what-game-circumstance-uses-fudge-dice) dice

`/r 4dF+2` - Roll Fudge/Fate dice with a modifier

### Count dice

Appending `>7` or `=10` or something else of the same variety to a basic roll or an exploded roll
will count the number of rolls that meet that criteria instead of summing the rolls. You can
(but don't need to) append a `t10` or `t>8` to count certain successes twice, and you can further
append a `f1` or `f<3` to add a failure condition. Failures and successes are counted separately,
but the result is the result of successes-failures.

`/r 3d10>=6f1` - oWoD roll, rolling a one is a failure, rolling more failures than successes is a *botch*

`/r 7d10!>7` - nWoD roll, tens explode, 8s and up are treated like a successes

`/r 1d10=10t10` - If a ten is rolled, count it twice

`/r 1d10>=8f1f2` - a one *or a two* is a failure

`/r 1d10>=8f<=2` - a one *or a two* is a failure

## Math

`/r (2+2)^3` - do math

`/r 3d6^2` - do math with dice

## Macros

## Other thing
