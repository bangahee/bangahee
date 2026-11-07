# The activity koi's iris cove

The git-koi resident now has a sheltered side pool in the same pixel-art garden.
A wooden footbridge, curving stepping stones, violet irises, and a creek-fed
inlet distinguish this setting from the large six-koi pond above it.

`pond-cove-background.png` was created with the built-in imagegen tool. The
original pond background and banner were used as edit and style references.
The exact prompt is recorded in `pond-cove-image-prompt.txt`.

`render_cove.py` animates the environment independently of the activity koi:
water refraction and caustics, moving water in the cascade, expanding inlet
ripples, and gently swaying reeds and willow foliage. The wooden bridge and
stone shores stay still. The original `koi/koi.gif` remains the source of the
resident's appearance, movement, and frame timing.

Run `python render_cove.py` after installing `requirements-pond.txt` and
generating the activity koi. The daily Koi workflow runs these same steps.
The README displays `koi/private-pond-maple.gif`; `koi/private-pond.gif` and
`koi/pond.gif` are identical compatibility copies for existing references. A still is supplied for reduced
motion. Local `koi/private-pond-review.jpg` is a visual QA contact sheet.

The renderer verifies the environment's seamless loop, independent background
motion, GIF frame count and timing, and decoded GIF frames without trails.

## Foreground maple breeze

The cove shares the top banner’s six textured maple sprites and wind-driven
tumbling renderer from `scripts/render_maple.py`. Leaves are composited above
the koi and scenery. Complete native koi cycles repeat under a slower leaf
loop, preserving the fish and water speed. The current source produces a
12-second, 180-frame loop. The daily workflow regenerates the effect too.
