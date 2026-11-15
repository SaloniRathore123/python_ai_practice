from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

app = FastAPI()

# What the caller must send using the POST method
class Review(BaseModel):
    text: str

class Analysis(BaseModel):
    label: str
    score: int
    theme: str

@app.post("/analyze")
def analyze_text(review: Review):
    response = client.models.generate_content(
        model ="gemini-3.5-flash",
        contents=(
            "Analyze this customer reviews.\n"
            "label must be one of the following: positive, negative, neutral.\n"
            "score must be a number from 1 (very bad) to 5 (very good).\n"
            "theme must be one lowercase word for the main topic of the review."
            "(for example: delivery, taste, price, service, quality)\n"
            f"Review: {review.text}\n"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Analysis
        )
    )
    return response.parsed