"""Streamlit interface for comparing recipes against weeknight constraints."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from history import list_recent_runs, record_run
from main import (
    configure_logging,
    filter_recipe_preferences,
    load_dotenv_file,
    load_processed_csv,
    recommend_recipes,
    run,
)

SAMPLE_CSV = Path("data/sample/weeknight-recipes.csv")
FOOD_CHOICES = [
    "Anything",
    "Chicken",
    "Salmon",
    "Vegetarian",
    "Pasta",
    "Turkey",
    "Beef",
]


def show_results(
    matches: list[dict[str, object]],
    preferred: list[dict[str, object]],
    source: str,
    loaded_count: int,
    preference_count: int,
    display_limit: int,
    max_prep: int,
    max_calories: int,
) -> None:
    """Render match counts and ranked results with an explicit source label."""
    shown = matches[:display_limit]
    metrics = st.columns(3)
    metrics[0].metric("Recipes loaded", loaded_count)
    metrics[1].metric("Match food + ingredients", preference_count)
    metrics[2].metric("Also meet time + calories", len(matches))
    st.caption(source)
    if not shown:
        if preferred:
            st.warning(
                "A recipe matches your food choice, but none fit both limits. "
                "Here is the closest excluded match."
            )
            closest = min(
                preferred,
                key=lambda recipe: (
                    max(int(recipe["prep_time_minutes"]) - max_prep, 0)
                    + max(int(recipe["calories"]) - max_calories, 0) / 50
                ),
            )
            prep_over = max(int(closest["prep_time_minutes"]) - max_prep, 0)
            calories_over = max(int(closest["calories"]) - max_calories, 0)
            reasons = []
            if prep_over:
                reasons.append(f"{prep_over} minutes over your time limit")
            if calories_over:
                reasons.append(f"{calories_over} calories over your calorie limit")
            st.info(
                f"**{closest['name']}** — {closest['prep_time_minutes']} minutes, "
                f"{closest['calories']} calories ({' and '.join(reasons)})."
            )
        else:
            st.warning(
                "No sample recipe matches that food and ingredient combination. "
                "Try Anything or remove an optional ingredient."
            )
        return
    top = shown[0]
    st.success(
        f"Top pick: {top['name']} — {top['prep_time_minutes']} minutes and "
        f"{top['calories']} calories."
    )
    st.subheader(f"Compare the matches (showing {len(shown)})")
    columns = [
        "recommendation_rank",
        "name",
        "cuisine",
        "difficulty",
        "prep_time_minutes",
        "cook_time_minutes",
        "total_time_minutes",
        "calories",
        "protein_grams",
        "servings",
        "instruction_count",
    ]
    st.dataframe(
        [{key: recipe.get(key) for key in columns} for recipe in shown],
        hide_index=True,
        use_container_width=True,
    )
    st.subheader("Recipe details")
    selected_name = st.selectbox(
        "Select a displayed recipe",
        [str(recipe["name"]) for recipe in shown],
        key=f"recipe-detail-{source}",
    )
    selected = next(recipe for recipe in shown if recipe["name"] == selected_name)
    details = st.columns(4)
    details[0].metric("Prep time", f"{selected['prep_time_minutes']} min")
    details[1].metric("Cook time", f"{selected['cook_time_minutes']} min")
    details[2].metric("Total time", f"{selected['total_time_minutes']} min")
    details[3].metric("Calories / serving", selected["calories"])
    nutrition = st.columns(4)
    nutrition[0].metric("Protein", f"{selected['protein_grams']:g} g")
    nutrition[1].metric("Servings", selected["servings"])
    nutrition[2].metric("Instruction steps", selected["instruction_count"])
    nutrition[3].metric(
        "Difficulty", str(selected.get("difficulty") or "Unknown").title()
    )
    tags = selected.get("dietary_tags") or []
    if tags:
        st.write(
            "**Dietary tags:** "
            + ", ".join(str(tag).replace("_", " ").title() for tag in tags)
        )
    ingredients = selected.get("ingredients") or []
    if ingredients:
        st.write("**Ingredients:** " + ", ".join(str(item) for item in ingredients))
    st.caption(f"Cuisine: {selected.get('cuisine') or 'Unknown'}")
    st.caption(
        f"Snapshot provenance: search '{selected.get('source_search') or 'unknown'}', "
        f"retrieved {selected.get('retrieved_at_utc') or 'unknown'} UTC."
    )
    instructions = selected.get("instructions") or []
    st.write("**Instructions from Recipe API**")
    if instructions:
        for number, step in enumerate(instructions, start=1):
            st.write(f"{number}. {step}")
    else:
        st.info("Step-by-step instructions were not provided by the data source.")


def render_app() -> None:
    """Render live and offline searches, ranked comparisons, and useful errors."""
    load_dotenv_file()
    configure_logging(
        os.getenv("LOG_LEVEL", "INFO"),
        os.getenv("LOG_FILE", "logs/weeknight-recipe-scout.log"),
    )
    st.set_page_config(
        page_title="Weeknight Recipe Scout", page_icon="🍲", layout="wide"
    )
    st.title("Weeknight Recipe Scout")
    st.write(
        "For busy cooks who want a realistic dinner: choose a food, set your time "
        "and calorie limits, then compare the best matches."
    )
    database_path = os.getenv(
        "RECIPE_HISTORY_DB", "data/weeknight-recipe-scout.sqlite3"
    )

    with st.sidebar:
        st.header("Your weeknight")
        default_search = os.getenv("RECIPE_SEARCH", "Chicken").title()
        search = st.selectbox(
            "What sounds good?",
            FOOD_CHOICES,
            index=FOOD_CHOICES.index(default_search)
            if default_search in FOOD_CHOICES
            else 0,
            help="Filters both live searches and the sample CSV.",
        )
        ingredients = st.text_input(
            "Ingredients you want included",
            value=os.getenv("RECIPE_INGREDIENTS", ""),
            help="Optional. Separate multiple ingredients with commas.",
        )
        dietary_tags = st.multiselect(
            "Dietary needs",
            [
                "dairy_free",
                "gluten_free",
                "halal",
                "kosher",
                "nut_free",
                "vegan",
                "vegetarian",
            ],
            format_func=lambda tag: tag.replace("_", " ").title(),
            help="A recipe must contain every selected provider dietary tag.",
        )
        max_prep = st.slider(
            "Maximum prep time",
            5,
            120,
            int(os.getenv("MAX_PREP_MINUTES", "30")),
            5,
            format="%d minutes",
        )
        max_calories = st.slider(
            "Maximum calories", 100, 1500, int(os.getenv("MAX_CALORIES", "650")), 50
        )
        result_limit = st.number_input(
            "Maximum results to display",
            min_value=1,
            max_value=50,
            value=int(os.getenv("RECIPE_PER_PAGE", "10")),
            help="Fewer results may appear when the data or limits produce fewer matches.",
        )
        api_key = st.text_input(
            "Recipe API key",
            value=os.getenv("RECIPE_API_KEY", ""),
            type="password",
            help="Only needed for live searches; it is not needed for the sample CSV.",
        )

    live_col, sample_col = st.columns(2)
    live_clicked = live_col.button("Search live Recipe API", type="primary")
    sample_clicked = sample_col.button(
        "Load saved API snapshot", use_container_width=True
    )

    if sample_clicked:
        try:
            recipes = load_processed_csv(SAMPLE_CSV)
            preferred = filter_recipe_preferences(recipes, search, ingredients)
            if dietary_tags:
                preferred = [
                    recipe
                    for recipe in preferred
                    if all(
                        tag in recipe.get("dietary_tags", []) for tag in dietary_tags
                    )
                ]
            matches = recommend_recipes(preferred, max_prep, max_calories)
            st.session_state["result_view"] = {
                "matches": matches,
                "preferred": preferred,
                "source": (
                    "Offline mode — 54-recipe snapshot retrieved from Recipe API "
                    "on August 13, 2026; no key or network request used now."
                ),
                "loaded_count": len(recipes),
                "preference_count": len(preferred),
                "display_limit": int(result_limit),
                "max_prep": max_prep,
                "max_calories": max_calories,
            }
        except (OSError, ValueError) as exc:
            st.error(f"Could not load sample data: {exc}")

    if live_clicked:
        try:
            live_search = "" if search == "Anything" else search
            summary, raw_path, processed_path = run(
                api_key,
                live_search,
                ingredients,
                1,
                int(result_limit),
                max_prep,
                max_calories,
            )
            record_run(Path(database_path), summary, processed_path)
            st.session_state["result_view"] = {
                "matches": summary["recommendations"],
                "preferred": summary["recipes"],
                "source": (
                    "Live mode — results fetched from Recipe API. "
                    f"Evidence: {raw_path}; processed results: {processed_path}."
                ),
                "loaded_count": summary["counts"]["recipes_returned"],
                "preference_count": summary["counts"]["recipes_returned"],
                "display_limit": int(result_limit),
                "max_prep": max_prep,
                "max_calories": max_calories,
            }
        except Exception as exc:  # noqa: BLE001
            st.error(
                f"Could not fetch recipes: {exc}. Check the API key and internet "
                "connection, then try again."
            )

    if "result_view" in st.session_state:
        show_results(**st.session_state["result_view"])

    recent = list_recent_runs(Path(database_path), limit=5)
    if recent:
        st.subheader("Recent recommendation history")
        st.dataframe(recent, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    render_app()
