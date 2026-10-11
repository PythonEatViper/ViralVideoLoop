# Production — EndScroll

```
production/
├── characters/                 # one reference sheet per character; README.md lists the generation job ids and the hint rules
└── episodes/<name>/
    ├── storyboard.md           # shots, lines, music per shot — reviewed by the boss before credits are spent
    ├── episode.json            # clip order, captions, sound effects (format: engine/tools/assemble.py)
    ├── shots/                  # generated clips
    ├── final.mp4               # the cut the boss reviews
    └── post.md                 # caption, cover frame, pinned comment
```

Cut an episode: `python3 engine/tools/assemble.py projects/endscroll/production/episodes/<name>/episode.json` (run from the repo root; needs ffmpeg and Pillow).

Generation uses Higgsfield through Claude's MCP connection (images: GPT Image 2.5; shots: Seedance 2.0 Mini with character references and native dialogue). Every credit spent is recorded with `./vvl add cost`.

Series bible and episode bank live in the app repo: `Unscroll/docs/growth/video_series_bible_s1.md`, `video_episode_bank.md`.
