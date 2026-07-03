from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
import requests


# =========================================================
# CONFIG
# =========================================================
TRANSCRIPTS_ROOT = Path(r"G:\Videos\Course Name\output\transcripts")
OUTPUT_ROOT = Path(r"G:\Videos\Course Name\output\content_v4")

VIDEO_OUTPUT_ROOT = OUTPUT_ROOT / "videos"
COURSE_OUTPUT_ROOT = OUTPUT_ROOT / "courses"
MASTER_OUTPUT_ROOT = OUTPUT_ROOT / "master"
PUBLISH_QUEUE_ROOT = OUTPUT_ROOT / "publish_queue"

VIDEO_INDEX_CSV = OUTPUT_ROOT / "video_content_index.csv"
COURSE_INDEX_CSV = OUTPUT_ROOT / "course_content_index.csv"
HOOK_BANK_CSV = OUTPUT_ROOT / "hook_bank.csv"
POST_BANK_CSV = OUTPUT_ROOT / "post_bank.csv"
VIDEO_SCRIPT_BANK_CSV = OUTPUT_ROOT / "video_script_bank.csv"
CAROUSEL_BANK_CSV = OUTPUT_ROOT / "carousel_bank.csv"
PUBLISH_QUEUE_CSV = OUTPUT_ROOT / "publish_queue.csv"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

SKIP_EXISTING = True
MAX_VIDEO_TRANSCRIPT_CHARS = 7000
MAX_COURSE_TRANSCRIPT_CHARS = 12000
MAX_MASTER_INPUT_CHARS = 50000


# =========================================================
# BRAND CONFIG
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
# SCHEMAS
# =========================================================
VIDEO_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "key_takeaways": {"type": "array", "items": {"type": "string"}},
        "golden_nuggets": {"type": "array", "items": {"type": "string"}},
        "actions_to_take": {"type": "array", "items": {"type": "string"}},
        "decision_guidance": {"type": "array", "items": {"type": "string"}},
        "content_pillar_fit": {"type": "string"},

        "hooks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "score": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["hook", "score", "reason"]
            }
        },

        "linkedin_posts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "post": {"type": "string"},
                    "cta": {"type": "string"},
                    "score": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["hook", "post", "cta", "score", "reason"]
            }
        },

        "short_video_scripts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hook": {"type": "string"},
                    "script": {"type": "string"},
                    "cta": {"type": "string"},
                    "score": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["hook", "script", "cta", "score", "reason"]
            }
        },

        "instagram_carousels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "slides": {"type": "array", "items": {"type": "string"}},
                    "caption": {"type": "string"},
                    "score": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["title", "slides", "caption", "score", "reason"]
            }
        },

        "newsletter_draft": {"type": "string"},
        "website_article_draft": {"type": "string"},
        "lead_magnet_idea": {"type": "string"},
        "image_prompts": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "title", "summary", "key_takeaways", "golden_nuggets", "actions_to_take",
        "decision_guidance", "content_pillar_fit", "hooks", "linkedin_posts",
        "short_video_scripts", "instagram_carousels", "newsletter_draft",
        "website_article_draft", "lead_magnet_idea", "image_prompts"
    ]
}

COURSE_SCHEMA = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "course_summary": {"type": "string"},
        "main_themes": {"type": "array", "items": {"type": "string"}},
        "best_lessons": {"type": "array", "items": {"type": "string"}},
        "golden_nuggets": {"type": "array", "items": {"type": "string"}},
        "common_mistakes_to_avoid": {"type": "array", "items": {"type": "string"}},
        "action_plan": {"type": "array", "items": {"type": "string"}},
        "abu_dhabi_property_angles": {"type": "array", "items": {"type": "string"}},
        "pillar_mapping": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pillar": {"type": "string"},
                    "angle": {"type": "string"},
                },
                "required": ["pillar", "angle"]
            }
        },
        "linkedin_post_ideas": {"type": "array", "items": {"type": "string"}},
        "video_content_ideas": {"type": "array", "items": {"type": "string"}},
        "newsletter_angle": {"type": "string"},
        "brand_article": {"type": "string"},
        "best_hook_candidates": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "course_title", "course_summary", "main_themes", "best_lessons",
        "golden_nuggets", "common_mistakes_to_avoid", "action_plan",
        "abu_dhabi_property_angles", "pillar_mapping", "linkedin_post_ideas",
        "video_content_ideas", "newsletter_angle", "brand_article",
        "best_hook_candidates"
    ]
}

