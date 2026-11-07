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
The README displays `koi/private-pond.gif`; `koi/pond.gif` is an identical
compatibility copy for existing references. A still is supplied for reduced
motion. Local `koi/private-pond-review.jpg` is a visual QA contact sheet.

The renderer verifies the environment's seamless loop, independent background
motion, GIF frame count and timing, and decoded GIF frames without trails.
