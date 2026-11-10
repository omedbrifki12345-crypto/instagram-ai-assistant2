import os
import anthropic

from google import genai
from google.genai import types

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://omedbrifki12345-crypto.github.io"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class VideoRequest(BaseModel):
    topic: str
    ai: Literal["Gemini", "Claude"] = "Gemini"


@app.get("/")
def home():
    return {"status": "Instagram AI backend is running!"}


@app.post("/generate-script")
def generate_script(request: VideoRequest):

    prompt = f"""
    Create a short Instagram Reel script about {request.topic}.

    Include:
    HOOK:
    SCENE 1:
    SCENE 2:
    SCENE 3:
    ENDING:

    Make it interesting and engaging.
    """

    try:

        if request.ai == "Gemini":

            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="Gemini API key is missing."
                )

            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=30000)
            )

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            script = response.text

        else:

            api_key = os.getenv("ANTHROPIC_API_KEY")

            if not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="Claude API key is missing."
                )

            client = anthropic.Anthropic(
                api_key=api_key,
                timeout=30.0
            )

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            script = response.content[0].text

        return {"script": script}

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )
