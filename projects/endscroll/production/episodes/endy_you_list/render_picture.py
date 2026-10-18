"""Render the silent picture track of endy_you_list (8.47 s, 1080x1920, 30 fps) -> shots/picture.mp4.

Timed to New Home, original 50.14-58.60 s (the climax the boss picked), see beatmap.md.
0-1.81     K1: Endy peeks over the rock holding the tied scroll; slow blink on the 1.24 accent.
1.81-6.02  the string is gone and the scroll unrolls down the rock (K2 revealed above a moving
           roll); one "N. You" line lands on each accent, the roll reaches the leaves at 6.02.
7.24       K3: he ducks shyly into his shell.  7.0-7.87  a maple leaf falls onto his head.
Run from anywhere: python3 render_picture.py
"""
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
K = HERE / "keyframes"
W, H, FPS, DUR = 1080, 1920, 30, 8.47
AV_LAG = 2 / FPS   # engine/tools/assemble.py shows the picture 2 frames after the audio

T_BLINK = (1.24, 1.38)
T_UNROLL = 1.81
T_SHY, T_LEAF, T_LAND = 7.24, 7.00, 7.87
# keyframe pixels (752x1344)
COLUMN = (215, 560)                 # x range of the paper and its roll
PAPER_TOP, ROLL_BOX = 668, (220, 1148, 556, 1212)
EYES = (250, 488, 480, 592)
LINES = [f"{i}. You" for i in range(1, 7)] + ["7. You..."]
LINE_TOP, LINE_STEP, TEXT_X = 692, 62, 300
# where the bottom of the paper is at each accent: line i is fully shown on its beat
FRONT = [(T_UNROLL, PAPER_TOP), (2.49, 752), (3.12, 814), (3.80, 876), (4.22, 938), (5.24, 1000),
         (6.02, ROLL_BOX[1])]


def load(name):
    return Image.open(K / name).convert("RGB")


k1, k2, k3 = load("K1_a.png"), load("K2_open_a.png"), load("K3_shy_a.png")
eye_mask = Image.new("L", k1.size, 0)
eye_mask.paste(255, EYES)
k1_blink = Image.composite(load("K1_blink.png"), k1, eye_mask.filter(ImageFilter.GaussianBlur(10)))
roll = k2.crop(ROLL_BOX).convert("RGBA")
_r = np.array(roll.convert("HSV")).astype(int)
roll.putalpha(Image.fromarray((((_r[..., 2] > 150) & (_r[..., 1] < 120)) * 255).astype(np.uint8))
              .filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1)))   # paper only, no leaves

# handwriting on a transparent layer, same coordinates as the keyframes
ink = Image.new("RGBA", k1.size, (0, 0, 0, 0))
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf", 44)
d = ImageDraw.Draw(ink)
for i, line in enumerate(LINES):
    d.text((TEXT_X, LINE_TOP + i * LINE_STEP), line, font=font, fill=(92, 58, 34, 235))
ink = ink.filter(ImageFilter.GaussianBlur(0.6))

# the leaf: white background keyed out
leaf = Image.open(K / "leaf.png").convert("RGB")
la = np.array(leaf).astype(int)
alpha = np.clip((765 - la.sum(2) - 30) * 4, 0, 255).astype(np.uint8)
leaf = leaf.convert("RGBA")
leaf.putalpha(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1)))
leaf = leaf.crop(leaf.getbbox())
leaf = leaf.resize((72, round(72 * leaf.height / leaf.width)), Image.LANCZOS)


def ease_out(u):
    return 1 - (1 - u) ** 3


def front(t):
    for (t0, y0), (t1, y1) in zip(FRONT, FRONT[1:]):
        if t < t1:
            return y0 + (y1 - y0) * ease_out((t - t0) / (t1 - t0))
    return FRONT[-1][1]


def cover(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def frame(t):
    t += AV_LAG
    if t < T_UNROLL:
        return k1_blink if T_BLINK[0] <= t < T_BLINK[1] else k1
    f = round(front(t))
    top = k2 if t < T_SHY else Image.blend(k2, k3, min(1, (t - T_SHY) * FPS / 3))
    im = top.copy()
    # inside the paper column the rock still shows below the roll
    x0, x1 = COLUMN
    im.paste(k1.crop((x0, f, x1, k1.height)), (x0, f))
    a = np.array(ink.getchannel("A"))
    a[f:] = 0                                    # only the unrolled part shows writing
    text = ink.copy()
    text.putalpha(Image.fromarray(a))
    im = im.convert("RGBA")
    im.alpha_composite(text)
    im.alpha_composite(roll, (ROLL_BOX[0], f))
    im = im.convert("RGB")
    if t >= T_LEAF:
        u = min(1, (t - T_LEAF) / (T_LAND - T_LEAF))
        x = 430 + (370 - 430) * u + 28 * math.sin(u * 2.5 * math.pi) * (1 - u)
        y = 260 + (468 - 260) * (u * u * 0.4 + u * 0.6)
        rot = 40 * math.sin(u * 2 * math.pi) * (1 - u) + 18
        lf = leaf.rotate(rot, resample=Image.BICUBIC, expand=True)
        im = im.convert("RGBA")
        im.alpha_composite(lf, (round(x - lf.width / 2), round(y - lf.height / 2)))
        im = im.convert("RGB")
    return im


def main():
    out = HERE / "shots/picture.mp4"
    out.parent.mkdir(exist_ok=True)
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out)],
        stdin=subprocess.PIPE)
    for i in range(round(DUR * FPS)):
        ff.stdin.write(cover(frame(i / FPS)).tobytes())
    ff.stdin.close()
    ff.wait()
    print(out)


if __name__ == "__main__":
    main()
