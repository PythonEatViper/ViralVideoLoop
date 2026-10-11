# Shared sound and music library

Used by every project. The audio files are not in git; `music/index.json` and this file are.

- `sfx/` — sound effects from Mixkit (free for commercial use, no attribution). See `sfx/README.md`.
- `music/` — background music from Mixkit, tagged by mood in `music/index.json`.
  - `mood` is one of the moods in `knowledge/music_moods.md`: `tension`, `comic`, `reveal`, `soft`.
  - The moods were assigned from Mixkit's own tags, without listening. `checked_by_human` is false until a person has confirmed the mood; set `bpm` at the same time.

In `episode.json`, refer to these files as `assets/sfx/<file>` or `assets/music/<file>`.
