from pathlib import Path
from faster_whisper import WhisperModel
import traceback

# Root folder that contains all the course folders/subfolders
ROOT_FOLDER = Path(r"G:\Videos\Course Name")

# Model settings
MODEL_SIZE = "small"      # change to "medium" if you want better accuracy
DEVICE = "cpu"            # use "cuda" only if you have NVIDIA GPU configured
COMPUTE_TYPE = "int8"     # good for CPU speed

# Skip files if transcript already exists
SKIP_EXISTING = True


def transcribe_video(model: WhisperModel, video_path: Path) -> None:
    txt_path = video_path.with_suffix(".txt")

    if SKIP_EXISTING and txt_path.exists():
        print(f"Skipping (already exists): {video_path}")
        return

    print(f"Transcribing: {video_path}")

    segments, info = model.transcribe(
        str(video_path),
        beam_size=1,          # faster
        vad_filter=True       # helps ignore long silent parts
    )

    with open(txt_path, "w", encoding="utf-8") as f:
        for segment in segments:
            text = segment.text.strip()
            if text:
                f.write(text + "\n")

    print(f"Saved: {txt_path}")
    print(f"Detected language: {info.language}")
    print("-" * 60)


def main():
    if not ROOT_FOLDER.exists():
        print(f"Folder does not exist: {ROOT_FOLDER}")
        return

    print("Loading model...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("Model loaded.")
    print("=" * 60)

    video_files = list(ROOT_FOLDER.rglob("*.mp4"))

    if not video_files:
        print("No MP4 files found.")
        return

    print(f"Found {len(video_files)} MP4 file(s).")
    print("=" * 60)

    for video_path in video_files:
        try:
            transcribe_video(model, video_path)
        except Exception as e:
            print(f"Error processing: {video_path}")
            print(f"Error: {e}")
            traceback.print_exc()
            print("-" * 60)

    print("All done.")


if __name__ == "__main__":
    main()