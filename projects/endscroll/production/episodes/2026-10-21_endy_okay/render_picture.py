"""Render the silent picture track of endy_okay (14.74 s, 1080x1920, 30 fps) -> shots/picture.mp4.

Remake of @sadgoose42 "You'll be okay" (references/sadgoose42_7695859890538958112), same original
audio. Option A (boss 10-21): Endy wrapped in a giant maple leaf with a mug of cocoa on an
autumn porch, a red squirrel asleep on its own on the pumpkin (boss: not leaning on him). Endy's mouth stays closed: the voice is a narrator.
0-10.0     Seedance clip, start = end = K1 (boss: a still opening has no hook): he looks up from the
           mug into the camera on the first words, a leaf drifts down, a nod on "I know", a sip.
10.0-end   Seedance clip (start K1, end K3): he waves at the camera on "You're okay. You are you."
           (10.44), then snuggles in and closes his eyes; the last frame holds to the end.
Run from anywhere: python3 render_picture.py
"""
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
K = HERE / "keyframes"
W, H, FPS, DUR = 1080, 1920, 30, 14.74
AV_LAG = 2 / FPS   # engine/tools/assemble.py shows the picture 2 frames after the audio
T_CLIP = 10.0
# The opening clip drifts: by its last frame the picture sits 1.25% smaller and 26 px to the left of
# where the wave clip (and K1) starts, which jumped at 10 s (boss). Undo the drift gradually over the
# opening, and zoom everything in 6% so the corrected edges never show (3% left a black strip).
DRIFT_SCALE, DRIFT_X = 0.9875, 26
ZOOM = 1.06


def cover(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))




def clip_frames(name):
    src = HERE / "shots" / name
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(info[0]), int(info[1])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf", f"fps={FPS}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return [cover(Image.fromarray(f)) for f in np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)]


def warp(im, f):
    """f = how much of the opening's drift to undo (0 at its first frame, 1 at its last)."""
    sx = 1 + (DRIFT_SCALE - 1) * f
    a = sx / ZOOM
    coeffs = (a, 0, sx * (W / 2 - W / 2 / ZOOM) - DRIFT_X * f, 0, a, sx * (H / 2 - H / 2 / ZOOM))
    return im.transform((W, H), Image.AFFINE, coeffs, resample=Image.BICUBIC)


def main():
    opening, wave = clip_frames("opening_seedance.mp4"), clip_frames("wave_seedance.mp4")
    out = HERE / "shots/picture.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out)],
        stdin=subprocess.PIPE)
    for i in range(round(DUR * FPS)):
        t = i / FPS + AV_LAG
        if t < T_CLIP:
            k = min(int(t * FPS), len(opening) - 1)
            im = warp(opening[k], k / (len(opening) - 1))
        else:
            im = warp(wave[min(int((t - T_CLIP) * FPS), len(wave) - 1)], 0)
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    ff.wait()
    print(out)


if __name__ == "__main__":
    main()
