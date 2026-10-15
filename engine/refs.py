"""Reference cards: download a viral video and cut a keyframe sheet. `vvl ref <url> ...` calls collect();
the dashboard's 参考 page shows every signal that has a sheet.
"""
import json
import subprocess
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FRAMES, COLS, THUMB_W = 12, 4, 270


def tikwm(url):
    """Public TikTok metadata and a watermark-free download link (no login)."""
    api = "https://www.tikwm.com/api/?hd=1&url=" + urllib.parse.quote(url, safe="")
    req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0"})
    data = json.loads(urllib.request.urlopen(req, timeout=60).read())
    if data.get("code") != 0:
        raise ValueError(f"tikwm could not read {url}: {data.get('msg')}")
    return data["data"]


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(video)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def keyframe_sheet(video, dst):
    """FRAMES evenly spaced frames in a COLS-wide grid, each labelled with its time."""
    length = duration(video)
    times = [0.3 + i * (length - 0.6) / (FRAMES - 1) for i in range(FRAMES)]
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
    thumbs = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, t in enumerate(times):
            frame = Path(tmp) / f"{i}.jpg"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                            "-frames:v", "1", "-vf", f"scale={THUMB_W}:-2", str(frame)],
                           check=True, stdin=subprocess.DEVNULL)
            img = Image.open(frame).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.text((8, 6), f"{t:.1f}s", font=font, fill="white", stroke_width=3, stroke_fill="black")
            thumbs.append(img)
    w, h = thumbs[0].size
    rows = -(-len(thumbs) // COLS)
    sheet = Image.new("RGB", (w * COLS, h * rows), "black")
    for i, img in enumerate(thumbs):
        sheet.paste(img, ((i % COLS) * w, (i // COLS) * h))
    sheet.save(dst, quality=85)
    return round(length, 1)


def collect(pdir, url, video=None):
    """Save the video and its keyframe sheet under references/; return the signal fields we can measure."""
    fields = {"url": url, "kind": "video", "tags": ["ref"]}
    if video is None:
        d = tikwm(url)
        author = d.get("author", {}).get("unique_id", "unknown")
        folder = pdir / "references" / f"{author}_{d['id']}"
        folder.mkdir(parents=True, exist_ok=True)
        video = folder / "video.mp4"
        if not video.exists():
            req = urllib.request.Request(d.get("hdplay") or d["play"], headers={"User-Agent": "Mozilla/5.0"})
            video.write_bytes(urllib.request.urlopen(req, timeout=180).read())
        music = d.get("music_info") or {}
        fields.update({
            "platform": "tiktok", "title": f"@{author}: {d.get('title', '')}"[:200],
            "views": d.get("play_count"), "likes": d.get("digg_count"), "shares": d.get("share_count"),
            "comments": d.get("comment_count"), "saves": d.get("collect_count"),
            "posted_at": datetime.fromtimestamp(d["create_time"], timezone.utc).isoformat(),
        })
        if music.get("title"):
            fields["sound"] = f"{music['title']} — {music.get('author', '')}".strip(" —")
    else:
        video = Path(video).resolve()
        folder = video.parent
    sheet = folder / "sheet.jpg"
    fields["duration_s"] = keyframe_sheet(video, sheet)
    fields["media"] = [str(p.relative_to(pdir)) for p in (video, sheet) if p.is_relative_to(pdir)]
    return {k: v for k, v in fields.items() if v not in (None, "")}
