import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-4-hydrogen"

st.set_page_config(page_title="Recipe Generator", page_icon="🍳")
st.title("🍳 Recipe Generator")
st.caption("Powered by Google Gemini")


@st.cache_resource
def get_client():
    return genai.Client()


def generate_recipe(ingredients, cuisine, diet, max_words):
    prompt = f"""
    Generate one food recipe using these ingredients: {", ".join(ingredients)}
    The recipe should be no more than {max_words} words.
    Cuisine: {cuisine}
    Diet: {diet}

    Format the recipe with a title, ingredients list, and step-by-step method.
    """
    response = get_client().models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    return response.text


with st.form("recipe_form"):
    ingredients_text = st.text_area(
        "Ingredients (comma-separated)",
        value="tomatoes, lentils, onion, jeera, salt",
        help="List the ingredients you have, separated by commas.",
    )

    col1, col2 = st.columns(2)
    with col1:
        cuisine = st.selectbox(
            "Cuisine",
            ["Any", "Indian", "Italian", "Mexican", "Chinese", "Thai", "Japanese", "Mediterranean", "American"],
        )
    with col2:
        diet = st.selectbox(
            "Diet",
            ["Any", "Vegetarian", "Vegan", "Jain", "Keto", "Gluten-Free", "Non-Vegetarian"],
        )

    max_words = st.slider("Max words", 50, 400, 150, step=50)

    submitted = st.form_submit_button("Generate Recipe", type="primary")

if submitted:
    ingredients = [i.strip() for i in ingredients_text.split(",") if i.strip()]
    if not ingredients:
        st.error("Please enter at least one ingredient.")
    else:
        with st.spinner("Cooking up a recipe..."):
            try:
                recipe = generate_recipe(ingredients, cuisine, diet, max_words)
                st.markdown("---")
                st.markdown(recipe)
            except Exception as e:
                st.error(f"Failed to generate recipe: {e}")
