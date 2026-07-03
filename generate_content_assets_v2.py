from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
import requests


# =========================================================
# CONFIG
# =========================================================
TRANSCRIPTS_ROOT = Path(r"D:\Desktop\Apps\Video Transcriber\output\transcripts")
OUTPUT_ROOT = Path(r"D:\Desktop\Apps\Video Transcriber\output\content_v2")

VIDEO_OUTPUT_ROOT = OUTPUT_ROOT / "videos"
COURSE_OUTPUT_ROOT = OUTPUT_ROOT / "courses"

VIDEO_CSV_PATH = OUTPUT_ROOT / "video_content_index.csv"
COURSE_CSV_PATH = OUTPUT_ROOT / "course_content_index.csv"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

SKIP_EXISTING = True
MAX_VIDEO_TRANSCRIPT_CHARS = 18000
MAX_COURSE_TRANSCRIPT_CHARS = 30000


# =========================================================
# PERSONAL BRAND CONFIG
# Edit this section to match your real voice and audience
# =========================================================
BRAND_CONFIG = {
    "brand_name": "Khodor Ghalayini",
    "brand_tagline": "Abu Dhabi Property Decisions, Engineered",

    "your_role": (
        "Engineering-minded Abu Dhabi property advisor, independent real estate consultant, "
        "and AI-enabled strategist helping buyers and investors make smarter property decisions"
    ),

    "audience": (
        "serious Abu Dhabi property buyers, investors, and end-users who want structured, "
        "data-driven guidance, curated opportunities, and clear decisions without pressure "
        "or generic broker sales tactics"
    ),

    "tone": (
        "premium, calm, analytical, trustworthy, structured, direct, human, clear, "
        "confident, non-pushy, and non-corny"
    ),

    "style_rules": [
        "Do not sound like a typical real estate broker.",
        "Do not use hype, pressure, or salesy language.",
        "Avoid generic motivational content.",
        "Use short, structured paragraphs for clarity.",
        "Prefer clarity and precision over fancy wording.",
        "Write like an advisor, not a salesperson.",
        "Explain reasoning, not just conclusions.",
        "Use real-world logic and practical thinking.",
        "Make insights feel experience-driven, not theoretical.",
        "Include clear takeaways and decision guidance.",
        "Focus on helping the reader choose, not just learn.",
        "Keep language simple but intelligent.",
    ],

    "content_goals": [
        "build high-trust authority in Abu Dhabi real estate",
        "educate buyers and investors with structured insights",
        "position as an engineering-minded, data-driven advisor",
        "differentiate from generic brokers and listing platforms",
        "generate qualified leads through value-driven content",
        "support decision-making, not just provide information",
    ],

    "differentiators": [
        "Engineering mindset applied to real estate decisions",
        "Independent, trust-first advisory approach",
        "AI-powered tools and structured analysis",
        "Curated opportunities instead of overwhelming listings",
        "Focus on fit, risk, and long-term value",
    ],

    "content_pillars": [
        "Abu Dhabi new launches",
        "community and area guides",
        "property investment strategy",
        "off-plan vs ready education",
        "project comparisons",
        "engineer's verdict analysis",
        "buyer decision frameworks",
    ],
}


# =========================================================
# JSON SCHEMAS
# =========================================================
VIDEO_CONTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "key_takeaways": {"type": "array", "items": {"type": "string"}},
        "golden_nuggets": {"type": "array", "items": {"type": "string"}},
        "actions_to_take": {"type": "array", "items": {"type": "string"}},
        "linkedin_posts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "post": {"type": "string"},
                    "cta": {"type": "string"},
                },
                "required": ["hook", "post", "cta"],
            },
        },
        "brand_rewritten_posts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "post": {"type": "string"},
                    "cta": {"type": "string"},
                },
                "required": ["hook", "post", "cta"],
            },
        },
        "short_video_scripts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "script": {"type": "string"},
                    "cta": {"type": "string"},
                },
                "required": ["hook", "script", "cta"],
            },
        },
        "brand_video_scripts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "script": {"type": "string"},
                    "cta": {"type": "string"},
                },
                "required": ["hook", "script", "cta"],
            },
        },
        "hooks": {"type": "array", "items": {"type": "string"}},
        "image_prompts": {"type": "array", "items": {"type": "string"}},
        "email_draft": {"type": "string"},
    },
    "required": [
        "title",
        "summary",
        "key_takeaways",
        "golden_nuggets",
        "actions_to_take",
        "linkedin_posts",
        "brand_rewritten_posts",
        "short_video_scripts",
        "brand_video_scripts",
        "hooks",
        "image_prompts",
        "email_draft",
    ],
}

