import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

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

@app.get("/")
def home():
    return {"status": "Gemini backend is running!"}

@app.post("/generate-script")
def generate_script(request: VideoRequest):
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=f"Create a short Instagram Reel script about {request.topic}. Include a hook, 3 scenes, and an ending.",
        config={"http_options": {"timeout": 30000}}
    )

    return {"script": response.text}