MASTER_SCHEMA = {
    "type": "object",
    "properties": {
        "library_summary": {"type": "string"},
        "best_global_themes": {"type": "array", "items": {"type": "string"}},
        "best_global_hooks": {"type": "array", "items": {"type": "string"}},
        "best_content_angles": {"type": "array", "items": {"type": "string"}},
        "best_lead_magnet_ideas": {"type": "array", "items": {"type": "string"}},
        "pillar_strategy": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pillar": {"type": "string"},
                    "why_it_fits": {"type": "string"},
                    "example_angles": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["pillar", "why_it_fits", "example_angles"]
            }
        },
        "best_series_ideas": {"type": "array", "items": {"type": "string"}},
        "best_newsletter_series_ideas": {"type": "array", "items": {"type": "string"}},
        "best_short_video_series": {"type": "array", "items": {"type": "string"}},
        "positioning_statement": {"type": "string"},
        "editorial_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "content_type": {"type": "string"},
                    "topic": {"type": "string"},
                    "goal": {"type": "string"},
                },
                "required": ["content_type", "topic", "goal"]
            }
        }
    },
    "required": [
        "library_summary", "best_global_themes", "best_global_hooks",
        "best_content_angles", "best_lead_magnet_ideas", "pillar_strategy",
        "best_series_ideas", "best_newsletter_series_ideas",
        "best_short_video_series", "positioning_statement", "editorial_plan"
    ]
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
    return text if len(text) <= max_chars else text[:max_chars] + "\n\n[TRUNCATED]"

def relative_folder(path: Path) -> Path:
    return path.parent.relative_to(TRANSCRIPTS_ROOT)

def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path: Path, data: dict[str, Any]) -> None:
    save_text(path, json.dumps(data, indent=2, ensure_ascii=False))

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def call_ollama(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "format": schema,
            "stream": False,
        },
        timeout=600,
    )
    response.raise_for_status()
    data = response.json()
    return json.loads(data["response"])

def append_csv(path: Path, fieldnames: list[str], row: dict[str, str]) -> None:
    file_exists = path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def brand_context_text() -> str:
    style_rules = "\n".join(f"- {x}" for x in BRAND_CONFIG["style_rules"])
    content_goals = "\n".join(f"- {x}" for x in BRAND_CONFIG["content_goals"])
    differentiators = "\n".join(f"- {x}" for x in BRAND_CONFIG["differentiators"])
    pillars = "\n".join(f"- {x}" for x in BRAND_CONFIG["content_pillars"])

    return f"""
Brand name: {BRAND_CONFIG['brand_name']}
Brand tagline: {BRAND_CONFIG['brand_tagline']}
Role: {BRAND_CONFIG['your_role']}
Audience: {BRAND_CONFIG['audience']}
Tone: {BRAND_CONFIG['tone']}

Style rules:
{style_rules}

Content goals:
{content_goals}

Differentiators:
{differentiators}

Content pillars:
{pillars}
""".strip()


# =========================================================
# PROMPTS
# =========================================================
def build_video_prompt(title: str, transcript: str) -> str:
    return f"""
You are a senior content strategist and ghostwriter.

Your job is to convert this transcript into high-trust, premium, advisor-style content
for an Abu Dhabi property advisor brand.

{brand_context_text()}

Important:
- The source transcript may not be about real estate.
- Extract transferable principles and intelligently map them into useful
  Abu Dhabi property advisory content where relevant.
- Do not force weak analogies.
- Never sound like a pushy broker.

Return:
- summary
- takeaways
- golden nuggets
- practical action items
- decision guidance
- best-fit content pillar
- scored hook bank
- scored LinkedIn posts
- scored short video scripts
- scored Instagram carousels
- newsletter draft
- website article draft
- lead magnet idea
- image prompts

Video title:
{title}

Transcript:
\"\"\"
{transcript}
\"\"\"
""".strip()