COURSE_CONTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "course_summary": {"type": "string"},
        "main_themes": {"type": "array", "items": {"type": "string"}},
        "best_lessons": {"type": "array", "items": {"type": "string"}},
        "golden_nuggets": {"type": "array", "items": {"type": "string"}},
        "common_mistakes_to_avoid": {"type": "array", "items": {"type": "string"}},
        "action_plan": {"type": "array", "items": {"type": "string"}},
        "brand_angles": {"type": "array", "items": {"type": "string"}},
        "linkedin_post_ideas": {"type": "array", "items": {"type": "string"}},
        "video_content_ideas": {"type": "array", "items": {"type": "string"}},
        "newsletter_angle": {"type": "string"},
        "brand_article": {"type": "string"},
    },
    "required": [
        "course_title",
        "course_summary",
        "main_themes",
        "best_lessons",
        "golden_nuggets",
        "common_mistakes_to_avoid",
        "action_plan",
        "brand_angles",
        "linkedin_post_ideas",
        "video_content_ideas",
        "newsletter_angle",
        "brand_article",
    ],
}


# =========================================================
# HELPERS
# =========================================================
def list_video_transcripts(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.txt")
        if p.name != "_combined_transcript.txt"
    )


def list_course_transcripts(root: Path) -> list[Path]:
    return sorted(root.rglob("_combined_transcript.txt"))


def truncate_text(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Transcript truncated for processing]"


def relative_folder_from_transcripts(path: Path) -> Path:
    return path.parent.relative_to(TRANSCRIPTS_ROOT)


def video_json_output_path(transcript_path: Path) -> Path:
    rel = relative_folder_from_transcripts(transcript_path)
    out_dir = VIDEO_OUTPUT_ROOT / rel
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{transcript_path.stem}_content.json"


def video_md_output_path(transcript_path: Path) -> Path:
    rel = relative_folder_from_transcripts(transcript_path)
    out_dir = VIDEO_OUTPUT_ROOT / rel
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{transcript_path.stem}_content.md"


def course_json_output_path(combined_path: Path) -> Path:
    rel = relative_folder_from_transcripts(combined_path)
    out_dir = COURSE_OUTPUT_ROOT / rel
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "course_summary.json"


def course_md_output_path(combined_path: Path) -> Path:
    rel = relative_folder_from_transcripts(combined_path)
    out_dir = COURSE_OUTPUT_ROOT / rel
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "course_summary.md"


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def call_ollama_structured(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "format": schema,
            "stream": False,
        },
        timeout=1200,
    )
    response.raise_for_status()
    data = response.json()
    raw = data.get("response", "").strip()
    return json.loads(raw)


def brand_context_text() -> str:
    rules = "\n".join(f"- {rule}" for rule in BRAND_CONFIG["style_rules"])
    goals = "\n".join(f"- {goal}" for goal in BRAND_CONFIG["content_goals"])

    return f"""
Personal brand context:
- Brand name: {BRAND_CONFIG['brand_name']}
- Role: {BRAND_CONFIG['your_role']}
- Audience: {BRAND_CONFIG['audience']}
- Tone: {BRAND_CONFIG['tone']}

Style rules:
{rules}

Content goals:
{goals}
""".strip()


