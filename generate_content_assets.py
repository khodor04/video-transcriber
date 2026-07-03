from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
import requests


# =========================
# CONFIG
# =========================
TRANSCRIPTS_ROOT = Path(r"D:\Desktop\Apps\Video Transcriber\output\transcripts")
CONTENT_ROOT = Path(r"D:\Desktop\Apps\Video Transcriber\output\content")
CSV_PATH = Path(r"D:\Desktop\Apps\Video Transcriber\output\content_index.csv")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

SKIP_EXISTING = True
MAX_TRANSCRIPT_CHARS = 18000  # keep prompts manageable on local models


# =========================
# JSON SCHEMA
# =========================
CONTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "key_takeaways": {
            "type": "array",
            "items": {"type": "string"}
        },
        "golden_nuggets": {
            "type": "array",
            "items": {"type": "string"}
        },
        "actions_to_take": {
            "type": "array",
            "items": {"type": "string"}
        },
        "linkedin_posts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "post": {"type": "string"},
                    "cta": {"type": "string"}
                },
                "required": ["hook", "post", "cta"]
            }
        },
        "short_video_scripts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "script": {"type": "string"},
                    "cta": {"type": "string"}
                },
                "required": ["hook", "script", "cta"]
            }
        },
        "hooks": {
            "type": "array",
            "items": {"type": "string"}
        },
        "image_prompts": {
            "type": "array",
            "items": {"type": "string"}
        },
        "email_draft": {"type": "string"}
    },
    "required": [
        "title",
        "summary",
        "key_takeaways",
        "golden_nuggets",
        "actions_to_take",
        "linkedin_posts",
        "short_video_scripts",
        "hooks",
        "image_prompts",
        "email_draft"
    ]
}


# =========================
# HELPERS
# =========================
def list_transcripts(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.txt")
        if p.name != "_combined_transcript.txt"
    )


def relative_folder_for_transcript(transcript_path: Path) -> Path:
    return transcript_path.parent.relative_to(TRANSCRIPTS_ROOT)


def json_output_path(transcript_path: Path) -> Path:
    rel = relative_folder_for_transcript(transcript_path)
    out_dir = CONTENT_ROOT / rel
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{transcript_path.stem}_content.json"


def md_output_path(transcript_path: Path) -> Path:
    rel = relative_folder_for_transcript(transcript_path)
    out_dir = CONTENT_ROOT / rel
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{transcript_path.stem}_content.md"


def truncate_text(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Transcript truncated for processing]"


def call_ollama_structured(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "format": schema,
            "stream": False,
        },
        timeout=900,
    )
    response.raise_for_status()
    data = response.json()
    raw = data.get("response", "").strip()
    return json.loads(raw)


def build_prompt(title: str, transcript: str) -> str:
    return f"""
You are a content strategist and educator.

You are given a transcript from a course video.
Your job is to extract practical knowledge and convert it into content assets.

Video title:
{title}

Return structured content with:
- a concise summary
- key takeaways
- golden nuggets
- action steps
- 3 LinkedIn posts
- 2 short video scripts
- 5 strong hooks
- 5 image prompts for social visuals
- 1 email newsletter draft

Rules:
- Be practical and specific.
- Do not invent facts not grounded in the transcript.
- Clean up noisy transcript language when needed.
- Write in a clear, modern, useful style.
- Make the content good enough to publish after light editing.
- For LinkedIn posts, avoid sounding robotic.
- For short video scripts, keep them punchy and engaging.
- For image prompts, describe clear social-media-ready visuals.

Transcript:
\"\"\"
{transcript}
\"\"\"
""".strip()


def markdown_from_content(data: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append(f"# {data.get('title', 'Untitled')}")
    lines.append("")
    lines.append("## Summary")
    lines.append(data.get("summary", ""))
    lines.append("")

    lines.append("## Key Takeaways")
    for item in data.get("key_takeaways", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Golden Nuggets")
    for item in data.get("golden_nuggets", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Actions To Take")
    for item in data.get("actions_to_take", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Hooks")
    for item in data.get("hooks", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## LinkedIn Posts")
    for i, post in enumerate(data.get("linkedin_posts", []), start=1):
        lines.append(f"### LinkedIn Post {i}")
        lines.append(f"**Hook:** {post.get('hook', '')}")
        lines.append("")
        lines.append(post.get("post", ""))
        lines.append("")
        lines.append(f"**CTA:** {post.get('cta', '')}")
        lines.append("")

    lines.append("## Short Video Scripts")
    for i, script in enumerate(data.get("short_video_scripts", []), start=1):
        lines.append(f"### Video Script {i}")
        lines.append(f"**Hook:** {script.get('hook', '')}")
        lines.append("")
        lines.append(script.get("script", ""))
        lines.append("")
        lines.append(f"**CTA:** {script.get('cta', '')}")
        lines.append("")

    lines.append("## Image Prompts")
    for item in data.get("image_prompts", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Email Draft")
    lines.append(data.get("email_draft", ""))
    lines.append("")

    return "\n".join(lines)


def append_csv_row(row: dict[str, str]) -> None:
    file_exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "transcript_name",
                "transcript_path",
                "json_output_path",
                "md_output_path",
                "status",
                "error",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# =========================
# MAIN
# =========================
def main() -> None:
    CONTENT_ROOT.mkdir(parents=True, exist_ok=True)

    transcripts = list_transcripts(TRANSCRIPTS_ROOT)
    if not transcripts:
        print("No transcript files found.")
        return

    print(f"Found {len(transcripts)} transcript(s).")

    for transcript_path in transcripts:
        out_json = json_output_path(transcript_path)
        out_md = md_output_path(transcript_path)

        if SKIP_EXISTING and out_json.exists() and out_md.exists():
            print(f"Skipping existing content: {transcript_path.name}")
            append_csv_row({
                "transcript_name": transcript_path.name,
                "transcript_path": str(transcript_path),
                "json_output_path": str(out_json),
                "md_output_path": str(out_md),
                "status": "skipped_existing",
                "error": "",
            })
            continue

        try:
            print(f"Generating content for: {transcript_path.name}")

            transcript_text = transcript_path.read_text(encoding="utf-8", errors="ignore")
            transcript_text = truncate_text(transcript_text, MAX_TRANSCRIPT_CHARS)

            prompt = build_prompt(transcript_path.stem, transcript_text)
            data = call_ollama_structured(prompt, CONTENT_SCHEMA)

            md = markdown_from_content(data)

            save_text(out_json, json.dumps(data, indent=2, ensure_ascii=False))
            save_text(out_md, md)

            append_csv_row({
                "transcript_name": transcript_path.name,
                "transcript_path": str(transcript_path),
                "json_output_path": str(out_json),
                "md_output_path": str(out_md),
                "status": "success",
                "error": "",
            })

            print(f"Saved: {out_json}")
            print(f"Saved: {out_md}")

        except Exception as e:
            append_csv_row({
                "transcript_name": transcript_path.name,
                "transcript_path": str(transcript_path),
                "json_output_path": str(out_json),
                "md_output_path": str(out_md),
                "status": "failed",
                "error": f"{type(e).__name__}: {e}",
            })
            print(f"Failed: {transcript_path.name} -> {type(e).__name__}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()