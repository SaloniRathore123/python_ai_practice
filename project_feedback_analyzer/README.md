# Project Feedback Analyzer

An AI-powered customer feedback analyzer that classifies reviews by **sentiment** (positive / negative / neutral), assigns a **score** (1–5), and extracts a **theme** (e.g. delivery, taste, price, service, quality).

The project is split into two parts:

* **FastAPI backend** (`api.py`) — calls Google Gemini to analyze a review and returns structured JSON.
* **Streamlit frontend** (`app.py`) — a friendly UI to enter reviews, pick from samples, view results, and browse history stored in a local SQLite database.

---

## Features

- Analyze free-text customer reviews with Google Gemini
- Sentiment label: `positive`, `negative`, or `neutral`
- Score: integer from 1 (very bad) to 5 (very good)
- Theme: single lowercase topic word (delivery, taste, price, service, quality, …)
- Sidebar with sample reviews to try out quickly
- Persistent history in a local SQLite database (`feedback.db`)
- Download analysis history as a CSV report
- Error handling if the FastAPI backend is not running

---

## Repository layout

```
project_feedback_analyzer/
├── app.py                 # Streamlit frontend UI
├── api.py                 # FastAPI backend (Gemini analysis endpoint)
├── database.py            # SQLite persistence layer
├── feedback.db            # SQLite database (created on first run)
├── sample_reviews.txt     # Example customer reviews
├── pyproject.toml         # Project metadata & dependencies
├── uv.lock                # Locked dependency versions
├── .python-version        # Python version pin
├── .gitignore
└── README.md
```

---

## Prerequisites

- Python 3.14+
- A Google Gemini API key (set as `GOOGLE_API_KEY` in a `.env` file or your environment)
- The Python package manager [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

---

## Installation

Clone the repository and sync dependencies:

```bash
cd project_feedback_analyzer
uv sync
```

If you are using `pip` instead:

```bash
pip install -r pyproject.toml   # or install the listed dependencies manually
```

Create a `.env` file in the project root with your Gemini API key:

```ini
GOOGLE_API_KEY=your_gemini_api_key_here
```

> The backend loads this file via `python-dotenv`, so `GOOGLE_API_KEY` must be available when running `api.py`.

---

## How to run

You need **two terminals**: one for the FastAPI backend and one for the Streamlit UI.

### 1. Start the FastAPI backend

```bash
cd project_feedback_analyzer

# With uv
uv run api.py

# Or with uvicorn directly
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000` with a POST `/analyze` endpoint.

### 2. Start the Streamlit UI

In a second terminal:

```bash
cd project_feedback_analyzer

# With uv
uv run streamlit run app.py

# Or with streamlit directly
streamlit run app.py
```

Open the URL shown by Streamlit (usually `http://localhost:8501`) in your browser.

---

## Using the UI

1. **Enter a review** in the text area, or pick one from the **Sample Reviews** dropdown in the sidebar and click **Use selected review**.
2. Click **Analyze review** to send it to the FastAPI backend.
3. View the result: sentiment (with color badge), score out of 5, and theme.
4. Browse your **Recent Analyses** below — each entry shows the review text, sentiment badge, score, and theme.
5. Use the sidebar to **Download Report (CSV)** or **Clear session view**.

---

## API endpoint

`POST /analyze`

Request body:
```json
{
  "text": "The food was delicious but the delivery took over an hour."
}
```

Response:
```json
{
  "label": "negative",
  "score": 2,
  "theme": "delivery"
}
```

---

## Sample reviews

The bundled `sample_reviews.txt` contains 10 example reviews covering food quality, delivery speed, pricing, service, app stability, and value for money. You can load any of them from the sidebar to try the analyzer instantly.

---

## Notes

- The Streamlit app expects the FastAPI server at `http://localhost:8000` (`API_BASE_URL` in `app.py`). If the backend isn't running, you'll see a connection error when analyzing.
- History is stored locally in `feedback.db` (SQLite) and persists across Streamlit sessions.
- Add `feedback.db` to `.gitignore` if you don't want to track the local database.