# =========================================================
# PROMPTS
# =========================================================
def build_video_prompt(title: str, transcript: str) -> str:
    return f"""
You are a content strategist, educator, and personal-brand ghostwriter.

You are given a transcript from a course video.

Your tasks:
1. Extract the real value from the transcript.
2. Summarize the lesson clearly.
3. Produce useful content assets.
4. Rewrite some content in the user's personal-brand voice.

{brand_context_text()}

Return structured output with:
- title
- summary
- key_takeaways
- golden_nuggets
- actions_to_take
- linkedin_posts (general publishable versions)
- brand_rewritten_posts (rewritten in my personal brand voice)
- short_video_scripts (general versions)
- brand_video_scripts (rewritten in my personal brand voice)
- hooks
- image_prompts
- email_draft

Rules:
- Be practical.
- Do not invent facts not supported by the transcript.
- Clean up transcript noise where needed.
- Make content useful, specific, and publishable after light editing.
- Brand rewritten content should feel natural, personal, and experience-driven.
- Avoid generic AI-style phrasing.

Video title:
{title}

Transcript:
\"\"\"
{transcript}
\"\"\"
""".strip()


def build_course_prompt(course_title: str, transcript: str) -> str:
    return f"""
You are a content strategist, knowledge synthesizer, and personal-brand ghostwriter.

You are given a combined transcript from a full course folder, containing multiple lessons.

Your tasks:
1. Synthesize the course into its most important ideas.
2. Extract the best lessons and most useful insights.
3. Turn the course into content angles for a personal brand.

{brand_context_text()}

Return structured output with:
- course_title
- course_summary
- main_themes
- best_lessons
- golden_nuggets
- common_mistakes_to_avoid
- action_plan
- brand_angles
- linkedin_post_ideas
- video_content_ideas
- newsletter_angle
- brand_article

Rules:
- Be practical and specific.
- Do not invent facts.
- Distill the course into what matters most.
- Make brand angles useful for social content, authority building, and audience growth.
- The brand article should read like a strong educational post or newsletter article in my voice.

Course folder title:
{course_title}

Combined transcript:
\"\"\"
{transcript}
\"\"\"
""".strip()


