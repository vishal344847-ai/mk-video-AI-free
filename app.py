from flask import Flask, render_template, request
import os
import whisper
import subprocess
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Whisper model
whisper_model = whisper.load_model("base")

# Load summarization model (NO pipeline)
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model_s = AutoModelForSeq2SeqLM.from_pretrained(model_name)


# -----------------------------
# FUNCTIONS
# -----------------------------

def extract_audio(video_path, audio_path):
    command = ["ffmpeg", "-y", "-i", video_path, audio_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]


def summarize_text(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

    summary_ids = model_s.generate(
        inputs["input_ids"],
        max_length=150,
        min_length=40,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def summarize_long_text(text):
    chunk_size = 1000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    final_summary = ""

    for chunk in chunks:
        final_summary += summarize_text(chunk) + "\n"

    return final_summary


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

            # Step 2: Transcribe
            full_text = transcribe_audio(audio_path)

            # Step 3: Summarize
            summary_text = summarize_long_text(full_text)

    return render_template("index.html", full_text=full_text, summary_text=summary_text)


# -----------------------------
# RUN (IMPORTANT FOR DEPLOY)
# -----------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway/Render compatible
    app.run(host="0.0.0.0", port=port)