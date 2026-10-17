"""Render the silent picture track of endy_nap (10 s, 1080x1920, 30 fps) -> shots/picture.mp4.

0-4.67 s  P1: Endy (masked from P1a over the empty plate) squashes on every beat (0.6 s),
          mouth flaps steadily while he sings (P1b open, P1h half-open), closed at real breaks.
4.67-5.22 burst: grok clip b, 0.30-0.85 s.
5.22-7.3  P3 in his shell.   7.3-7.9  P4 floppy over the chair.   7.9-10  P5 asleep under the blanket.
Run from anywhere: python3 render_picture.py
"""
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).parent
K = HERE / "keyframes"
W, H, FPS, DUR = 1080, 1920, 30, 10.0

BEAT, BEAT_PHASE, SQUASH = 0.6, 0.55, 0.03   # head is highest at 0.55 + 0.6k in the reference
T_BURST, BURST_IN, BURST_OUT = 4.67, 0.30, 0.85   # papers burst on "took", as in the reference
T_P3, T_P4, T_P5 = T_BURST + (BURST_OUT - BURST_IN), 7.3, 7.9
AV_LAG = 2 / FPS   # measured: assemble.py shows picture frame j at (j+2)/30 s, i.e. 2 frames after the audio
MOUTH_BOX = (250, 570, 410, 670)   # in keyframe pixels (752x1344)


def cover(im):
    """Scale to cover 1080x1920 and centre-crop."""
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def load(name):
    return Image.open(K / name).convert("RGB")


plate = cover(load("plate_a.png"))
p1a, p1b, p1h = load("P1a_v2.png"), load("P1b_v1.png"), load("P1h_v1.png")
box_mask = Image.new("L", p1a.size, 0)
box_mask.paste(255, MOUTH_BOX)
box_mask = box_mask.filter(ImageFilter.GaussianBlur(8))
p1_open = Image.composite(p1b, p1a, box_mask)
p1_half = Image.composite(p1h, p1a, box_mask)
mask = Image.open(K / "P1_mask.png").convert("L")
layers = {}
for key, im in (("closed", p1a), ("half", p1_half), ("open", p1_open)):
    rgba = cover(im).convert("RGBA")
    rgba.putalpha(cover(mask.convert("RGB")).convert("L"))
    layers[key] = rgba
alpha = np.array(layers["closed"])[:, :, 3] > 128
ys, xs = np.nonzero(alpha)
ANCHOR_X, ANCHOR_Y = (xs.min() + xs.max()) / 2, ys.max()   # feet, bottom centre
stills = {name: cover(load(f)) for name, f in (("P3", "P3_a.png"), ("P4", "P4_b.png"), ("P5", "P5_a.png"))}


def burst_frames():
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(BURST_IN), "-t", str(BURST_OUT - BURST_IN),
         "-i", str(HERE / "shots/burst_grok_b.mp4"), "-vf", f"fps={FPS}",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    w, h = 704, 1280
    arr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    return [cover(Image.fromarray(f)) for f in arr]


# Boss 10-17 (final): while he is singing, the mouth just opens and closes at a steady, relaxed
# rate (one cycle per half beat, 0.3 s), and only stops where the voice really breaks off.
# Sung stretches measured from the song (band energies + sibilants): "in-stead" ends at 3.90,
# then only a bass hit and silence until "I" at 4.37 (not 3.68 as whisper said); "took" 4.67. The voice runs straight from "today" into "but", but the boss wanted a
# breath at the comma (where the caption line changes): closed 1.90-2.12 (0.25 s), reopening on "but".
SUNG = [(0.20, 2.00), (2.09, 3.90), (4.34, 4.67)]
CYCLE = ["closed", "half", "open", "open", "open", "half", "closed", "closed", "closed"]   # 9 frames = 0.3 s


def mouth(t):
    t += AV_LAG
    for start, end in SUNG:
        if start <= t < end:
            return CYCLE[int(round((t - start) * FPS)) % len(CYCLE)]
    return "closed"


def p1_frame(t):
    # squash: full height at the top of each beat, shortest half a beat later
    phase = ((t - BEAT_PHASE) / BEAT) % 1.0
    k = (1 - np.cos(2 * np.pi * phase)) / 2          # 0 at the top, 1 at the bottom
    sy, sx = 1 - SQUASH * k, 1 + SQUASH * 0.5 * k
    layer = layers[mouth(t)]
    lw, lh = round(W * sx), round(H * sy)
    scaled = layer.resize((lw, lh), Image.LANCZOS)
    ox = round(ANCHOR_X - ANCHOR_X * sx)
    oy = round(ANCHOR_Y - ANCHOR_Y * sy)
    frame = plate.convert("RGBA")
    frame.alpha_composite(scaled.crop((max(0, -ox), max(0, -oy), max(0, -ox) + W - max(0, ox), max(0, -oy) + H - max(0, oy))),
                          (max(0, ox), max(0, oy)))
    return frame.convert("RGB")


def main():
    burst = burst_frames()
    out = HERE / "shots/picture.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out)],
        stdin=subprocess.PIPE)
    for i in range(round(DUR * FPS)):
        t = i / FPS
        if t < T_BURST:
            im = p1_frame(t)
        elif t < T_P3:
            im = burst[min(int((t - T_BURST) * FPS), len(burst) - 1)]
        elif t < T_P4:
            im = stills["P3"]
        elif t < T_P5:
            im = stills["P4"]
        else:
            im = stills["P5"]
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    ff.wait()
    print(out)


if __name__ == "__main__":
    main()
