import streamlit as st
import requests

# ------------------------------
# Page Settings
# ------------------------------
st.set_page_config(page_title="Smart Meal Recommender", page_icon="🍽️", layout="wide")

st.title("🍽️ Smart Meal Recommender")
st.write("Enter your mood, time, and ingredients to get personalized menu recommendations.")


# ------------------------------
# API KEY
# ------------------------------
API_KEY = st.secrets["SPOONACULAR_API_KEY"]


# ------------------------------
# Recommendation Rules (Mood → Flavor)
# ------------------------------
def mood_to_flavor(mood):
    return {
        "Happy": "sweet",
        "Tired": "comfort",
        "Stressed": "spicy",
        "Lazy": "easy",
        "Neutral": "simple"
    }.get(mood, "simple")


# ------------------------------
# Spoonacular: Complex Search
# ------------------------------
def get_recipes(keyword, max_time, cuisine, number=5):
    url = f"https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": API_KEY,
        "query": keyword,
        "cuisine": cuisine if cuisine != "Any" else None,
        "maxReadyTime": max_time,
        "number": number,
        "addRecipeInformation": True
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])


# ------------------------------
# Spoonacular: Get Full Recipe Info
# ------------------------------
def get_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": API_KEY}
    response = requests.get(url, params=params)
    return response.json()


# ------------------------------
# SIDEBAR: User Input
# ------------------------------
st.sidebar.header("Your Preferences")

mood = st.sidebar.selectbox("Your Mood", ["Happy", "Tired", "Stressed", "Lazy", "Neutral"])
max_time = st.sidebar.slider("Max Cooking Time (minutes)", 10, 120, 30)
cuisine = st.sidebar.selectbox("Preferred Cuisine", ["Any", "Korean", "Japanese", "Chinese", "Italian", "American"])

query = st.sidebar.text_input("Optional Keyword (e.g., chicken, pasta, tofu)")
search_button = st.sidebar.button("Find Recipes")


# ------------------------------
# MAIN LOGIC
# ------------------------------
if search_button:
    st.subheader("🔍 Recommended Menus Based on Your Input")

    flavor_keyword = mood_to_flavor(mood)

    # Priority of search keywords:
    # 1) user keyword
    # 2) mood-based flavor keyword
    search_word = query if query else flavor_keyword

    with st.spinner("Searching recipes..."):
        recipes = get_recipes(search_word, max_time, cuisine)

    if not recipes:
        st.warning("No recipes found. Try different keywords or increase max time.")
    else:
        for recipe in recipes:
            st.markdown("---")
            cols = st.columns([1.2, 2])

            # Image
            with cols[0]:
                st.image(recipe["image"], width=240)

            # Info
            with cols[1]:
                st.subheader(recipe["title"])
                st.write(f"⏱ **Ready in:** {recipe['readyInMinutes']} min")
                st.write(f"🍽 **Servings:** {recipe['servings']}")

                # Expand to show details
                with st.expander("📋 Ingredients & Instructions"):
                    details = get_recipe_details(recipe["id"])

                    st.markdown("### Ingredients")
                    for ing in details.get("extendedIngredients", []):
                        st.write("- " + ing["original"])

                    st.markdown("### Instructions")
                    steps = details.get("analyzedInstructions", [])
                    if steps:
                        for step in steps[0]["steps"]:
                            st.write(f"{step['number']}. {step['step']}")
                    else:
                        st.write("No detailed instructions available.")