def build_course_prompt(course_title: str, transcript: str) -> str:
    return f"""
You are a senior content strategist and editorial planner.

You are given a combined transcript from a course folder.

Your job is to synthesize the strongest lessons and transform them into
high-trust brand assets for an Abu Dhabi property advisor.

{brand_context_text()}

Important:
- Extract principles, frameworks, mistakes, and decision patterns.
- Map ideas into buyer, investor, off-plan, ready property, project comparison,
  risk analysis, and advisor-style education where relevant.
- Be specific and non-salesy.

Course title:
{course_title}

Combined transcript:
\"\"\"
{transcript}
\"\"\"
""".strip()

def build_master_prompt(master_input: str) -> str:
    return f"""
You are a chief content officer building the editorial brain of a premium Abu Dhabi property advisory brand.

Use the course summaries below to create a strategic master report for the brand.

{brand_context_text()}

Your goal:
- identify the strongest recurring themes
- identify the best hooks and angles
- identify the best lead magnets
- build an editorial plan
- strengthen the positioning of the brand

Course summary inputs:
\"\"\"
{master_input}
\"\"\"
""".strip()


# =========================================================
# OUTPUT PATHS
# =========================================================
def video_json_path(transcript_path: Path) -> Path:
    return VIDEO_OUTPUT_ROOT / relative_folder(transcript_path) / f"{transcript_path.stem}_content.json"

def video_md_path(transcript_path: Path) -> Path:
    return VIDEO_OUTPUT_ROOT / relative_folder(transcript_path) / f"{transcript_path.stem}_content.md"

def course_json_path(combined_path: Path) -> Path:
    return COURSE_OUTPUT_ROOT / relative_folder(combined_path) / "course_summary.json"

def course_md_path(combined_path: Path) -> Path:
    return COURSE_OUTPUT_ROOT / relative_folder(combined_path) / "course_summary.md"

def master_json_path() -> Path:
    return MASTER_OUTPUT_ROOT / "library_master_report.json"

def master_md_path() -> Path:
    return MASTER_OUTPUT_ROOT / "library_master_report.md"


# =========================================================
# MARKDOWN RENDERERS
# =========================================================
def render_video_md(data: dict[str, Any]) -> str:
    lines = [
        f"# {data.get('title', 'Untitled')}",
        "",
        "## Summary",
        data.get("summary", ""),
        "",
        "## Key Takeaways",
    ]
    lines += [f"- {x}" for x in data.get("key_takeaways", [])]
    lines += ["", "## Golden Nuggets"]
    lines += [f"- {x}" for x in data.get("golden_nuggets", [])]
    lines += ["", "## Actions To Take"]
    lines += [f"- {x}" for x in data.get("actions_to_take", [])]
    lines += ["", "## Decision Guidance"]
    lines += [f"- {x}" for x in data.get("decision_guidance", [])]
    lines += ["", "## Content Pillar Fit", data.get("content_pillar_fit", ""), "", "## Hooks"]

    for item in data.get("hooks", []):
        lines += [
            f"- {item.get('hook', '')}",
            f"  - Score: {item.get('score', '')}",
            f"  - Why: {item.get('reason', '')}",
        ]

    lines += ["", "## LinkedIn Posts"]
    for i, post in enumerate(data.get("linkedin_posts", []), start=1):
        lines += [
            f"### LinkedIn Post {i}",
            f"**Hook:** {post.get('hook', '')}",
            "",
            post.get("post", ""),
            "",
            f"**CTA:** {post.get('cta', '')}",
            f"**Score:** {post.get('score', '')}",
            f"**Why it works:** {post.get('reason', '')}",
            "",
        ]

    lines += ["## Short Video Scripts"]
    for i, s in enumerate(data.get("short_video_scripts", []), start=1):
        lines += [
            f"### Script {i}",
            f"**Hook:** {s.get('hook', '')}",
            "",
            s.get("script", ""),
            "",
            f"**CTA:** {s.get('cta', '')}",
            f"**Score:** {s.get('score', '')}",
            f"**Why it works:** {s.get('reason', '')}",
            "",
        ]

    lines += ["## Instagram Carousel Ideas"]
    for i, c in enumerate(data.get("instagram_carousels", []), start=1):
        lines += [f"### Carousel {i}", f"**Title:** {c.get('title', '')}", ""]
        for idx, slide in enumerate(c.get("slides", []), start=1):
            lines.append(f"- Slide {idx}: {slide}")
        lines += [
            "",
            f"**Caption:** {c.get('caption', '')}",
            f"**Score:** {c.get('score', '')}",
            f"**Why it works:** {c.get('reason', '')}",
            "",
        ]

    lines += ["## Newsletter Draft", data.get("newsletter_draft", ""), "", "## Website Article Draft", data.get("website_article_draft", ""), "", "## Lead Magnet Idea", data.get("lead_magnet_idea", ""), "", "## Image Prompts"]
    lines += [f"- {x}" for x in data.get("image_prompts", [])]
    lines += [""]

    return "\n".join(lines)

