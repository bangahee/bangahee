"""Animate the original many-koi artwork as a seamless six-second scene.

Run: python scripts/render_banner.py
Install: python -m pip install -r requirements-banner.txt

The source PNG stays intact. Imagegen prepared registered fish and water layers;
this renderer animates the water, waterfall, foliage, fish and floating leaves.
"""

from collections import deque
from math import cos, pi, sin, tau
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 864, 288
FRAMES, SECONDS = 72, 6


def mask_polygon(points, blur=4):
    mask = Image.new("L", (WIDTH, HEIGHT))
    ImageDraw.Draw(mask).polygon(
        [(round(x * WIDTH), round(y * HEIGHT)) for x, y in points], fill=255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(mask, dtype=float) / 255


def load_fish():
    atlas = Image.open(ROOT / "banner/koi-sprites.png").convert("RGBA")
    atlas = atlas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    # Use the generated cutout's alpha with the original registered RGB. This
    # preserves the exact original fish markings and avoids colored matte edges.
    original = Image.open(ROOT / "pond-banner.png").convert("RGB")
    original = original.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    atlas = Image.merge("RGBA", (*original.split(), atlas.getchannel("A")))
    occupied = np.asarray(atlas.getchannel("A")) > 100
    seen = np.zeros(occupied.shape, dtype=bool)
    components = []
    for y, x in zip(*np.where(occupied)):
        if seen[y, x]:
            continue
        queue = deque([(int(x), int(y))])
        seen[y, x] = True
        points = []
        while queue:
            cx, cy = queue.popleft()
            points.append((cx, cy))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < WIDTH and 0 <= ny < HEIGHT
                        and occupied[ny, nx] and not seen[ny, nx]):
                    seen[ny, nx] = True
                    queue.append((nx, ny))
        if len(points) > 160:
            components.append(points)
    if len(components) != 6:
        raise ValueError(f"Expected six registered koi sprites, got {len(components)}")
    fish = []
    for points in sorted(components, key=lambda pts: min(x for x, _ in pts)):
        left = max(0, min(x for x, _ in points) - 3)
        top = max(0, min(y for _, y in points) - 3)
        right = min(WIDTH, max(x for x, _ in points) + 4)
        bottom = min(HEIGHT, max(y for _, y in points) + 4)
        crop = atlas.crop((left, top, right, bottom))
        sprite = Image.new("RGBA", (crop.width + 16, crop.height + 16))
        sprite.alpha_composite(crop, (8, 8))
        fish.append((sprite, (left + right) / 2, (top + bottom) / 2))
    return fish


