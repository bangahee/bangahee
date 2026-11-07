# Many-koi garden banner

The original `pond-banner.png` is preserved. The README displays `many-koi-calm.gif`
above the garden sign, with the original still image as a reduced-motion fallback.

This twelve-second loop preserves each koi's original position, size, and
orientation. Independent short drifts stay within 13 pixels of the original
anchors. Each fish has separate, softly eased paddling bouts and rest periods,
with two or three slow tail strokes per loop instead of sixteen synchronized
strokes. The body wave relaxes during the pauses.
The existing water, waterfall, ripples, foliage, lantern light, and leaf animation
retain their six-second cadence. The camera stays fixed. The activity-driven koi
pond remains a separate daily-updated scene.

## Rebuild

Install `requirements-banner.txt`, then run `python scripts/render_banner.py`
from the repository root. The renderer uses a fixed palette and transparent
delta frames to keep the full-scene GIF compact. It verifies the loop endpoint.

The built-in image generation tool prepared `pond-clean.png` and
`koi-sprites.png`. The latter supplies the sprite alpha; colors come from the
original registered artwork so the koi retain their original markings.

## Image generation prompts

### Background plate

Edit target: the attached original Japanese pixel-art koi garden panorama. Create an animation clean background plate. REMOVE ONLY THE SIX KOI FISH from the water and seamlessly fill the exact fish-shaped gaps with matching water, reflections, and ripples. Keep every other feature pixel-for-pixel as close as possible: lantern, rocks, maple branches, flowers, lily pads, waterfall, bamboo spout, shore, light, perspective, palette, pixel-art style, and original panoramic framing. Do not redesign the scene or change composition. Preserve the 3:1 aspect ratio and the full original canvas. Keep the existing water and all static objects. Absolutely no fish anywhere after the edit. No added objects, no text. This will be the fixed background under independently moving versions of the original fish.

### Fish extraction

Edit target: attached original Japanese koi garden panorama. Create an animation sprite extraction plate with a TRUE TRANSPARENT background. KEEP ONLY THE SIX ORIGINAL KOI FISH, in exactly the same original positions, orientations, relative sizes, colors, markings and shapes. Remove all water, ripples, reflections, shadows, plants, stones, lantern, waterfall, leaves, and every other background element. Do not redesign or repaint the fish. Preserve the original full panoramic 3:1 canvas so the six fish remain registered to their original positions: upper-left white-red koi, upper-right gold koi, far-right white-black-red koi, center large white-red koi, lower-left gold-white koi, lower-right white-red koi. The six fish must remain spatially separated and surrounded by genuine alpha transparency. No grid, no frame, no checkerboard, no text, no additional fish.

### Edge cleanup

Edit target image 1 is a transparent cutout sheet of six koi. Reference image 2 is the original pond scene, for exact fish colors. Fix ONLY the erroneous bright pure-yellow and pure-red fringe pixels outside the fish silhouettes on image 1. Remove these colored matte/segmentation halos and stray dots to true alpha transparency. Keep all six fish, their positions, sizes, orientations, real red markings, gold scales and original artwork unchanged. The fish should have clean natural dark-gray pixel-art outlines, not neon yellow/red outlines. Preserve the exact full panoramic 3:1 canvas and true transparent background. No added background, no checkerboard, no text. This is a precise edge-cleanup edit for transparent animation sprites.
