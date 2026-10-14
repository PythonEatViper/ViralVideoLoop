---
name: vvl-retro
description: Daily or weekly self-review of the ViralVideoLoop project - pull the newest numbers, compare every recent post with its forecast and its cell in the exploration map, update learnings and the playbook, and propose the next two videos (one remake, one original). Use when the boss asks for a review, a 复盘, "what did we learn", "看看最新反馈", or before planning the next videos.
---

# vvl-retro: review, learn, plan the next two videos

Run from the ViralVideoLoop repo root. Write everything for the boss in Chinese, plainly, highest-level first.

## 1. Pull the facts (token-free commands first)

```
./vvl ingest
./vvl status
./vvl predict --check
./vvl list note --days 2 --json        # what the boss said; follow it
./vvl list comment --days 3 --json
./vvl list incident --days 2 --json
./vvl list signal --days 2 --sort relevance --json
```

Also read `projects/<project>/team/director.md` (standing instructions) and `knowledge/exploration.md`.

## 2. Judge each post published in the last 3 days

For each post and platform:

- Compare the measured signals with the post's `expected` values (`./vvl get post <id>`). Write down which estimates were off and by how much; that is how the estimates improve.
- Compare with the account's own earlier posts at the same age, never with absolute targets.
- First hour near zero means the platform did not distribute it; that is an account or publishing problem, not a content verdict. Say so separately.
- Fill the post's row in the "已经试过的格子" table in `knowledge/exploration.md`.

## 3. Update what we believe

- `./vvl add learning` - add `evidence_for` / `evidence_against` to existing learnings, adjust `confidence`. New claims start as `hypothesis`. Nothing becomes `supported` with fewer than 3 posts behind it.
- Apply the exploration rules (promote a cell after 3 good posts, pause it after 3 bad ones).
- If a forecast threshold was clearly wrong for us, adjust `engine/predict.py` and note it in `knowledge/forecast.md`.

## 4. Propose the next two videos

- **Remake slot (evening):** a viral from the last ~6 months, millions of views, strong script, ideally riding someone else's trend; keep its structure and camera moves, swap in our characters. Name the source URL.
- **Original slot (morning):** borrow a structure from another domain, add an original hook, aim for something rare. Pick a cell of the exploration map we have not tried.
- Score both with `./vvl predict --idea ... --expected ... --why ...`.
- Write a storyboard for each (attention rule: one point of attention at a time; one line of text; plain words) and raise a `storyboard` review. Do not spend credits before the boss approves.

## 5. Report

Write `projects/<project>/plans/<date>.md` (format in `engine/roles/director.md`), then tell the boss in under 15 lines: what the numbers said, what we learned, the two proposals, and what is needed from the boss. Commit locally.

## Rules that always apply

Read `knowledge/attention.md`, `knowledge/dialogue_audio.md`, `knowledge/familiarity.md` and `production/characters/README.md` before writing a storyboard. Tone: upbeat or healing, self-mocking at most, never gloomy. Never a real brand logo; phones get the mint case with a star sticker.
