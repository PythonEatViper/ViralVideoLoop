# Outbox — posts approved for publishing

One subfolder per post. The director creates a folder only after the boss has approved the final cut. Sellers read these folders and never change anything in them.

```
outbox/
└── <YYYY-MM-DD>_<slug>/        # the folder name is the post id
    ├── post.json               # read this first
    ├── video.mp4               # 1080x1920, 30 fps, H.264 + AAC; upload as it is
    ├── cover.jpg               # cover frame (same frame as cover_time_seconds)
    ├── caption.txt             # caption, UTF-8; post it exactly as written
    └── pinned_comment.txt      # comment to post from our account, then pin
```

## Formats

`post.json` has a `format` field. When it is missing, the post is a video.

| `format` | files | goes to |
| --- | --- | --- |
| `video` | `video.mp4`, `cover.jpg`, `caption.txt`, `pinned_comment.txt` | TikTok, Reels, YouTube |
| `images` | `images/01.jpg`, `02.jpg`, … (1080x1350 or 1080x1920, uploaded in file-name order), `caption.txt`, optional `pinned_comment.txt` | TikTok photo post, Reels/Facebook carousel |
| `text` | `title.txt`, `body.md`, optional `images/`; `post.json` names the `community` (e.g. `r/nosurf`) and optional `flair` | Reddit and other text communities |

## post.json

| field | meaning |
| --- | --- |
| `status` | `hold` = being fixed, do not publish. `ready` = approved. |
| `platforms` | where it should go, e.g. `["tiktok", "reels"]` |
| `publish_window` | when to publish (ISO times with offset). If the window has passed, use the same hours on the next day. |
| `ai_generated_label` | turn the platform's AI label on when true |
| `add_music` | `false` = add no sound. Otherwise the mood of the platform sound to add, at the lowest volume. |
| `privacy`, `allow_comments`, `allow_duet`, `allow_stitch`, `cover_time_seconds` | as named |

## How a seller uses it

1. `./vvl outbox --platform <platform>` lists the posts that are `ready` and not yet live on that platform.
2. Publish as the seller prompt describes (`./vvl prompt seller_<platform>`).
3. Report the result: `./vvl add publish --by <staff id> --json '{"post_id": "<folder name>", "platform": "...", "account": "@...", "url": "...", "published_at": "...", "ai_label_on": true, "pinned_comment_posted": true}'`.

A post counts as published on a platform once that `publish` record exists; `post.json` itself is never edited by sellers.
