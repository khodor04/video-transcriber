from faster_whisper import WhisperModel

video_path = r"G:\Videos\Course Name\video.mp4"

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(video_path, beam_size=1)

with open("transcript.txt", "w", encoding="utf-8") as f:
    for segment in segments:
        f.write(segment.text + "\n")

print("Done")
print("Detected language:", info.language)