class Scene:
    def __init__(self):
        self.base = Image.open(ROOT / "banner/pond-clean.png").convert("RGB")
        self.base = self.base.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        self.pixels = np.asarray(self.base)
        self.yy, self.xx = np.mgrid[:HEIGHT, :WIDTH]
        self.water = mask_polygon([
            (.24, .27), (.39, .22), (.61, .23), (.76, .25), (.89, .29),
            (.85, .56), (.83, .74), (.70, .85), (.56, .88), (.42, .78),
            (.27, .72), (.23, .54)])
        self.foliage = np.maximum(
            mask_polygon([(0, 0), (.39, 0), (.35, .16), (.22, .33), (0, .12)]),
            mask_polygon([(.89, .50), (1, .39), (1, 1), (.85, 1), (.84, .78)]))
        bright = self.pixels.mean(axis=2) > 130
        self.falls = mask_polygon([(.68, 0), (.79, 0), (.77, .25), (.69, .25)], 2) * bright
        self.lantern = mask_polygon([(.055, .32), (.13, .32), (.13, .52), (.055, .52)], 2)
        warm = ((self.pixels[:, :, 0].astype(int) > self.pixels[:, :, 2].astype(int) + 65)
                & (self.pixels[:, :, 0] > 150))
        self.lantern *= warm
        self.fish = load_fish()
        atlas = Image.open(ROOT / "maple/leaves-atlas.png").convert("RGBA")
        self.leaves = []
        for index in range(4):
            col, row = index % 3, index // 3
            tile = atlas.crop((col * atlas.width // 3, row * atlas.height // 2,
                               (col + 1) * atlas.width // 3, (row + 1) * atlas.height // 2))
            tile = tile.crop(tile.getchannel("A").getbbox())
            tile.thumbnail((16, 16), Image.Resampling.LANCZOS)
            self.leaves.append(tile)

    def render(self, t):
        phase = tau * (t % 1)
        dx = self.water * (1.35 * np.sin(self.yy / 10 + phase)
                           + .55 * np.sin(self.xx / 25 - 2 * phase))
        dy = self.water * .8 * np.sin(self.xx / 18 + phase)
        dx += self.foliage * 1.8 * np.sin(phase + self.yy / 33)
        dy += self.foliage * .65 * np.sin(phase + self.xx / 48)
        dx += self.falls * 1.5 * np.sin(self.yy / 3 - 6 * phase)
        sx = np.clip(np.rint(self.xx + dx).astype(int), 0, WIDTH - 1)
        sy = np.clip(np.rint(self.yy + dy).astype(int), 0, HEIGHT - 1)
        colors = self.pixels[sy, sx].astype(float)
        light = 1 + self.water * .018 * np.sin(self.xx / 35 + self.yy / 25 - 2 * phase)
        light += self.falls * .13 * np.sin(self.yy / 2.8 - 8 * phase)
        light += self.lantern * .045 * (sin(3 * phase) + .4 * sin(7 * phase))
        colors = np.clip(np.rint(colors * light[:, :, None]), 0, 255).astype("uint8")
        scene = Image.fromarray(colors).convert("RGBA")

        ripples = Image.new("RGBA", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(ripples)
        for rx, ry, scale in ((.9, .30, 1), (.72, .235, .75)):
            for ring in range(3):
                progress = (t * 4 + ring / 3) % 1
                radius = (8 + progress * 29) * scale
                opacity = round(95 * sin(pi * progress))
                cx, cy = WIDTH * rx, HEIGHT * ry
                draw.ellipse((cx - radius, cy - radius / 3,
                              cx + radius, cy + radius / 3),
                             outline=(206, 237, 205, opacity), width=1)
        for index in range(12):
            x, y = 250 + index * 37 % 420, 80 + index * 31 % 125
            alpha = round(30 * (1 + sin(2 * phase + index * 1.7)) / 2)
            draw.line((x - 3, y, x + 3, y), fill=(238, 243, 176, alpha))
        scene = Image.alpha_composite(scene, ripples)

        for index, (sprite, cx, cy) in enumerate(self.fish):
            local = phase + index * 1.3
            pixels = np.asarray(sprite)
            yy, xx = np.mgrid[:sprite.height, :sprite.width]
            bend = 1.5 * np.sin(yy / 11 + 2 * local)
            sample_x = np.clip(np.rint(xx + bend).astype(int), 0, sprite.width - 1)
            moving = Image.fromarray(pixels[yy, sample_x])
            moving = moving.rotate(2.2 * sin(local), Image.Resampling.BICUBIC, expand=True)
            x = round(cx + 6 * sin(local) - moving.width / 2)
            y = round(cy + 3 * cos(local) - moving.height / 2)
            shadow = Image.new("RGBA", moving.size, (0, 25, 24, 0))
            shadow.putalpha(moving.getchannel("A").point(lambda a: a // 6))
            scene.alpha_composite(shadow, (x + 2, y + 3))
            scene.alpha_composite(moving, (x, y))

        for index, leaf in enumerate(self.leaves):
            local = phase + index * 1.7
            x = WIDTH * (.27 + index * .15) + 10 * sin(local)
            y = HEIGHT * (.32 + (index % 2) * .36) + 4 * cos(local)
            moving = leaf.rotate(20 * sin(local), Image.Resampling.BICUBIC, expand=True)
            scene.alpha_composite(moving, (round(x), round(y)))
        return scene.convert("RGB")


def main():
    scene = Scene()
    assert not ImageChops.difference(scene.render(0), scene.render(1)).getbbox(), "Loop does not close"
    samples = Image.new("RGB", (WIDTH, HEIGHT * 4))
    for index in range(4):
        samples.paste(scene.render(index / 4), (0, HEIGHT * index))
    palette = samples.quantize(colors=255)
    rgb_palette = palette.getpalette()[:765] + [0, 0, 0]
    palette.putpalette(rgb_palette)
    replacement = min(range(255), key=lambda i: sum(rgb_palette[3*i:3*i+3]))
    frames, durations = [], []
    previous = None
    for index in range(FRAMES):
        frame = scene.render(index / FRAMES).quantize(palette=palette, dither=Image.Dither.NONE)
        frame = frame.point([*range(255), replacement])
        indices = np.asarray(frame).copy()
        if previous is not None:
            unchanged = Image.fromarray(np.where(indices == previous, 255, 0).astype("uint8"))
            frame.paste(255, mask=unchanged)
        previous = indices
        frames.append(frame)
        durations.append((80, 80, 90)[index % 3])
    output = ROOT / "banner/many-koi.gif"
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, optimize=False, transparency=255, disposal=1)
    scene.render(0).save(ROOT / "banner/many-koi-still.png")
    print(f"{output}: {output.stat().st_size / 1024 / 1024:.2f} MiB, {FRAMES} frames, {SECONDS}s")


if __name__ == "__main__":
    main()
