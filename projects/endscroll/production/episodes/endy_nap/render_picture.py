"""Render the silent picture track of endy_nap (10 s, 1080x1920, 30 fps) -> shots/picture.mp4.

0-4.55 s  P1: Endy (masked from P1a over the empty plate) squashes on every beat (0.6 s),
          mouth opens on each sung word (mouth patch from P1b).
4.55-5.1  burst: grok clip b, 0.30-0.85 s.
5.1-7.3   P3 in his shell.   7.3-7.9  P4 floppy over the chair.   7.9-10  P5 asleep under the blanket.
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
T_BURST, BURST_IN, BURST_OUT = 4.55, 0.30, 0.85
T_P3, T_P4, T_P5 = T_BURST + (BURST_OUT - BURST_IN), 7.3, 7.9
# sung words in the P1 section (start, end), from the reference audio
WORDS = [(0.22, 0.34), (0.34, 0.52), (0.52, 0.64), (0.64, 0.74), (0.74, 0.88), (0.88, 1.08),
         (1.08, 1.36), (1.36, 1.68), (1.68, 2.08), (2.10, 2.46), (2.46, 2.62), (2.62, 2.82),
         (2.82, 3.0), (3.0, 3.15), (3.15, 3.30), (3.30, 3.68), (3.68, 4.40)]
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
p1a, p1b = load("P1a_v2.png"), load("P1b_v1.png")
box_mask = Image.new("L", p1a.size, 0)
box_mask.paste(255, MOUTH_BOX)
box_mask = box_mask.filter(ImageFilter.GaussianBlur(8))
p1_open = Image.composite(p1b, p1a, box_mask)
mask = Image.open(K / "P1_mask.png").convert("L")
layers = {}
for key, im in (("closed", p1a), ("open", p1_open)):
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


def p1_frame(t):
    # squash: full height at the top of each beat, shortest half a beat later
    phase = ((t - BEAT_PHASE) / BEAT) % 1.0
    k = (1 - np.cos(2 * np.pi * phase)) / 2          # 0 at the top, 1 at the bottom
    sy, sx = 1 - SQUASH * k, 1 + SQUASH * 0.5 * k
    singing = any(s <= t < (e if e - s > 0.5 else s + min(0.2, (e - s) * 0.8)) for s, e in WORDS)   # a held note stays open
    layer = layers["open" if singing else "closed"]
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
