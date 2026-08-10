"""Streamlit interface for comparing recipes against weeknight constraints."""

from __future__ import annotations

import os

import streamlit as st

from main import configure_logging, load_dotenv_file, run


def render_app() -> None:
    """Render the search form, ranked comparison, and actionable errors."""
    load_dotenv_file()
    configure_logging(os.getenv("LOG_LEVEL", "INFO"), os.getenv("LOG_FILE", "logs/weeknight-recipe-scout.log"))
    st.set_page_config(page_title="Weeknight Recipe Scout", page_icon="🍲", layout="wide")
    st.title("Weeknight Recipe Scout")
    st.write("For busy cooks who want a realistic dinner: set your time and calorie limits, then compare the best matches.")

    with st.sidebar:
        st.header("Your weeknight")
        search = st.text_input("What sounds good?", value=os.getenv("RECIPE_SEARCH", "chicken"))
        ingredients = st.text_input("Ingredients you want included", value=os.getenv("RECIPE_INGREDIENTS", ""), help="Separate multiple ingredients with commas.")
        max_prep = st.slider("Maximum prep time", 5, 120, int(os.getenv("MAX_PREP_MINUTES", "30")), 5, format="%d minutes")
        max_calories = st.slider("Maximum calories", 100, 1500, int(os.getenv("MAX_CALORIES", "650")), 50)
        per_page = st.number_input("Recipes to compare", min_value=1, max_value=50, value=int(os.getenv("RECIPE_PER_PAGE", "10")))
        api_key = st.text_input("Recipe API key", value=os.getenv("RECIPE_API_KEY", ""), type="password", help="Stored only for this session. For local CLI use, put RECIPE_API_KEY in .env.")

    if st.button("Find my best options", type="primary"):
        try:
            summary, raw_path, processed_path = run(api_key, search, ingredients, 1, int(per_page), max_prep, max_calories)
            matches = summary["recommendations"]
            if not matches:
                st.warning("No complete recipes met both limits. Increase one limit or try a broader search.")
            else:
                top = matches[0]
                st.success(f"Top pick: {top['name']} — {top['prep_time_minutes']} minutes and {top['calories']} calories.")
                columns = ["recommendation_rank", "name", "cuisine", "difficulty", "prep_time_minutes", "calories", "instruction_count"]
                st.subheader("Compare the matches")
                st.dataframe([{key: recipe.get(key) for key in columns} for recipe in matches], hide_index=True, use_container_width=True)
            st.caption(f"Evidence saved to {raw_path}; processed results saved to {processed_path}.")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not fetch recipes: {exc}. Check the API key and internet connection, then try again.")


if __name__ == "__main__":
    render_app()