def render_course_md(data: dict[str, Any]) -> str:
    lines = [
        f"# {data.get('course_title', 'Untitled Course')}",
        "",
        "## Course Summary",
        data.get("course_summary", ""),
        "",
        "## Main Themes",
    ]
    lines += [f"- {x}" for x in data.get("main_themes", [])]
    lines += ["", "## Best Lessons"]
    lines += [f"- {x}" for x in data.get("best_lessons", [])]
    lines += ["", "## Golden Nuggets"]
    lines += [f"- {x}" for x in data.get("golden_nuggets", [])]
    lines += ["", "## Common Mistakes To Avoid"]
    lines += [f"- {x}" for x in data.get("common_mistakes_to_avoid", [])]
    lines += ["", "## Action Plan"]
    lines += [f"- {x}" for x in data.get("action_plan", [])]
    lines += ["", "## Abu Dhabi Property Angles"]
    lines += [f"- {x}" for x in data.get("abu_dhabi_property_angles", [])]
    lines += ["", "## Pillar Mapping"]

    for item in data.get("pillar_mapping", []):
        lines += [f"- **{item.get('pillar', '')}**: {item.get('angle', '')}"]

    lines += ["", "## LinkedIn Post Ideas"]
    lines += [f"- {x}" for x in data.get("linkedin_post_ideas", [])]
    lines += ["", "## Video Content Ideas"]
    lines += [f"- {x}" for x in data.get("video_content_ideas", [])]
    lines += ["", "## Newsletter Angle", data.get("newsletter_angle", ""), "", "## Brand Article", data.get("brand_article", ""), "", "## Best Hook Candidates"]
    lines += [f"- {x}" for x in data.get("best_hook_candidates", [])]
    lines += [""]
    return "\n".join(lines)

def render_master_md(data: dict[str, Any]) -> str:
    lines = [
        "# Library Master Report",
        "",
        "## Library Summary",
        data.get("library_summary", ""),
        "",
        "## Best Global Themes",
    ]
    lines += [f"- {x}" for x in data.get("best_global_themes", [])]
    lines += ["", "## Best Global Hooks"]
    lines += [f"- {x}" for x in data.get("best_global_hooks", [])]
    lines += ["", "## Best Content Angles"]
    lines += [f"- {x}" for x in data.get("best_content_angles", [])]
    lines += ["", "## Best Lead Magnet Ideas"]
    lines += [f"- {x}" for x in data.get("best_lead_magnet_ideas", [])]
    lines += ["", "## Pillar Strategy"]

    for item in data.get("pillar_strategy", []):
        lines += [
            f"### {item.get('pillar', '')}",
            item.get("why_it_fits", ""),
            "",
            "**Example angles:**"
        ]
        lines += [f"- {x}" for x in item.get("example_angles", [])]
        lines += [""]

    lines += ["## Best Series Ideas"]
    lines += [f"- {x}" for x in data.get("best_series_ideas", [])]
    lines += ["", "## Best Newsletter Series Ideas"]
    lines += [f"- {x}" for x in data.get("best_newsletter_series_ideas", [])]
    lines += ["", "## Best Short Video Series"]
    lines += [f"- {x}" for x in data.get("best_short_video_series", [])]
    lines += ["", "## Positioning Statement", data.get("positioning_statement", ""), "", "## Editorial Plan"]

    for item in data.get("editorial_plan", []):
        lines += [f"- **{item.get('content_type', '')}** | {item.get('topic', '')} | Goal: {item.get('goal', '')}"]

    lines += [""]
    return "\n".join(lines)


