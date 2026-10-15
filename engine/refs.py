"""Reference cards: download a viral video, cut a keyframe sheet, and build one page of all cards.

`vvl ref <url> ...` calls collect(); the dashboard server and `vvl build` call page().
"""
import html
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


def page(pdir, signals, file_prefix):
    """One page with a card per reference that has a keyframe sheet. file_prefix turns a path
    relative to the project folder into a link: '' for the static file, '/file/' for the server."""
    refs = [s for s in sorted(signals, key=lambda s: s.get("first_at", s["at"]))
            if any(m.endswith("sheet.jpg") for m in s.get("media", []))]

    def link(rel):
        return html.escape(file_prefix + rel)

    def num(v):
        return f"{v:,}" if isinstance(v, int) else "–"

    def row(label, value):
        return f"<dt>{label}</dt><dd>{html.escape(str(value))}</dd>" if value else ""

    cards = []
    for n, s in reversed(list(enumerate(refs, 1))):
        sheet = next(m for m in s["media"] if m.endswith("sheet.jpg"))
        video = next((m for m in s["media"] if m.endswith(".mp4")), None)
        posted = s.get("posted_at", "")[:10]
        cards.append(f"""
<article class="card">
  <a href="{link(sheet)}" target="_blank"><img src="{link(sheet)}" loading="lazy" alt="keyframes"></a>
  <div class="body">
    <h2><span class="num">R{n}</span> {html.escape(s.get('title', ''))}</h2>
    <p class="links"><a href="{html.escape(s['url'])}" target="_blank">原视频 ↗</a>
      {f'<a href="{link(video)}" target="_blank">本地副本 ▶</a>' if video else ''}
      <span>{html.escape(s.get('platform', ''))} · {s.get('duration_s', '–')} 秒 · 发布 {posted or '–'}</span></p>
    <p class="stats">播放 <b>{num(s.get('views'))}</b> · 赞 {num(s.get('likes'))} · 分享 {num(s.get('shares'))}
      · 评论 {num(s.get('comments'))} · 收藏 {num(s.get('saves'))}</p>
    <dl>
      {row('剧情', s.get('summary'))}
      {row('开头钩子', s.get('hook_text'))}
      {row('音频', s.get('sound'))}
      {row('爆点', s.get('why_it_works'))}
      {row('我们怎么用', s.get('use_for_us'))}
      {row('收集人', f"{s.get('by', '')} · {s.get('first_at', '')[:16].replace('T', ' ')}")}
    </dl>
  </div>
</article>""")
    body = "\n".join(cards) or "<p>还没有带关键帧的参考。项目经理用 <code>./vvl ref &lt;链接&gt;</code> 收集。</p>"
    return f"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>热点参考 · {html.escape(pdir.name)}</title>
<style>
:root {{ --bg: #f6f5f2; --card: #fff; --ink: #1d1d1f; --muted: #6b6b70; --line: #e4e2dc; --accent: #2a7f62; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg: #141416; --card: #1e1e22; --ink: #ececef; --muted: #9a9aa2;
  --line: #2e2e34; --accent: #5cc8a1; }} }}
body {{ margin: 0; padding: 24px 16px; background: var(--bg); color: var(--ink);
  font: 15px/1.5 -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif; }}
h1 {{ max-width: 1200px; margin: 0 auto 4px; font-size: 22px; }}
.sub {{ max-width: 1200px; margin: 0 auto 20px; color: var(--muted); }}
.card {{ max-width: 1200px; margin: 0 auto 20px; background: var(--card); border: 1px solid var(--line);
  border-radius: 12px; overflow: hidden; display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); }}
.card img {{ width: 100%; display: block; cursor: zoom-in; }}
.body {{ padding: 16px 20px; }}
h2 {{ margin: 0 0 8px; font-size: 17px; }}
.num {{ background: var(--accent); color: var(--card); border-radius: 6px; padding: 1px 8px; margin-right: 6px; }}
.links a {{ color: var(--accent); margin-right: 14px; font-weight: 600; }}
.links span, .stats {{ color: var(--muted); }}
.stats b {{ color: var(--ink); }}
dl {{ margin: 12px 0 0; display: grid; grid-template-columns: 5.5em 1fr; gap: 6px 10px; }}
dt {{ color: var(--muted); }} dd {{ margin: 0; }}
@media (max-width: 760px) {{ .card {{ grid-template-columns: 1fr; }} }}
</style></head>
<body><h1>热点参考</h1><p class="sub">{len(refs)} 条 · 最新在上 · 点关键帧看大图 · 决定时说编号，比如「翻拍 R3」</p>
{body}
</body></html>"""
