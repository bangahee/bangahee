"""Render the profile's seamless maple breeze. Requires Pillow >= 10.

Run from any directory: python scripts/render_maple.py
The original banner stays intact. No network access is needed.
"""

from pathlib import Path
import math
import random

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1080, 360
FPS, SECONDS = 20, 12
FRAMES = FPS * SECONDS
TAU = math.tau


def load_sprites():
    atlas = Image.open(ROOT / 'maple/leaves-atlas.png').convert('RGBA')
    cell_w, cell_h = atlas.width // 3, atlas.height // 2
    sprites = []
    for row in range(2):
        for col in range(3):
            tile = atlas.crop((col * cell_w, row * cell_h,
                               (col + 1) * cell_w, (row + 1) * cell_h))
            tile = tile.crop(tile.getchannel('A').getbbox())
            tile.thumbnail((160, 160), Image.Resampling.LANCZOS)
            sprites.append(tile)
    return sprites


def make_leaves(count, height):
    rng = random.Random(714)
    leaves = []
    for i in range(count):
        # Stratified positions keep the whole width gently populated.
        leaves.append(dict(
            x=(i + rng.random()) / count * WIDTH,
            phase=rng.random(), size=rng.uniform(26, 51),
            angle=rng.uniform(0, 360), turns=rng.choice([-1, 1]),
            drift=rng.uniform(85, 180), sway=rng.uniform(12, 28),
            sprite=i % 6, height=height,
        ))
    return leaves


def render(t, leaves, sprites, backdrop=None, height=HEIGHT):
    frame = (backdrop.copy() if backdrop is not None else
             Image.new('RGBA', (WIDTH, height), (0, 0, 0, 0)))
    for leaf in leaves:
        q = (t / SECONDS + leaf['phase']) % 1
        # Wrap only beyond the image edges: no visible mid-air respawning.
        y = -90 + q * (height + 180)
        x = (leaf['x'] + leaf['drift'] * q
             + leaf['sway'] * math.sin(TAU * (2*q + leaf['phase']))
             + 9 * math.sin(TAU * t / SECONDS))
        x = (x + 90) % (WIDTH + 180) - 90
        angle = (leaf['angle'] + leaf['turns'] * 360 * q
                 + 14 * math.sin(TAU * 2*q))
        # An edge-on turn followed by a full face gives a fluttering tumble.
        foreshorten = 0.20 + 0.80 * abs(math.cos(TAU * q + leaf['phase'] * TAU))
        source = sprites[leaf['sprite']]
        size = leaf['size'] * (0.94 + 0.06 * math.sin(TAU*q))
        sh = round(size * source.height / source.width)
        sprite = source.resize((max(2, round(size * foreshorten)), sh),
                               Image.Resampling.LANCZOS)
        sprite = sprite.rotate(angle, resample=Image.Resampling.BICUBIC,
                               expand=True)
        frame.alpha_composite(sprite, (round(x - sprite.width/2),
                                       round(y - sprite.height/2)))
    return frame


def encode_gif(path, leaves, sprites, backdrop=None, height=HEIGHT):
    # A fixed global palette keeps the static pond stable between frames.
    samples = Image.new('RGB', (WIDTH, height * 4), '#172c26')
    for i in range(4):
        frame = render(i * SECONDS/4, leaves, sprites, backdrop, height)
        samples.paste(frame.convert('RGB'), (0, i*height))
    palette = samples.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    rgb_palette = palette.getpalette()[:765] + [0, 0, 0]
    palette.putpalette(rgb_palette)
    dark_index = min(range(255), key=lambda i: sum(
        channel * channel for channel in rgb_palette[3*i:3*i+3]))
    frames = []
    previous = None
    for n in range(FRAMES):
        rgba = render(n / FPS, leaves, sprites, backdrop, height)
        frame = rgba.convert('RGB').quantize(palette=palette,
                                            dither=Image.Dither.NONE)
        # Keep index 255 exclusively for transparency, including dark pond pixels.
        frame = frame.point([*range(255), dark_index])
        if backdrop is None:
            # GIF has binary transparency; keep solid leaf edges, no halos.
            transparent = rgba.getchannel('A').point(lambda a: 255 if a < 110 else 0)
            frame.paste(255, mask=transparent)
        else:
            full_frame = frame.copy()
            if previous is not None:
                current_indices = Image.frombytes('L', frame.size, frame.tobytes())
                previous_indices = Image.frombytes('L', previous.size, previous.tobytes())
                unchanged = ImageChops.difference(current_indices, previous_indices).point(
                    lambda value: 255 if value == 0 else 0)
                frame.paste(255, mask=unchanged)
            previous = full_frame
        frames.append(frame)
    options = dict(save_all=True, append_images=frames[1:], loop=0,
                   duration=1000//FPS, optimize=False, transparency=255)
    if backdrop is None:
        options.update(transparency=255, disposal=2)
    else:
        options.update(disposal=1)
    frames[0].save(path, **options)
    return frames


def main():
    sprites = load_sprites()
    pond = Image.open(ROOT / 'pond-banner.png').convert('RGBA')
    pond = pond.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    leaves = make_leaves(29, HEIGHT)
    banner = ROOT / 'maple/pond-maple-breeze.gif'
    encode_gif(banner, leaves, sprites, pond)
    strip = ROOT / 'maple/maple-breeze.gif'
    strip_leaves = make_leaves(24, 130)
    encode_gif(strip, strip_leaves, sprites, height=130)
    render(0, strip_leaves, sprites, height=130).save(ROOT / 'maple/maple-still.png')

    # Review several points in time and the transition back to frame zero.
    contact = Image.new('RGB', (WIDTH, (HEIGHT + 28) * 4), '#faf9f6')
    draw = ImageDraw.Draw(contact)
    for i, t in enumerate((0, 3, 6, 9)):
        contact.paste(render(t, leaves, sprites, pond).convert('RGB'),
                      (0, i*(HEIGHT+28)))
        draw.text((12, i*(HEIGHT+28) + HEIGHT + 7), f'{t}s', fill='#50382b')
    contact.save(ROOT / 'maple/animation-review.jpg', quality=90)
    render(0, leaves, sprites, pond).save(ROOT / 'maple/poster.png')

    assert not ImageChops.difference(render(0, leaves, sprites, pond),
                                    render(SECONDS, leaves, sprites, pond)).getbbox()
    for path in (banner, strip):
        with Image.open(path) as gif:
            assert gif.n_frames == FRAMES, (path, gif.n_frames)
            assert gif.info['loop'] == 0
            elapsed = 0
            for n in range(gif.n_frames):
                gif.seek(n)
                elapsed += gif.info['duration']
            assert elapsed == SECONDS * 1000, elapsed
            gif.seek(FRAMES-1)
            gif.load()
        print(f'{path.name}: {path.stat().st_size/1024/1024:.2f} MiB, '
              f'{FRAMES} frames, {SECONDS}s, seamless loop verified')


if __name__ == '__main__':
    main()
