"""Add photographic maple leaves above the current six-koi README banner.

Run after rendering banner/many-koi-calm.gif. The original GIF is preserved.
Requires Pillow and the existing render_maple.py helper in this directory.
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence
import render_maple as breeze

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'banner/many-koi-calm.gif'
DESTINATION = ROOT / 'banner/many-koi-maple.gif'


def main():
    with Image.open(SOURCE) as source:
        size = source.size
        palette = Image.new('P', (1, 1))
        colors = source.getpalette()
        palette.putpalette(colors)
        original = [(frame.convert('RGBA'), frame.info.get('duration', 70))
                    for frame in ImageSequence.Iterator(source)]
    duration = sum(ms for _, ms in original)
    breeze.WIDTH, breeze.HEIGHT = size
    breeze.SECONDS = duration / 1000
    sprites = breeze.load_sprites()
    leaves = breeze.make_leaves(26, size[1])
    for leaf in leaves:
        leaf['size'] *= .83
    # Reuse the source palette exactly, preserving the garden's pixel colors.
    # These warm autumn reds/golds are already present in its maple branches.
    dark = min(range(255), key=lambda i: sum(c*c for c in colors[3*i:3*i+3]))
    encoded, durations, reviews = [], [], []
    previous = None
    time_ms = 0
    for i, (base, ms) in enumerate(original):
        scene = breeze.render(time_ms/1000, leaves, sprites, base, size[1])
        frame = scene.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
        frame = frame.point([*range(255), dark])
        full_frame = frame.copy()
        if previous is not None:
            now_indices = Image.frombytes('L', size, frame.tobytes())
            old_indices = Image.frombytes('L', size, previous.tobytes())
            unchanged = ImageChops.difference(now_indices, old_indices).point(
                lambda value: 255 if value == 0 else 0)
            frame.paste(255, mask=unchanged)
        previous = full_frame
        encoded.append(frame)
        durations.append(ms)
        if i in (0, len(original)//4, len(original)//2, 3*len(original)//4):
            reviews.append(scene.convert('RGB'))
        time_ms += ms
    encoded[0].save(DESTINATION, save_all=True, append_images=encoded[1:],
                    duration=durations, loop=0, transparency=255,
                    disposal=1, optimize=False)

    # The sprite trajectory closes exactly; the source keeps its original timing.
    assert not ImageChops.difference(
        breeze.render(0, leaves, sprites, original[0][0], size[1]),
        breeze.render(breeze.SECONDS, leaves, sprites, original[0][0], size[1])
    ).getbbox()
    review = Image.new('RGB', (size[0], size[1]*len(reviews)))
    for n, scene in enumerate(reviews):
        review.paste(scene, (0, n*size[1]))
    review.save(ROOT / 'banner/maple-motion-review.jpg', quality=92)
    reviews[0].save(ROOT / 'banner/maple-poster.png')
    with Image.open(DESTINATION) as check:
        assert check.size == size
        assert check.n_frames == len(original)
        assert check.info['loop'] == 0
        elapsed = 0
        for n in range(check.n_frames):
            check.seek(n)
            assert check.info['duration'] == durations[n]
            elapsed += check.info['duration']
            if n in (0, len(original)//2, len(original)-1):
                t = sum(durations[:n])/1000
                expected = breeze.render(t, leaves, sprites, original[n][0], size[1])
                expected = expected.convert('RGB').quantize(palette=palette,
                    dither=Image.Dither.NONE).point([*range(255),dark]).convert('RGB')
                assert not ImageChops.difference(check.convert('RGB'), expected).getbbox()
        assert elapsed == duration
    print(f'{DESTINATION.name}: {size[0]}x{size[1]}, {len(original)} frames, '
          f'{duration/1000:g}s, {DESTINATION.stat().st_size/1024/1024:.2f} MiB; '
          'timing, loop, and decoded frames verified')


if __name__ == '__main__':
    main()
