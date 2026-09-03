# Demo video production

The product video is generated from a real browser session rather than a composited mock-up.
One cue table, `demo-video/cues.json`, drives both the Chinese narration and the SRT subtitles.

## Outputs

- `demo-video/wealthguard-demo-captioned.mp4` — 1080p H.264/AAC delivery version.
- `demo-video/wealthguard-demo-clean.mp4` — narrated master without burned-in captions.
- `demo-video/wealthguard-demo.zh-CN.srt` — editable Chinese subtitles.

## Reproduce

1. Start the app at `http://127.0.0.1:8000` using the commands in the README.
2. From `frontend`, install Playwright's Chromium if needed: `npx playwright install chromium`.
3. Record the real interface: `node scripts/record-demo.mjs`.
4. Install `edge-tts` and ensure `ffmpeg` and `ffprobe` are available on `PATH`.
5. From the repository root, run `python scripts/build_demo_video.py`.

The build fails when a spoken line exceeds its cue window. The committed delivery used
`zh-CN-YunxiNeural` at a five-percent slower speaking rate and a 0.4-second safety gap per cue.

## Subtitle safe-area check

The caption master uses a dedicated 105-pixel black band below the 1920×975 interface recording,
so subtitles never cover product controls or evidence. The checked style is Microsoft YaHei UI,
10px ASS scale, 96px horizontal margin, 4px vertical margin, and 0.8px outline.

Run the local `produce-demo-videos` subtitle preflight at 1920×1080 with the same style before
shipping a changed cue table. The committed preflight report passed all 13 cues.

## Truth boundary

The recording shows deterministic local demo flows, cached official documents, and committed
synthetic regression tests. It does not claim real users, live financial-institution deployment,
commercial performance, or investment outcomes.
