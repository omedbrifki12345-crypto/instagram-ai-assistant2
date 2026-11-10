import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI()

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
        model="gemini-2.5-flash",
        contents=f"""
        Create a short Instagram Reel script about {request.topic}.
        Include a hook, 3 scenes, and an ending.
        """
    )

    return {"script": response.text}
