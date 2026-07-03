# Video Transcriber

Local, offline pipeline for transcribing course/lesson videos with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and turning the transcripts into summaries and social/content assets using a locally-hosted [Ollama](https://ollama.com/) model. Nothing is sent to a third-party API — transcription runs on your CPU/GPU and summarization runs against `localhost:11434`.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) running locally with a pulled model (scripts default to `qwen2.5:7b`)
- `pip install -r requirements.txt`

## Scripts

All scripts use hardcoded `CONFIG` sections at the top of the file (source/output paths, model settings) — edit these before running.

| Script | Purpose |
|---|---|
| `transcribe.py` | Minimal example: transcribe a single video file to `transcript.txt`. |
| `batch_transcribe.py` | Recursively transcribe every `.mp4` under a root folder, writing a `.txt` next to each video. |
| `batch_transcribe_and_summarize.py` | Batch transcribe a folder tree, summarize each transcript with Ollama, and log results to a CSV index. |
| `generate_content_assets.py` | Turn existing transcripts into a single structured JSON (summary, key takeaways, golden nuggets, action items) + markdown, per video. |
| `generate_content_assets_v2.py` / `_v3.py` / `_v4.py` | Iterative, more elaborate versions of the content generator: per-video and per-course rollups, hook/post/script/carousel banks, and a personal `BRAND_CONFIG` block used to steer tone and content pillars for social content. Each version adds more output types (v4 is the most complete, including a publish queue). |

## Typical workflow

1. Point a batch script's `SOURCE_ROOT` / `ROOT_FOLDER` at a folder of course videos and run it to produce transcripts under `output/`.
2. Point a `generate_content_assets*.py` script's `TRANSCRIPTS_ROOT` at that output and run it to produce summaries and (in v2+) social content drafts.
3. Review generated CSV indexes and markdown/JSON files under `output/`.

`output/`, `transcript.txt`, and `*.csv` are gitignored since they contain generated transcripts/content from your own source videos.

## Note on `BRAND_CONFIG`

`generate_content_assets_v2.py`+ include a `BRAND_CONFIG` block (voice, tone, content pillars) used to steer generated social copy. Edit it to match your own brand before generating content.
