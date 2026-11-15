from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

app = FastAPI()


@app.get("/")
def read_root():
  return {"message": "Welcome, kaise ho app?"}

@app.get("/margin")
def margin(revenue: float, expense: float):
  profit = revenue - expense
  margin_percent = (profit / revenue) * 100
  return {"profit": profit, "margin_percent": margin_percent}

class Review(BaseModel):
  text: str

class Sentiment(BaseModel):
    label: str
    confidence: float

@app.post("/sentiment")
def analyze_sentiment(review: Review):
  response = client.models.generate_content(
    model="gemini-3.6-flash",  
    contents=(
      "Find the Sentiment of this customer review."
      "Label must be 'positive', 'negative', or 'neutral'"
      "Score must a number from 1(very bad) to 5(very good)."
      f"Review: {review.text}"
    ),
    config=types.GenerateContentConfig(
      response_mime_type="application/json",
      response_schema=Sentiment, 
    )
  )
  return response.parsed
  
  