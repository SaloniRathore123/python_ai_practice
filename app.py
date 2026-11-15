import streamlit as st
import requests
import csv
import io
from typing import List, Dict, Optional
from database import init_db, save_feedback, load_feedback_history

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Project Feedback Analyzer",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded",
)

API_BASE_URL = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Initialize Database
# ---------------------------------------------------------------------------
init_db()  # Creates the SQLite database and feedback table if it doesn't exist

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    # Load persistent history from the SQLite database
    st.session_state.history = load_feedback_history()  

if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = ""

if "review_text" not in st.session_state:
    st.session_state.review_text = ""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_sample_reviews() -> List[str]:
    """Load sample reviews from the bundled sample file."""
    try:
        with open("sample_reviews.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def analyze_review(text: str) -> Dict:
    """Send a review to the FastAPI backend and return the analysis."""
    base_url = API_BASE_URL.rstrip("/")
    response = requests.post(f"{base_url}/analyze", json={"text": text}, timeout=60)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("📝 Project Feedback Analyzer")
st.caption("Analyze customer reviews with AI — sentiment, score, and theme.")

st.divider()

# Sidebar: sample reviews
st.sidebar.header("Sample Reviews")
sample_reviews = load_sample_reviews()
if sample_reviews:
    chosen = st.sidebar.selectbox(
        "Pick a sample review to analyze:",
        options=["—"] + sample_reviews,
        index=0,
        key="sample_select",
    )
    if chosen != "—":
        st.session_state.selected_sample = chosen
        if st.sidebar.button("Use selected review", use_container_width=True):
            st.session_state.review_text = chosen
else:
    st.sidebar.info("No sample reviews found.")

st.sidebar.divider()
st.sidebar.subheader("History & Reports")

if st.session_state.history:
    # Button to download history as a CSV report from database records
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["text", "label", "score", "theme"])
    writer.writeheader()
    for entry in st.session_state.history:
        writer.writerow(entry)

    st.sidebar.download_button(
        label="📥 Download Report (CSV)",
        data=output.getvalue(),
        file_name="feedback_report.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.sidebar.button("Clear session view", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    for i, entry in enumerate(reversed(st.session_state.history[-10:]), 1):
        st.sidebar.caption(f"{i}. {entry['text'][:60]}…")
else:
    st.sidebar.caption("No analyses yet.")

# Main input area
st.subheader("Enter a customer review")
review_input = st.text_area(
    "Review text",
    height=160,
    placeholder="e.g. The food was delicious but the delivery took over an hour. Not happy.",
    key="review_text",
)

# Ensure review_text is safely treated as a string
review_text: str = review_input if review_input is not None else ""

col1, col2 = st.columns([1, 1])
with col1:
    analyze_btn = st.button("🔍 Analyze review", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.review_text = ""
        st.rerun()

# Analysis + results
if analyze_btn:
    if not review_text.strip():
        st.warning("Please enter a review before analyzing.")
    else:
        with st.spinner("Analyzing with AI…"):
            try:
                result = analyze_review(review_text.strip())
                label = result.get("label", "neutral").lower()
                score = int(result.get("score", 0))
                theme = result.get("theme", "general")

                # Save feedback persistently to the SQLite database
                save_feedback(
                    review=review_text.strip(),
                    label=label,
                    score=score,
                    theme=theme,
                )

                # Refresh history from the database so new entry appears immediately
                st.session_state.history = load_feedback_history()

                # Display results
                st.divider()
                st.subheader("Analysis Result")

                res_col1, res_col2, res_col3 = st.columns(3)
                with res_col1:
                    label_color = {
                        "positive": "🟢",
                        "negative": "🔴",
                        "neutral": "🟡",
                    }.get(label, "⚪")
                    st.metric("Sentiment", f"{label_color} {label.title()}")
                with res_col2:
                    st.metric("Score", f"{score} / 5")
                with res_col3:
                    st.metric("Theme", theme.title())

                st.divider()
                st.caption(f"Review: _{review_text}_")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the analysis API. "
                    f"Make sure the FastAPI server is running at {API_BASE_URL} "
                    "(e.g. `uv run api.py` or `uvicorn api:app --reload`)."
                )
            except requests.exceptions.HTTPError as exc:
                st.error(f"API returned an error: {exc}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Unexpected error: {exc}")

# History section
if st.session_state.history:
    st.divider()
    st.subheader("Recent Analyses")
    for entry in st.session_state.history:
        with st.container(border=True):
            h_col1, h_col2 = st.columns([4, 1])
            with h_col1:
                st.write(entry["text"])
            with h_col2:
                label = entry["label"].lower()
                badge = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(label, "⚪")
                st.write(f"{badge} {label.title()}")
            st.caption(f"Score: {entry['score']} / 5  •  Theme: {entry['theme'].title()}")

st.divider()
st.caption("Powered by FastAPI + Google Gemini + SQLite + Streamlit")