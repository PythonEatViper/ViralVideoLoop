"""Render the silent picture track of endy_nap (10 s, 1080x1920, 30 fps) -> shots/picture.mp4.

0-4.55 s  P1: Endy (masked from P1a over the empty plate) squashes on every beat (0.6 s),
          mouth opens on the stressed words only (patches from P1b open, P1h half-open).
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
# mouth opens only on the stressed words (boss 10-17: every syllable looked like chewing).
# Times are the vocal onsets measured in the song (300-3500 Hz spectral flux), not whisper's word
# starts, which were up to 0.2 s off; they match where the goose's beak opens in the reference.
# Open 1 frame before the sound, about 0.25 s each; the "I" closes at 3.94 because the voice
# stops there (silence 4.0-4.3), it is not held.  THINGS, to-DAY, KNOW, DID, I
ACCENTS = [(0.91, 1.16), (1.92, 2.12), (2.61, 2.86), (3.19, 3.44), (3.61, 3.94)]
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


def mouth(t):
    """closed -> half (1 frame) -> open -> half (2 frames) -> closed, so the mouth never snaps."""
    f = 1 / FPS
    for s, e in ACCENTS:
        if s - f <= t < s or e - 2 * f <= t < e:
            return "half"
        if s <= t < e - 2 * f:
            return "open"
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
