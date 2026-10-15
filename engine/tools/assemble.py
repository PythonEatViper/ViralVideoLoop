"""Assemble an episode: clips -> 1080x1920 MP4 with burned-in captions.

Usage: python3 engine/tools/assemble.py projects/<project>/production/episodes/<name>/episode.json

episode.json:
{
  "clips": ["shots/01.mp4", {"file": "shots/02.mp4", "start": 0.4, "end": 3.5}],
  "captions": [
    {"text": "App Island · Ep 1", "start": 0, "end": 25, "pos": "top", "size": 56},
    {"text": "first recoupling: 2 AM", "start": 20, "end": 25, "pos": "center"}
  ],
  "voice_gain": 1.0,
  "music": {"file": "assets/music/one_more_dance.mp3", "offset": 8, "gain": 0.35},
  "sfx": [
    {"file": "assets/sfx/whoosh.mp3", "start": 4.9, "gain": 0.6, "dur": 1.0}
  ]
}
Paths are relative to the episode folder; a path starting with "assets/" is relative to
the repo root (shared sound and music library). "voice_gain" scales the clips' own audio;
A clip given as an object is cut to "start".."end" seconds (both optional); "crop":
[x, y, w, h] (fractions of the frame) keeps only that region, to hide something at an edge;
"audio_from" replaces the clip's sound with another file's, starting at "audio_start" seconds
(to borrow a better line reading from another take); "speed" plays the picture faster (above 1) or slower (below 1) and drops the clip's own
sound, for silent clips cut to a song; "mute_after" silences the clip's own
sound from that second on (in the clip's own time), keeping the picture. A caption may
give "y" (pixels from the top) instead of "pos", a "color", "font": "rounded" for a softer
rounded face instead of the heavy default, "stroke" (outline width in pixels), and "lit"
(karaoke: only the first N words bright, the rest faint; one caption per word). "dur" trims a sound effect. "music" starts at "offset" seconds into the track, ducks
under dialogue and fades out at the end. The mix is normalised to -14 LUFS (TikTok's loudness).
Output: <episode>/final.mp4
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
W, H, FPS = 1080, 1920, 30
FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FONTS = {"rounded": "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"}
# TikTok's UI covers the bottom ~420px and the right ~150px; keep text clear of both.
TEXT_MAX_WIDTH = 860
POS_Y = {"top": 300, "center": 820, "bottom": 1250}


def resolve(root, path):
    return REPO / path if path.startswith("assets/") else root / path


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return bool(out)


def normalize(src, dst, start=None, end=None, crop=None, audio=None, audio_start=0,
              mute_after=None, speed=None):
    """Scale/crop to 9:16, fixed fps, always one stereo audio track."""
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1"
    if crop:
        x, y, w, h = crop
        vf = f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}," + vf
    if speed:
        vf = f"setpts=PTS/{speed}," + vf
    cut = (["-ss", str(start)] if start else []) + (["-to", str(end)] if end else [])
    cmd = ["ffmpeg", "-y", *cut, "-i", str(src)]
    if audio:
        cmd += ["-ss", str(audio_start), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-shortest"]
    elif has_audio(src) and not speed:
        cmd += ["-map", "0:v:0", "-map", "0:a:0"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-map", "0:v:0", "-map", "1:a:0", "-shortest"]
    if mute_after is not None:
        # Times here count from the cut point, because -ss is applied before the input.
        cmd += ["-af", f"afade=t=out:st={max(0, mute_after - (start or 0) - 0.06)}:d=0.06"]
    cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-ac", "2", str(dst)]
    run(cmd)


def wrap(text, font, draw):
    """Auto-wrap to TEXT_MAX_WIDTH; an explicit "\\n" in the text forces a break."""
    if "\n" in text:
        return [l for part in text.split("\n") for l in wrap(part, font, draw)]
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= TEXT_MAX_WIDTH:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def caption_png(cap, dst):
    size = cap.get("size", 72)
    font = ImageFont.truetype(FONTS.get(cap.get("font"), FONT), size)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = cap["y"] if "y" in cap else POS_Y[cap.get("pos", "top")]
    # Text is centred on the full width. TikTok's buttons sit on the right of the lower half;
    # only a line that would run under them is moved left, and only as far as needed.
    beside_buttons = y >= 900
    stroke = cap.get("stroke", max(4, size // 12))
    lit, n = cap.get("lit"), 0  # karaoke: the first `lit` words bright, the rest faint
    for line in wrap(cap["text"], font, draw):
        width = draw.textlength(line, font=font)
        x = (W - width) / 2
        if beside_buttons and x + width > W - 150:
            x = max(20, W - 150 - width)
        if lit is None:
            draw.text((x, y), line, font=font, fill=cap.get("color", "white"),
                      stroke_width=stroke, stroke_fill="black")
        else:
            for word in line.split():
                faint = n >= lit
                draw.text((x, y), word, font=font, fill=(255, 255, 255, 90 if faint else 255),
                          stroke_width=stroke, stroke_fill=(0, 0, 0, 40 if faint else 255))
                x += draw.textlength(word + " ", font=font)
                n += 1
        y += int(size * 1.2)
    img.save(dst)


def main():
    episode_file = Path(sys.argv[1]).resolve()
    root = episode_file.parent
    spec = json.loads(episode_file.read_text())

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        parts = []
        for i, clip in enumerate(spec["clips"]):
            part = tmp / f"part{i:02d}.mp4"
            if isinstance(clip, str):
                clip = {"file": clip}
            normalize(root / clip["file"], part, clip.get("start"), clip.get("end"), clip.get("crop"),
                      root / clip["audio_from"] if "audio_from" in clip else None,
                      clip.get("audio_start", 0), clip.get("mute_after"), clip.get("speed"))
            parts.append(part)

        concat_list = tmp / "list.txt"
        concat_list.write_text("".join(f"file '{p}'\n" for p in parts))
        joined = tmp / "joined.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(joined)])

        captions = spec.get("captions", [])
        sfx = spec.get("sfx", [])
        cmd = ["ffmpeg", "-y", "-i", str(joined)]
        for i, cap in enumerate(captions):
            png = tmp / f"cap{i:02d}.png"
            caption_png(cap, png)
            cmd += ["-i", str(png)]
        for s in sfx:
            cmd += ["-i", str(resolve(root, s["file"]))]
        music = spec.get("music")
        if music:
            cmd += ["-ss", str(music.get("offset", 0)), "-i", str(resolve(root, music["file"]))]

        chain, last = [], "0:v"
        for i, cap in enumerate(captions):
            out = f"v{i}"
            chain.append(f"[{last}][{i + 1}:v]overlay=0:0:"
                         f"enable='between(t,{cap['start']},{cap['end']})'[{out}]")
            last = out
        if not captions:
            chain.append("[0:v]null[v]")
            last = "v"

        mix = [f"[0:a]volume={spec.get('voice_gain', 1.0)},asplit=2[voice][vkey]"]
        labels = ["[voice]"]
        if music:
            total = float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(joined)],
                capture_output=True, text=True, check=True).stdout)
            idx = 1 + len(captions) + len(sfx)
            mix.append(f"[{idx}:a]atrim=0:{total},aresample=44100,"
                       f"aformat=channel_layouts=stereo,volume={music.get('gain', 0.35)},"
                       f"afade=t=out:st={max(0, total - 1.5)}:d=1.5[mraw]")
            # Duck the music whenever a character speaks.
            mix.append("[mraw][vkey]sidechaincompress=threshold=0.03:ratio=6:"
                       "attack=15:release=350[music]")
            labels.append("[music]")
        else:
            mix.append("[vkey]anullsink")
        for j, s in enumerate(sfx):
            idx = 1 + len(captions) + j
            trim = f"atrim=0:{s['dur']}," if "dur" in s else ""
            delay = int(s["start"] * 1000)
            mix.append(f"[{idx}:a]{trim}aresample=44100,aformat=channel_layouts=stereo,"
                       f"volume={s.get('gain', 1.0)},adelay={delay}|{delay}[s{j}]")
            labels.append(f"[s{j}]")
        mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
                   "loudnorm=I=-14:TP=-1.5:LRA=11[a]")

        cmd += ["-filter_complex", ";".join(chain + mix), "-map", f"[{last}]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-movflags", "+faststart", str(root / "final.mp4")]
        run(cmd)

    print(root / "final.mp4")


if __name__ == "__main__":
    main()
