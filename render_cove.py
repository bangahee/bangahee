"""Render the activity koi in its animated iris cove.

Run from the repository root after git-koi generates koi/koi.gif.
The activity sprite and its frame timing are preserved. Water, waterfall,
caustics, plants and ripples are animated separately underneath it.
"""
from math import ceil, pi, sin, tau
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageSequence
from scripts import render_maple as maple

ROOT = Path(__file__).resolve().parent
SIZE = (864, 432)
WIDTH, HEIGHT = SIZE


def polygon_mask(points, blur=3):
    mask = Image.new('L', SIZE)
    ImageDraw.Draw(mask).polygon(
        [(round(x*WIDTH), round(y*HEIGHT)) for x, y in points], fill=255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(mask, dtype=float)/255


class Cove:
    def __init__(self):
        self.base = Image.open(ROOT/'pond-cove-background.png').convert('RGB')
        self.base = self.base.resize(SIZE, Image.Resampling.LANCZOS)
        self.pixels = np.asarray(self.base)
        self.yy, self.xx = np.mgrid[:HEIGHT, :WIDTH]
        self.water = polygon_mask([
            (.26,.29),(.37,.17),(.54,.13),(.70,.19),(.87,.26),
            (.92,.40),(.85,.67),(.78,.82),(.63,.89),(.38,.87),
            (.22,.77),(.16,.57),(.20,.39)])
        self.inlet = polygon_mask([
            (.11,.055),(.17,.06),(.205,.14),(.27,.23),
            (.265,.32),(.205,.35),(.16,.26),(.14,.16)], 2)
        brightness = self.pixels.mean(axis=2)
        pale_water = (brightness > 115) & (self.pixels[:,:,2] > 75)
        self.falls = self.inlet*pale_water
        plants = np.maximum(
            polygon_mask([(0,.53),(.12,.55),(.23,.92),(.18,1),(0,1)], 2),
            polygon_mask([(.97,0),(1,0),(1,.79),(.90,.73),(.87,.42)], 2))
        green = ((self.pixels[:,:,1].astype(float) > self.pixels[:,:,0]*1.08)
                 & (self.pixels[:,:,1] > 65))
        self.foliage = plants*green
        luma = (self.pixels[:,:,0]*.2126 + self.pixels[:,:,1]*.7152
                + self.pixels[:,:,2]*.0722)
        self.caustics = self.water*np.clip((luma-100)/75, 0, 1)
        # Share the top banner's textured maple sprites and wind/tumble motion.
        maple.WIDTH, maple.HEIGHT, maple.SECONDS = WIDTH, HEIGHT, 1.0
        self.maple_sprites = maple.load_sprites()
        self.maple_leaves = maple.make_leaves(26, HEIGHT)
        for leaf in self.maple_leaves:
            leaf['size'] *= .83

    def foreground(self, scene, t):
        return maple.render(t % 1, self.maple_leaves, self.maple_sprites,
                            scene.convert('RGBA'), HEIGHT).convert('RGB')

    def render(self, t):
        t %= 1
        phase = tau*t
        # Pixel-sized refraction moves the painted pebbles and water detail.
        # The wooden bridge and stone banks remain fixed.
        dx = self.water*(1.15*np.sin(self.yy/14 + phase)
                         + .4*np.sin(self.xx/29 - 2*phase))
        dy = self.water*.8*np.sin(self.xx/21 + phase)
        dx += self.falls*.85*np.sin(self.yy/3.1 - 5*phase)
        dy += self.falls*2.4*np.sin(self.yy/3.7 - 6*phase)
        dx += self.foliage*1.7*np.sin(phase + self.yy/34)
        dy += self.foliage*.5*np.sin(phase + self.xx/47)
        sx = np.clip(np.rint(self.xx+dx).astype(int), 0, WIDTH-1)
        sy = np.clip(np.rint(self.yy+dy).astype(int), 0, HEIGHT-1)
        colors = self.pixels[sy,sx].astype(float)
        light = 1 + self.caustics*.055*np.sin(self.xx/33 + self.yy/24 - 2*phase)
        light += self.falls*.1*np.sin(self.yy/2.7 - 8*phase)
        colors = np.clip(np.rint(colors*light[:,:,None]),0,255).astype('uint8')
        scene = Image.fromarray(colors).convert('RGBA')

        ripples = Image.new('RGBA',SIZE)
        draw = ImageDraw.Draw(ripples)
        for ring in range(3):
            progress = (t*3 + ring/3) % 1
            radius = 10 + 46*progress
            opacity = round(74*sin(pi*progress))
            cx,cy = WIDTH*.227,HEIGHT*.322
            draw.ellipse((cx-radius,cy-radius*.36,cx+radius,cy+radius*.36),
                         outline=(213,239,207,opacity),width=1)
        for index in range(9):
            x = WIDTH*(.32 + (index*13 % 45)/100)
            y = HEIGHT*(.33 + (index*11 % 41)/100)
            alpha = round(23*(1+sin(2*phase+index*1.7))/2)
            draw.line((x-3,y,x+3,y),fill=(224,239,176,alpha),width=1)
        return Image.alpha_composite(scene,ripples)


def koi_scene(cove, fish, source_size, t):
    t %= 1
    scene = cove.render(t)
    box = fish.getbbox()
    if not box:
        raise ValueError('A source koi frame has no visible fish')
    center_x,center_y = (box[0]+box[2])/2,(box[1]+box[3])/2
    pond_x = WIDTH*(.51 + (center_x/source_size[0]-.5)*.49)
    pond_y = HEIGHT*(.53 + (center_y/source_size[1]-.5)*.48)
    wake = Image.new('RGBA',SIZE)
    draw = ImageDraw.Draw(wake)
    for ring in range(2):
        progress = (t*4 + ring/2) % 1
        radius = 18 + 23*progress
        alpha = round(30*sin(pi*progress))
        draw.ellipse((pond_x-radius,pond_y-radius*.4,
                      pond_x+radius,pond_y+radius*.4),
                     outline=(198,229,197,alpha),width=1)
    scene = Image.alpha_composite(scene,wake)
    sprite = fish.crop(box)
    scale = .88*min(512/source_size[0],512/source_size[1])
    sprite = sprite.resize((max(1,round(sprite.width*scale)),
                            max(1,round(sprite.height*scale))),
                           Image.Resampling.NEAREST)
    x,y = round(pond_x-sprite.width/2),round(pond_y-sprite.height/2)
    shadow = Image.new('RGBA',sprite.size,(2,29,28,0))
    shadow.putalpha(sprite.getchannel('A').point(lambda a:a//5))
    scene.alpha_composite(shadow,(x+3,y+4))
    scene.alpha_composite(sprite,(x,y))
    return scene.convert('RGB')


def render_pond():
    cove = Cove()
    with Image.open(ROOT/'koi/koi.gif') as source:
        source_size = source.size
        frames = [(frame.convert('RGBA'),frame.info.get('duration',70))
                  for frame in ImageSequence.Iterator(source)]
    if not frames:
        raise ValueError('The source koi animation is empty')
    native_duration = sum(ms for _,ms in frames)
    # Keep the native fish and water speed, while giving the falling leaves a
    # slower full loop. Repeat complete koi cycles rather than stretching them.
    frames *= max(1,ceil(10000/native_duration))
    assert not ImageChops.difference(cove.render(0).convert('RGB'),
                                    cove.render(1).convert('RGB')).getbbox(), \
        'The cove animation must close seamlessly'
    assert ImageChops.difference(cove.render(0).convert('RGB'),
                                cove.render(.25).convert('RGB')).getbbox(), \
        'The cove background must animate independently of the koi'
    assert not ImageChops.difference(cove.foreground(cove.base,0),
                                    cove.foreground(cove.base,1)).getbbox(), \
        'The foreground maple loop must close seamlessly'

    samples = Image.new('RGB',(512,512),'#18685b')
    for index,(frame,_) in enumerate(frames[::max(1,len(frames)//16)][:16]):
        box = frame.getbbox()
        if box:
            sprite = frame.crop(box)
            sprite.thumbnail((128,128),Image.Resampling.NEAREST)
            samples.paste(sprite,((index%4)*128,(index//4)*128),sprite)
    colors = cove.base.quantize(colors=208).getpalette()[:208*3]
    colors += samples.quantize(colors=47).getpalette()[:47*3]
    colors += [0,0,0]
    palette = Image.new('P',(1,1))
    palette.putpalette(colors)
    dark = min(range(255),key=lambda i:sum(v*v for v in colors[3*i:3*i+3]))

    duration = sum(ms for _,ms in frames)
    encoded,durations,review,review_frames = [],[],[],{}
    previous = None
    time_ms = 0
    for index,(fish,ms) in enumerate(frames):
        t = time_ms/duration
        scene = koi_scene(cove,fish,source_size,time_ms/native_duration)
        scene = cove.foreground(scene,t)
        frame = scene.quantize(palette=palette,dither=Image.Dither.NONE)
        frame = frame.point([*range(255),dark])
        full_frame = frame.copy()
        if previous is not None:
            new_indices = Image.frombytes('L',SIZE,frame.tobytes())
            old_indices = Image.frombytes('L',SIZE,previous.tobytes())
            same = ImageChops.difference(new_indices,old_indices).point(
                lambda value:255 if value==0 else 0)
            frame.paste(255,mask=same)
        previous = full_frame
        encoded.append(frame)
        durations.append(ms)
        if index in (0,len(frames)//4,len(frames)//2,3*len(frames)//4):
            review.append(scene)
            review_frames[index] = full_frame.convert('RGB')
        time_ms += ms

    output = ROOT/'koi/private-pond-maple.gif'
    output.parent.mkdir(exist_ok=True)
    temporary = output.with_suffix('.tmp.gif')
    encoded[0].save(temporary,save_all=True,append_images=encoded[1:],
                    duration=durations,loop=0,optimize=False,
                    transparency=255,disposal=1)
    with Image.open(temporary) as check:
        assert check.size==SIZE and check.n_frames==len(frames)
        assert check.info['loop']==0
        total = 0
        for n in range(check.n_frames):
            check.seek(n)
            assert check.info['duration']==durations[n]
            total += check.info['duration']
            if n in review_frames:
                assert not ImageChops.difference(
                    check.convert('RGB'),review_frames[n]).getbbox(), \
                    'GIF delta encoding left a trail'
        assert total==duration
    temporary.replace(output)
    # Keep existing consumers of the original pond URL up to date as well.
    shutil.copyfile(output,ROOT/'koi/pond.gif')
    shutil.copyfile(output,ROOT/'koi/private-pond.gif')
    review[0].save(ROOT/'koi/private-pond-still.png')
    contact = Image.new('RGB',(WIDTH,HEIGHT*len(review)))
    for n,scene in enumerate(review):
        contact.paste(scene,(0,n*HEIGHT))
    contact.save(ROOT/'koi/private-pond-review.jpg',quality=90)
    print(f'Rendered {len(frames)} frames, {duration/1000:g}s, '
          f'{output.stat().st_size/1024/1024:.2f} MiB to {output}; '
          'background motion, loop, timing, and decoded GIF verified')


if __name__=='__main__':
    render_pond()
