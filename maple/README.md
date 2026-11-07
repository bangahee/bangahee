# Maple breeze

A seamless autumn-leaf animation for bangahee's little garden. Six textured
maple leaves in crimson, vermilion, amber, copper, orange, and burgundy drift
with lateral sway and edge-on tumbling.

## Profile integration

The profile README adds `maple/maple-breeze.gif` as a transparent leaf strip,
with `maple/maple-still.png` as the reduced-motion fallback. It sits beneath
the garden notes, keeping the activity-driven koi pond intact. Transparency
lets the strip blend with both GitHub light and dark themes.

GitHub profile READMEs display image animations but cannot run JavaScript or
position a particle overlay across the whole page. The effect stays inside
its image area.

To put this on the live profile, upload `maple-breeze.gif` and `maple-still.png`
into a `maple/` folder in the `bangahee/bangahee` repository, then add the
picture block from the updated root README. No GitHub Action, external
service, or API key is needed for playback.

`pond-maple-breeze.gif` is an alternative with the same leaves floating over
the original static pond banner. It is provided as a preview/alternative;
the README keeps the activity-driven pond.

## Recreate or tune

Install Pillow, then run `python scripts/render_maple.py` from the project
directory. Both GIFs loop for 12 seconds at 20 frames per second. Change
`make_leaves` counts, `size`, `drift`, or `sway` in the script to adjust the
effect. A fixed seed makes the result reproducible. The renderer verifies
frame count, duration, and the seamless loop endpoint.

`leaves-atlas.png` is the original transparent six-leaf asset generated with
the built-in imagegen tool. `poster.png` and `animation-review.jpg` are local
review artifacts. `image-prompt.txt` records the exact generation prompt.