# =========================================================
# MARKDOWN RENDERERS
# =========================================================
def render_video_markdown(data: dict[str, Any]) -> str:
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
    lines.append("")

    lines.append("## Personal-Brand Rewritten Posts")
    for i, post in enumerate(data.get("brand_rewritten_posts", []), start=1):
        lines.append(f"### Brand Post {i}")
        lines.append(f"**Hook:** {post.get('hook', '')}")
        lines.append("")
        lines.append(post.get("post", ""))
        lines.append("")
        lines.append(f"**CTA:** {post.get('cta', '')}")
        lines.append("")
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
    lines.append("")

    lines.append("## Personal-Brand Video Scripts")
    for i, script in enumerate(data.get("brand_video_scripts", []), start=1):
        lines.append(f"### Brand Video Script {i}")
        lines.append(f"**Hook:** {script.get('hook', '')}")
        lines.append("")
        lines.append(script.get("script", ""))
        lines.append("")
        lines.append(f"**CTA:** {script.get('cta', '')}")
        lines.append("")
    lines.append("")

    lines.append("## Image Prompts")
    for item in data.get("image_prompts", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Email Draft")
    lines.append(data.get("email_draft", ""))
    lines.append("")

    return "\n".join(lines)


def render_course_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {data.get('course_title', 'Untitled Course')}")
    lines.append("")

    lines.append("## Course Summary")
    lines.append(data.get("course_summary", ""))
    lines.append("")

    lines.append("## Main Themes")
    for item in data.get("main_themes", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Best Lessons")
    for item in data.get("best_lessons", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Golden Nuggets")
    for item in data.get("golden_nuggets", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Common Mistakes To Avoid")
    for item in data.get("common_mistakes_to_avoid", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Action Plan")
    for item in data.get("action_plan", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Personal Brand Angles")
    for item in data.get("brand_angles", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## LinkedIn Post Ideas")
    for item in data.get("linkedin_post_ideas", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Video Content Ideas")
    for item in data.get("video_content_ideas", []):
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Newsletter Angle")
    lines.append(data.get("newsletter_angle", ""))
    lines.append("")

    lines.append("## Brand Article")
    lines.append(data.get("brand_article", ""))
    lines.append("")

    return "\n".join(lines)


# =========================================================
# CSV HELPERS
# =========================================================
def append_video_csv(row: dict[str, str]) -> None:
    file_exists = VIDEO_CSV_PATH.exists()
    with open(VIDEO_CSV_PATH, "a", newline="", encoding="utf-8") as f:
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


def append_course_csv(row: dict[str, str]) -> None:
    file_exists = COURSE_CSV_PATH.exists()
    with open(COURSE_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "course_folder",
                "combined_transcript_path",
                "json_output_path",
                "md_output_path",
                "status",
                "error",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# =========================================================
# PROCESSORS
# =========================================================
def process_video_transcript(transcript_path: Path) -> None:
    out_json = video_json_output_path(transcript_path)
    out_md = video_md_output_path(transcript_path)

    if SKIP_EXISTING and out_json.exists() and out_md.exists():
        print(f"Skipping video content: {transcript_path.name}")
        append_video_csv({
            "transcript_name": transcript_path.name,
            "transcript_path": str(transcript_path),
            "json_output_path": str(out_json),
            "md_output_path": str(out_md),
            "status": "skipped_existing",
            "error": "",
        })
        return

    try:
        print(f"Generating video content: {transcript_path.name}")

        transcript_text = transcript_path.read_text(encoding="utf-8", errors="ignore")
        transcript_text = truncate_text(transcript_text, MAX_VIDEO_TRANSCRIPT_CHARS)

        prompt = build_video_prompt(transcript_path.stem, transcript_text)
        data = call_ollama_structured(prompt, VIDEO_CONTENT_SCHEMA)

        save_text(out_json, json.dumps(data, indent=2, ensure_ascii=False))
        save_text(out_md, render_video_markdown(data))

        append_video_csv({
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
        append_video_csv({
            "transcript_name": transcript_path.name,
            "transcript_path": str(transcript_path),
            "json_output_path": str(out_json),
            "md_output_path": str(out_md),
            "status": "failed",
            "error": f"{type(e).__name__}: {e}",
        })
        print(f"Failed video content: {transcript_path.name} -> {type(e).__name__}: {e}")


def process_course_transcript(combined_path: Path) -> None:
    out_json = course_json_output_path(combined_path)
    out_md = course_md_output_path(combined_path)

    rel_folder = relative_folder_from_transcripts(combined_path)
    course_folder_name = str(rel_folder)

    if SKIP_EXISTING and out_json.exists() and out_md.exists():
        print(f"Skipping course content: {course_folder_name}")
        append_course_csv({
            "course_folder": course_folder_name,
            "combined_transcript_path": str(combined_path),
            "json_output_path": str(out_json),
            "md_output_path": str(out_md),
            "status": "skipped_existing",
            "error": "",
        })
        return

    try:
        print(f"Generating course content: {course_folder_name}")

        transcript_text = combined_path.read_text(encoding="utf-8", errors="ignore")
        transcript_text = truncate_text(transcript_text, MAX_COURSE_TRANSCRIPT_CHARS)

        prompt = build_course_prompt(course_folder_name, transcript_text)
        data = call_ollama_structured(prompt, COURSE_CONTENT_SCHEMA)

        save_text(out_json, json.dumps(data, indent=2, ensure_ascii=False))
        save_text(out_md, render_course_markdown(data))

        append_course_csv({
            "course_folder": course_folder_name,
            "combined_transcript_path": str(combined_path),
            "json_output_path": str(out_json),
            "md_output_path": str(out_md),
            "status": "success",
            "error": "",
        })

        print(f"Saved: {out_json}")
        print(f"Saved: {out_md}")

    except Exception as e:
        append_course_csv({
            "course_folder": course_folder_name,
            "combined_transcript_path": str(combined_path),
            "json_output_path": str(out_json),
            "md_output_path": str(out_md),
            "status": "failed",
            "error": f"{type(e).__name__}: {e}",
        })
        print(f"Failed course content: {course_folder_name} -> {type(e).__name__}: {e}")


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    VIDEO_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    COURSE_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    video_transcripts = list_video_transcripts(TRANSCRIPTS_ROOT)
    course_transcripts = list_course_transcripts(TRANSCRIPTS_ROOT)

    print(f"Found {len(video_transcripts)} video transcript(s).")
    print(f"Found {len(course_transcripts)} combined course transcript(s).")

    for transcript_path in video_transcripts:
        process_video_transcript(transcript_path)

    for combined_path in course_transcripts:
        process_course_transcript(combined_path)

    print("All done.")


if __name__ == "__main__":
    main()