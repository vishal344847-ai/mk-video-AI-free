from flask import Flask, render_template, request
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# FUNCTIONS
# -----------------------------

def extract_audio(video_path, audio_path):
    command = ["ffmpeg", "-y", "-i", video_path, audio_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def fake_transcription(audio_path):
    # TEMP: Replace later with real AI API
    return "This is a sample transcription of the video. AI will process real content in future."


def simple_summary(text):
    # Simple summary logic (lightweight)
    sentences = text.split(".")
    return ". ".join(sentences[:2])  # first 2 sentences as summary


# -----------------------------
# ROUTES
# -----------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    full_text = ""
    summary_text = ""

    if request.method == "POST":
        video = request.files.get("video")

        if video:
            video_path = os.path.join(UPLOAD_FOLDER, video.filename)
            video.save(video_path)

            audio_path = os.path.join(UPLOAD_FOLDER, "audio.mp3")

            # Step 1: Extract audio
            extract_audio(video_path, audio_path)

            # Step 2: Fake transcription
            full_text = fake_transcription(audio_path)

            # Step 3: Simple summary
            summary_text = simple_summary(full_text)

    return render_template("index.html", full_text=full_text, summary_text=summary_text)


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