# =========================================================
# BANKS / QUEUE
# =========================================================
def append_hook_bank(video_name: str, course_folder: str, hooks: list[dict[str, Any]]) -> None:
    for item in hooks:
        append_csv(
            HOOK_BANK_CSV,
            ["video_name", "course_folder", "hook", "score", "reason"],
            {
                "video_name": video_name,
                "course_folder": course_folder,
                "hook": str(item.get("hook", "")),
                "score": str(item.get("score", "")),
                "reason": str(item.get("reason", "")),
            }
        )

def append_post_bank(video_name: str, course_folder: str, posts: list[dict[str, Any]]) -> None:
    for item in posts:
        append_csv(
            POST_BANK_CSV,
            ["video_name", "course_folder", "hook", "post", "cta", "score", "reason"],
            {
                "video_name": video_name,
                "course_folder": course_folder,
                "hook": str(item.get("hook", "")),
                "post": str(item.get("post", "")),
                "cta": str(item.get("cta", "")),
                "score": str(item.get("score", "")),
                "reason": str(item.get("reason", "")),
            }
        )

def append_video_script_bank(video_name: str, course_folder: str, scripts: list[dict[str, Any]]) -> None:
    for item in scripts:
        append_csv(
            VIDEO_SCRIPT_BANK_CSV,
            ["video_name", "course_folder", "hook", "script", "cta", "score", "reason"],
            {
                "video_name": video_name,
                "course_folder": course_folder,
                "hook": str(item.get("hook", "")),
                "script": str(item.get("script", "")),
                "cta": str(item.get("cta", "")),
                "score": str(item.get("score", "")),
                "reason": str(item.get("reason", "")),
            }
        )

def append_carousel_bank(video_name: str, course_folder: str, carousels: list[dict[str, Any]]) -> None:
    for item in carousels:
        append_csv(
            CAROUSEL_BANK_CSV,
            ["video_name", "course_folder", "title", "slides_json", "caption", "score", "reason"],
            {
                "video_name": video_name,
                "course_folder": course_folder,
                "title": str(item.get("title", "")),
                "slides_json": json.dumps(item.get("slides", []), ensure_ascii=False),
                "caption": str(item.get("caption", "")),
                "score": str(item.get("score", "")),
                "reason": str(item.get("reason", "")),
            }
        )

def append_publish_queue_item(
    source_name: str,
    course_folder: str,
    content_type: str,
    title_or_hook: str,
    score: int,
    reason: str,
) -> None:
    append_csv(
        PUBLISH_QUEUE_CSV,
        ["source_name", "course_folder", "content_type", "title_or_hook", "score", "reason"],
        {
            "source_name": source_name,
            "course_folder": course_folder,
            "content_type": content_type,
            "title_or_hook": title_or_hook,
            "score": str(score),
            "reason": reason,
        }
    )

def add_publish_queue_from_video_data(video_name: str, course_folder: str, data: dict[str, Any]) -> None:
    for item in data.get("hooks", []):
        append_publish_queue_item(
            video_name,
            course_folder,
            "hook",
            str(item.get("hook", "")),
            int(item.get("score", 0)),
            str(item.get("reason", "")),
        )

    for item in data.get("linkedin_posts", []):
        append_publish_queue_item(
            video_name,
            course_folder,
            "linkedin_post",
            str(item.get("hook", "")),
            int(item.get("score", 0)),
            str(item.get("reason", "")),
        )

    for item in data.get("short_video_scripts", []):
        append_publish_queue_item(
            video_name,
            course_folder,
            "short_video_script",
            str(item.get("hook", "")),
            int(item.get("score", 0)),
            str(item.get("reason", "")),
        )

    for item in data.get("instagram_carousels", []):
        append_publish_queue_item(
            video_name,
            course_folder,
            "instagram_carousel",
            str(item.get("title", "")),
            int(item.get("score", 0)),
            str(item.get("reason", "")),
        )


