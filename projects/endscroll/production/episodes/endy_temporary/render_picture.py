"""Render the silent picture track of endy_temporary (20.04 s, 1080x1920, 30 fps) -> shots/picture.mp4.

Remake of @sadgoose42 "Everything is temporary" (references/ig_Db3HwpNslGs): same words at the
same times, same original audio. The picture quietly acts out the words (boss picked option B):
0-11.15   K1 Endy sips on the roof next to the snail, petals drift by.
11.15     "It won't last forever": K2 the cup is empty, he looks into it.
13.25     "And if things are going bad": the light dims and it rains; 13.6 K3 he hides in his shell.
16.65     the rain stops; 16.85 "It can't last forever": K4 he peeks out, the snail shares its drink.
18.15     no more words: K5 both sip; loops back to K1.
Run from anywhere: python3 render_picture.py
"""
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

HERE = Path(__file__).parent
K = HERE / "keyframes"
W, H, FPS, DUR = 1080, 1920, 30, 20.04
AV_LAG = 2 / FPS   # engine/tools/assemble.py shows the picture 2 frames after the audio
XFADE = 3          # frames of cross-fade at each cut, hides the small noise between keyframes

CUTS = [(0.0, "K1_a.png"), (11.15, "K2_empty.png"), (13.60, "K3_shell.png"),
        (16.85, "K4_share.png"), (18.15, "K5_both.png")]
RAIN = (13.25, 16.65)   # light dims and rain falls, with RAMP s in and out
RAMP = 0.4


def cover(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


shots = [(t, cover(Image.open(K / f).convert("RGB"))) for t, f in CUTS]

rng = random.Random(7)
# petals: drift slowly down and to the right, wrap around
PETALS = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H * 0.8), vx=rng.uniform(15, 35), vy=rng.uniform(35, 70),
               r=rng.uniform(5, 9), ph=rng.uniform(0, 6.28)) for _ in range(9)]
DROPS = [dict(x=rng.uniform(0, W * 1.1), y0=rng.uniform(0, H), v=rng.uniform(1700, 2300), l=rng.uniform(40, 80))
         for _ in range(140)]


def base(t):
    i = max(k for k, (t0, _) in enumerate(shots) if t >= t0)
    t0, im = shots[i]
    if i and t - t0 < XFADE / FPS:
        im = Image.blend(shots[i - 1][1], im, (t - t0) * FPS / XFADE)
    return im, i


def rain_amount(t):
    s, e = RAIN
    if t < s or t > e + RAMP:
        return 0.0
    return min(1.0, (t - s) / RAMP, (e + RAMP - t) / RAMP)


def frame(t):
    t += AV_LAG
    im, i = base(t)
    a = rain_amount(t)
    if a:
        dark = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.75)).enhance(0.72)
        im = Image.blend(im, dark, a)
    im = im.convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if a < 1:
        for p in PETALS:
            x = (p["x"] + p["vx"] * t + 25 * np.sin(t * 1.3 + p["ph"])) % W
            y = (p["y"] + p["vy"] * t) % (H * 0.85)
            r = p["r"]
            d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=(255, 255, 255, round(210 * (1 - a))))
    if a:
        for q in DROPS:
            y = (q["y0"] + q["v"] * t) % (H + 100) - 100
            x = q["x"] - 0.12 * y
            d.line((x, y, x - 0.12 * q["l"], y + q["l"]), fill=(225, 235, 255, round(120 * a)), width=3)
    im.alpha_composite(layer)
    return im.convert("RGB")


def main():
    out = HERE / "shots/picture.mp4"
    out.parent.mkdir(exist_ok=True)
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out)],
        stdin=subprocess.PIPE)
    for i in range(round(DUR * FPS)):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    print(out)


if __name__ == "__main__":
    main()
