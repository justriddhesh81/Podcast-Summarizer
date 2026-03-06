from fastapi import FastAPI, HTTPException
import yt_dlp
import whisper
import os
import time

from summarizer import summarize_text, AVAILABLE_MODELS

app = FastAPI()


whisper_model = whisper.load_model("base")


def download_audio(video_id):
    
    if "&" in video_id:
        video_id = video_id.split("&")[0]

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{video_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    final_file = f"{video_id}.mp3"

    if not os.path.isfile(final_file):
        raise Exception("Audio file not found")

    return final_file


@app.get("/")
def root():
    return {
        "message": "YouTube Summarizer API Running",
        "available_models": list(AVAILABLE_MODELS.keys())
    }


@app.get("/summarize/{video_id}")
def summarize_video(video_id: str, model: str = "bart"):

    if model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Model not supported. Choose from {list(AVAILABLE_MODELS.keys())}"
        )

    try:
        audio_file = download_audio(video_id)

        result = whisper_model.transcribe(audio_file)
        transcript = result["text"]

        if not transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript empty")

        final_summary = summarize_text(transcript, model_key=model)

        os.remove(audio_file)

        return {
            "video_id": video_id,
            "model_used": model,
            "summary": final_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
