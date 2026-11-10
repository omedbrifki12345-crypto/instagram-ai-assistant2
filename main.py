from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Instagram AI backend is running!"
    }
