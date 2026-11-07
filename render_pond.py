"""Render the activity koi in a living pond without modifying git-koi's GIF.

Run from the repository root after git-koi has generated koi/koi.gif.
The output uses one palette for the entire loop to avoid background flicker.
"""

from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageSequence


ROOT = Path(__file__).resolve().parent
SIZE = (960, 480)


def render_pond():
    background = Image.open(ROOT / "pond-background.png").convert("RGB")
    background = background.resize(SIZE, Image.Resampling.LANCZOS)
    with Image.open(ROOT / "koi/koi.gif") as source:
        source_size = source.size
        frames = [
            (frame.convert("RGBA"), frame.info.get("duration", 70))
            for frame in ImageSequence.Iterator(source)
        ]
    if not frames or not any(frame.getbbox() for frame, _ in frames):
        raise ValueError("The source koi animation is empty")

    # Reserve palette colors for both the habitat and the activity-driven fish.
    samples = Image.new("RGB", (512, 512), "#18685b")
    for index, (frame, _) in enumerate(frames[:: max(1, len(frames) // 16)][:16]):
        box = frame.getbbox()
        if box:
            sprite = frame.crop(box)
            sprite.thumbnail((128, 128), Image.Resampling.NEAREST)
            samples.paste(sprite, ((index % 4) * 128, (index // 4) * 128), sprite)
    colors = background.quantize(colors=208).getpalette()[: 208 * 3]
    colors += samples.quantize(colors=48).getpalette()[: 48 * 3]
    palette = Image.new("P", (1, 1))
    palette.putpalette(colors)

    output_frames = []
    durations = []
    for index, (fish, duration) in enumerate(frames):
        phase = 2 * pi * index / len(frames)
        scene = background.convert("RGBA")
        water = Image.new("RGBA", SIZE)
        draw = ImageDraw.Draw(water)
        box = fish.getbbox()
        if not box:
            raise ValueError("A source koi frame has no visible fish")
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2
        pond_x = 480 + (center_x / source_size[0] - 0.5) * 540
        pond_y = 242 + (center_y / source_size[1] - 0.5) * 290

        # Short, gentle glints make the open water feel alive without flashing.
        for number in range(5):
            x = pond_x + 80 * sin(number * 2.3) + 3 * sin(phase + number)
            y = pond_y + 65 * cos(number * 2.3) + 2 * cos(phase + number)
            glow = int(18 + 22 * (1 + sin(phase + number * 1.7)) / 2)
            draw.line((x - 5, y, x + 5, y), fill=(211, 240, 184, glow), width=1)
            draw.line((x, y - 2, x, y + 2), fill=(211, 240, 184, glow), width=1)

        # Keep the moving wake local to the fish so GIF delta frames stay small.
        for ring in range(2):
            progress = (index / len(frames) * 4 + ring / 3) % 1
            radius = 22 + 32 * progress
            opacity = int(45 * (1 - progress))
            draw.ellipse((pond_x - radius, pond_y - radius / 2,
                          pond_x + radius, pond_y + radius / 2),
                         outline=(201, 235, 185, opacity), width=1)
        scene = Image.alpha_composite(scene, water)

        if box:
            sprite = fish.crop(box)
            # Preserve the koi's appearance and animation, fitting its orbit to
            # the open water rather than leaving its transparent square visible.
            scale = 0.98 * min(512 / source_size[0], 512 / source_size[1])
            sprite = sprite.resize((max(1, round(sprite.width * scale)),
                                    max(1, round(sprite.height * scale))),
                                   Image.Resampling.NEAREST)
            x = round(pond_x - sprite.width / 2)
            y = round(pond_y - sprite.height / 2)
            shadow = Image.new("RGBA", sprite.size, (2, 33, 32, 0))
            shadow.putalpha(sprite.getchannel("A").point(lambda alpha: alpha // 4))
            scene.alpha_composite(shadow, (x + 6, y + 7))
            scene.alpha_composite(sprite, (x, y))

        output_frames.append(scene.convert("RGB").quantize(
            palette=palette, dither=Image.Dither.NONE))
        durations.append(duration)

    destination = ROOT / "koi/pond.gif"
    temporary = destination.with_suffix(".tmp.gif")
    output_frames[0].save(temporary, save_all=True,
                          append_images=output_frames[1:], duration=durations,
                          loop=0, optimize=False, disposal=1)
    temporary.replace(destination)
    print(f"Rendered {len(output_frames)} frames to {destination} "
          f"({destination.stat().st_size / 1024 / 1024:.2f} MiB)")


if __name__ == "__main__":
    render_pond()
