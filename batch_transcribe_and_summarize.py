from __future__ import annotations

import csv
import json
import traceback
from pathlib import Path
from typing import Optional
import requests

from faster_whisper import WhisperModel


# =========================
# CONFIG
# =========================
SOURCE_ROOT = Path(r"G:\Videos\Course Name")
OUTPUT_ROOT = Path(r"G:\Videos\Course Name\output")

MODEL_SIZE = "small"          # "small" for speed, "medium" for better accuracy
DEVICE = "cpu"                # change to "cuda" only if NVIDIA GPU is configured
COMPUTE_TYPE = "int8"         # best practical CPU option
BEAM_SIZE = 1
VAD_FILTER = True

TRANSCRIPTS_DIRNAME = "transcripts"
SUMMARIES_DIRNAME = "summaries"
CSV_FILENAME = "index.csv"
LOG_FILENAME = "run_log.txt"

SKIP_EXISTING_TRANSCRIPTS = True
ENABLE_SUMMARIES = True

# Ollama settings
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".m4v",".ts"}


# =========================
# HELPERS
# =========================
def log(message: str) -> None:
    print(message)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_ROOT / LOG_FILENAME, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def ensure_dirs() -> None:
    (OUTPUT_ROOT / TRANSCRIPTS_DIRNAME).mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / SUMMARIES_DIRNAME).mkdir(parents=True, exist_ok=True)


def relative_course_folder(video_path: Path) -> Path:
    """
    Returns the relative folder path under SOURCE_ROOT.
    Example:
    SOURCE_ROOT\Part1\LessonA.mp4 -> Part1
    """
    return video_path.parent.relative_to(SOURCE_ROOT)


def transcript_output_path(video_path: Path) -> Path:
    rel_folder = relative_course_folder(video_path)
    out_dir = OUTPUT_ROOT / TRANSCRIPTS_DIRNAME / rel_folder
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{video_path.stem}.txt"


def summary_output_path(video_path: Path) -> Path:
    rel_folder = relative_course_folder(video_path)
    out_dir = OUTPUT_ROOT / SUMMARIES_DIRNAME / rel_folder
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{video_path.stem}_summary.md"


def combined_transcript_output_path(folder_rel: Path) -> Path:
    out_dir = OUTPUT_ROOT / TRANSCRIPTS_DIRNAME / folder_rel
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "_combined_transcript.txt"


def list_video_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS:
            files.append(p)
    return sorted(files)


def transcribe_video(model: WhisperModel, video_path: Path) -> tuple[str, str]:
    """
    Returns:
        transcript_text, detected_language
    """
    segments, info = model.transcribe(
        str(video_path),
        beam_size=BEAM_SIZE,
        vad_filter=VAD_FILTER,
    )

    lines: list[str] = []
    for segment in segments:
        text = segment.text.strip()
        if text:
            lines.append(text)

    transcript_text = "\n".join(lines).strip()
    language = getattr(info, "language", "unknown")
    return transcript_text, language


