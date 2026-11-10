import os
import base64
import json
import urllib.request
import urllib.error

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from google import genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://omedbrifki12345-crypto.github.io"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

class VideoRequest(BaseModel):
    topic: str
    ai: Literal["Gemini"] = "Gemini"

class VoiceRequest(BaseModel):
    text: str
    voice: str = "Kore"

@app.get("/")
def home():
    return {"status": "Instagram AI backend is running!"}

@app.post("/generate-script")
def generate_script(request: VideoRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Please enter a topic.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key is missing.")

    prompt = f"""
Create a short, engaging Instagram Reel script about: {topic}

Keep it around 30–45 seconds when spoken.
Use this exact structure:
HOOK:
SCENE 1:
SCENE 2:
SCENE 3:
ENDING:
Use clear, spoken language. Do not include camera directions in the narration.
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        if not response.text:
            raise ValueError("Gemini returned an empty script.")
        return {"script": response.text}
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Script generation failed: {error}"
        )

@app.post("/generate-audio")
def generate_audio(request: VoiceRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="There is no script to narrate.")

    if len(text) > 4500:
        raise HTTPException(
            status_code=400,
            detail="Please keep the narration under 4,500 characters."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key is missing.")

    payload = {
        "contents": [{
            "parts": [{
                "text": "Read this naturally and clearly, like an energetic social-media narrator. Transcript: " + text
            }]
        }],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": request.voice
                    }
                }
            }
        }
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-3.8-flash-tts:generateContent"
    )

    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=55) as response:
            result = json.loads(response.read().decode("utf-8"))

        parts = result["candidates"][0]["content"]["parts"]

        audio_part = next(
            (
                part for part in parts
                if "inlineData" in part
                and "data" in part["inlineData"]
            ),
            None
        )

        if not audio_part:
            raise ValueError("The voice service did not return audio.")

        audio_data = audio_part["inlineData"]["data"]
        mime_type = audio_part["inlineData"].get("mimeType", "audio/wav")

        return {
            "audio": audio_data,
            "mime_type": mime_type
        }

    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise HTTPException(
            status_code=502,
            detail=f"Voice generation failed: {detail[:700]}"
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Voice generation failed: {error}"
        )