# =========================================================
# PROCESSORS
# =========================================================
def process_video(transcript_path: Path) -> None:
    out_json = video_json_path(transcript_path)
    out_md = video_md_path(transcript_path)

    if SKIP_EXISTING and out_json.exists() and out_md.exists():
        print(f"Skipping video: {transcript_path.name}")
        return

    print(f"Generating video content: {transcript_path.name}")
    transcript = truncate_text(read_text(transcript_path), MAX_VIDEO_TRANSCRIPT_CHARS)
    try:
        data = call_ollama(build_video_prompt(transcript_path.stem, transcript), VIDEO_SCHEMA)
    except Exception as e:
        print(f"Retrying once...")
        data = call_ollama(build_video_prompt(transcript_path.stem, transcript), VIDEO_SCHEMA)

    save_json(out_json, data)
    save_text(out_md, render_video_md(data))

    course_folder = str(relative_folder(transcript_path))

    append_csv(
        VIDEO_INDEX_CSV,
        ["transcript_name", "course_folder", "transcript_path", "json_output_path", "md_output_path", "status"],
        {
            "transcript_name": transcript_path.name,
            "course_folder": course_folder,
            "transcript_path": str(transcript_path),
            "json_output_path": str(out_json),
            "md_output_path": str(out_md),
            "status": "success",
        }
    )

    append_hook_bank(transcript_path.name, course_folder, data.get("hooks", []))
    append_post_bank(transcript_path.name, course_folder, data.get("linkedin_posts", []))
    append_video_script_bank(transcript_path.name, course_folder, data.get("short_video_scripts", []))
    append_carousel_bank(transcript_path.name, course_folder, data.get("instagram_carousels", []))
    add_publish_queue_from_video_data(transcript_path.name, course_folder, data)

def process_course(combined_path: Path) -> None:
    out_json = course_json_path(combined_path)
    out_md = course_md_path(combined_path)

    if SKIP_EXISTING and out_json.exists() and out_md.exists():
        print(f"Skipping course: {relative_folder(combined_path)}")
        return

    print(f"Generating course content: {relative_folder(combined_path)}")
    transcript = truncate_text(read_text(combined_path), MAX_COURSE_TRANSCRIPT_CHARS)
    data = call_ollama(build_course_prompt(str(relative_folder(combined_path)), transcript), COURSE_SCHEMA)

    save_json(out_json, data)
    save_text(out_md, render_course_md(data))

    append_csv(
        COURSE_INDEX_CSV,
        ["course_folder", "combined_transcript_path", "json_output_path", "md_output_path", "status"],
        {
            "course_folder": str(relative_folder(combined_path)),
            "combined_transcript_path": str(combined_path),
            "json_output_path": str(out_json),
            "md_output_path": str(out_md),
            "status": "success",
        }
    )

def process_master(course_transcripts: list[Path]) -> None:
    out_json = master_json_path()
    out_md = master_md_path()

    if SKIP_EXISTING and out_json.exists() and out_md.exists():
        print("Skipping master report.")
        return

    inputs = []
    for p in course_transcripts:
        folder_name = str(relative_folder(p))
        content = truncate_text(read_text(p), 6000)
        inputs.append(f"=== COURSE: {folder_name} ===\n{content}")

    master_input = "\n\n".join(inputs)
    master_input = truncate_text(master_input, MAX_MASTER_INPUT_CHARS)

    print("Generating master report...")
    data = call_ollama(build_master_prompt(master_input), MASTER_SCHEMA)

    save_json(out_json, data)
    save_text(out_md, render_master_md(data))


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    VIDEO_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    COURSE_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    MASTER_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    PUBLISH_QUEUE_ROOT.mkdir(parents=True, exist_ok=True)

    video_transcripts = list_video_transcripts(TRANSCRIPTS_ROOT)
    course_transcripts = list_course_transcripts(TRANSCRIPTS_ROOT)

    print(f"Found {len(video_transcripts)} video transcript(s).")
    print(f"Found {len(course_transcripts)} course transcript(s).")

    for transcript_path in video_transcripts:
        try:
            process_video(transcript_path)
        except Exception as e:
            print(f"Failed video {transcript_path.name}: {type(e).__name__}: {e}")

    for combined_path in course_transcripts:
        try:
            process_course(combined_path)
        except Exception as e:
            print(f"Failed course {combined_path}: {type(e).__name__}: {e}")

    try:
        process_master(course_transcripts)
    except Exception as e:
        print(f"Failed master report: {type(e).__name__}: {e}")

    print("All done.")


if __name__ == "__main__":
    main()