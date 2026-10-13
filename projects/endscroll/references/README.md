# References — other people's videos, saved so the director can actually look and listen

The director cannot open TikTok, Reels or Shorts pages. It can read files in this folder: it looks at images, extracts frames from video files, measures and transcribes audio. So a reference is only useful once its files are here.

One subfolder per video, named `<account>_<short-slug>`, e.g. `calmlings_done_scrolling/`.

```
references/
└── calmlings_done_scrolling/
    ├── video.mp4        # best: the video file itself, with sound (saved or screen-recorded)
    ├── 00_first.png     # if no video file: the very first frame
    ├── 01_1s.png        #   about 1 second in
    ├── 02_3s.png        #   about 3 seconds in
    ├── 03_mid.png       #   the middle
    ├── 04_end.png       #   the last frame
    ├── audio.m4a        # if no video file: a recording of the sound, start to end
    └── notes.md         # see below
```

`video.mp4` alone is enough; the screenshots and the audio recording are the fallback when the video cannot be saved.

`notes.md`, in English, as much as you can observe:

- URL; account; views, likes, comments, shares, saves; length in seconds; date posted.
- Sound: the sound name and author shown on the page; is it the account's own sound or someone else's; how many videos use that sound.
- What you hear, second by second: music (instrument, tempo, mood), speech or singing verbatim, sound effects, silences.
- Does the character's mouth move with the words (lip-sync), or is the voice laid over a character that does not open its mouth?
- On-screen text, verbatim, with when each line appears and disappears, where it sits, and roughly how big.
- First frame: what is in it, how much of the frame the character fills, the background, the colours.
- Caption and hashtags verbatim; the pinned or top comment.

After saving, update the signal for that URL so the files are linked:

    vvl add signal --by <you> --json '{"url": "<the video URL>", "platform": "...", "kind": "video", "title": "...", "summary": "...", "media": ["references/<folder>/video.mp4"]}'

These files are for study only. Never repost them, and never use their audio or pictures in our own videos.