def summarize_with_ollama(transcript: str, video_name: str) -> str:
    prompt = f"""
You are summarizing a course video transcript.

Video title:
{video_name}

Your task:
Create a practical, high-quality summary in markdown with these sections:

# Summary
A concise overview of the main ideas.

# Key Takeaways
Bullet points of the most important lessons.

# Golden Nuggets
The smartest, most valuable, or most actionable insights.

# Actions To Take
Specific actions, habits, scripts, or implementation steps the learner should do.

# Quotes / Memorable Lines
Only include if clearly present in the transcript and useful.

Rules:
- Be practical, not fluffy.
- Do not invent facts not supported by the transcript.
- If the transcript is noisy, still extract the clearest useful meaning.
- Use clean markdown.
- Make the output useful for revision and execution.

Transcript:
\"\"\"
{transcript}
\"\"\"
""".strip()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=600,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def append_csv_row(csv_path: Path, row: dict[str, str]) -> None:
    file_exists = csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "video_name",
                "video_path",
                "course_folder",
                "transcript_path",
                "summary_path",
                "language",
                "status",
                "error",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def build_combined_transcripts() -> None:
    transcripts_root = OUTPUT_ROOT / TRANSCRIPTS_DIRNAME
    if not transcripts_root.exists():
        return

    for folder in sorted([p for p in transcripts_root.rglob("*") if p.is_dir()]):
        txt_files = sorted(
            [
                p for p in folder.glob("*.txt")
                if p.name != "_combined_transcript.txt"
            ]
        )
        if not txt_files:
            continue

        combined_parts: list[str] = []
        for txt_file in txt_files:
            content = txt_file.read_text(encoding="utf-8").strip()
            if not content:
                continue

            combined_parts.append(f"{'=' * 80}")
            combined_parts.append(f"FILE: {txt_file.name}")
            combined_parts.append(f"{'=' * 80}")
            combined_parts.append(content)
            combined_parts.append("")

        combined_path = folder / "_combined_transcript.txt"
        write_text_file(combined_path, "\n".join(combined_parts).strip() + "\n")
        log(f"Built combined transcript: {combined_path}")


# =========================
# MAIN
# =========================
def main() -> None:
    ensure_dirs()

    if not SOURCE_ROOT.exists():
        log(f"Source root does not exist: {SOURCE_ROOT}")
        return

    csv_path = OUTPUT_ROOT / CSV_FILENAME

    log("Loading faster-whisper model...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    log("Model loaded.")

    video_files = list_video_files(SOURCE_ROOT)
    if not video_files:
        log("No video files found.")
        return

    log(f"Found {len(video_files)} video file(s).")

    for video_path in video_files:
        transcript_path = transcript_output_path(video_path)
        summary_path = summary_output_path(video_path)
        course_folder = str(relative_course_folder(video_path))

        try:
            if SKIP_EXISTING_TRANSCRIPTS and transcript_path.exists():
                log(f"Skipping existing transcript: {video_path}")

                append_csv_row(
                    csv_path,
                    {
                        "video_name": video_path.name,
                        "video_path": str(video_path),
                        "course_folder": course_folder,
                        "transcript_path": str(transcript_path),
                        "summary_path": str(summary_path) if summary_path.exists() else "",
                        "language": "",
                        "status": "skipped_existing",
                        "error": "",
                    },
                )
                continue

            log(f"Transcribing: {video_path}")
            transcript_text, language = transcribe_video(model, video_path)
            write_text_file(transcript_path, transcript_text)
            log(f"Saved transcript: {transcript_path}")

            saved_summary_path = ""
            if ENABLE_SUMMARIES:
                try:
                    log(f"Summarizing: {video_path.name}")
                    summary_md = summarize_with_ollama(transcript_text, video_path.stem)
                    write_text_file(summary_path, summary_md)
                    saved_summary_path = str(summary_path)
                    log(f"Saved summary: {summary_path}")
                except Exception as summary_error:
                    log(f"Summary failed for {video_path.name}: {summary_error}")

            append_csv_row(
                csv_path,
                {
                    "video_name": video_path.name,
                    "video_path": str(video_path),
                    "course_folder": course_folder,
                    "transcript_path": str(transcript_path),
                    "summary_path": saved_summary_path,
                    "language": language,
                    "status": "success",
                    "error": "",
                },
            )

        except Exception as e:
            error_text = f"{type(e).__name__}: {e}"
            log(f"Error processing {video_path}: {error_text}")
            log(traceback.format_exc())

            append_csv_row(
                csv_path,
                {
                    "video_name": video_path.name,
                    "video_path": str(video_path),
                    "course_folder": course_folder,
                    "transcript_path": str(transcript_path),
                    "summary_path": str(summary_path),
                    "language": "",
                    "status": "failed",
                    "error": error_text,
                },
            )

    build_combined_transcripts()
    log("All done.")


if __name__ == "__main__":
    main()