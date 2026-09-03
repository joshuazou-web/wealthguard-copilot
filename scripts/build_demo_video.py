"""Build narrated clean and captioned WealthGuard demo videos from one cue table."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo-video"
WORK = DEMO / "work"
CUES_PATH = DEMO / "cues.json"
DURATION = 155.0


def run(command: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(command, text=True, capture_output=capture, check=False)
    if result.returncode:
        if capture:
            print(result.stdout)
            print(result.stderr)
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(command)}")
    return result.stdout.strip() if capture else ""


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"


def media_duration(path: Path) -> float:
    output = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture=True,
    )
    return float(output)


def ffmpeg_filter_path(path: Path) -> str:
    """Escape an absolute Windows path for use inside an FFmpeg filter."""
    return path.resolve().as_posix().replace(":", r"\:").replace("'", r"\'")


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    cues = json.loads(CUES_PATH.read_text(encoding="utf-8"))
    srt = DEMO / "wealthguard-demo.zh-CN.srt"
    srt.write_text(
        "\n\n".join(
            f"{index}\n{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{cue['text']}"
            for index, cue in enumerate(cues, 1)
        )
        + "\n",
        encoding="utf-8",
    )

    edge_tts = shutil.which("edge-tts")
    if not edge_tts:
        raise RuntimeError("edge-tts is required")
    audio_files: list[Path] = []
    for index, cue in enumerate(cues, 1):
        output = WORK / f"cue-{index:02d}.mp3"
        run(
            [
                edge_tts,
                "--voice",
                "zh-CN-YunxiNeural",
                "--rate=-5%",
                "--text",
                cue["text"],
                "--write-media",
                str(output),
            ]
        )
        spoken = media_duration(output)
        available = cue["end"] - cue["start"] - 0.4
        if spoken > available:
            raise RuntimeError(f"Cue {index} audio {spoken:.2f}s exceeds safe duration {available:.2f}s")
        audio_files.append(output)

    filter_parts = []
    mixed_labels = []
    for index, (cue, _) in enumerate(zip(cues, audio_files, strict=True)):
        delay = round(cue["start"] * 1000)
        label = f"a{index}"
        filter_parts.append(f"[{index}:a]adelay={delay}|{delay}[{label}]")
        mixed_labels.append(f"[{label}]")
    filter_parts.append(
        "".join(mixed_labels) + f"amix=inputs={len(audio_files)}:duration=longest:normalize=0,"
        f"loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:{DURATION}[out]"
    )
    narration = DEMO / "wealthguard-demo-narration.m4a"
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for audio in audio_files:
        command.extend(["-i", str(audio)])
    command.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[out]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(narration),
        ]
    )
    run(command)

    recordings = sorted(WORK.glob("*.webm"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not recordings:
        raise RuntimeError("No Playwright recording found in demo-video/work")
    source = recordings[0]
    clean = DEMO / "wealthguard-demo-clean.mp4"
    video_filter = (
        "scale=1920:975:force_original_aspect_ratio=decrease,"
        "pad=1920:975:(ow-iw)/2:(oh-ih)/2:color=0xEEF2EF,"
        "pad=1920:1080:0:0:color=black"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-i",
            str(narration),
            "-vf",
            video_filter,
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-t",
            str(DURATION),
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(clean),
        ]
    )

    captioned = DEMO / "wealthguard-demo-captioned.mp4"
    subtitle_style = (
        "FontName=Microsoft YaHei UI,FontSize=10,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=1,Outline=0.8,Shadow=0,"
        "Alignment=2,MarginL=96,MarginR=96,MarginV=4"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(clean),
            "-vf",
            f"subtitles='{ffmpeg_filter_path(srt)}':force_style='{subtitle_style}'",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(captioned),
        ]
    )
    print(
        json.dumps(
            {
                "srt": str(srt),
                "narration": str(narration),
                "clean": str(clean),
                "captioned": str(captioned),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
