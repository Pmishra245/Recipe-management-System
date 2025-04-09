import streamlit as st
from auth import authenticate_user, add_user
from recipes import add_recipe, edit_recipe, delete_recipe, rate_recipe, get_all_recipes, get_user_recipes, get_recipe_reviews
from icon.icon import icon_base64

st.set_page_config(page_title="Recipes DBMS", page_icon=icon_base64, layout="wide")
st.title("Recipe Manager")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    auth_choice = st.sidebar.radio("Login/Signup", ["Login", "Signup"])
    
    if auth_choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    
    elif auth_choice == "Signup":
        st.subheader("Signup")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        if st.button("Signup"):
            if add_user(new_username, new_password):
                st.success("Signup Successful! Please login.")
            else:
                st.error("Username already exists. Try another.")
else:
    username = st.session_state.username
    menu = ["View Recipes", "Search Recipes", "Add Recipe", "Manage My Recipes", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "View Recipes":
        st.subheader("📖 All Recipes")
        recipes = get_all_recipes()
        
        for recipe in recipes:
            st.markdown("---")
            st.markdown(f"## {recipe['name']}")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**🌍 Cuisine:** `{recipe['cuisine']}`")
                st.write(f"**⏳ Cook Time:** `{recipe['cook_time']} mins`")
                st.write(f"**👤 Added By:** `{recipe['added_by']}`")
                st.write(f"**⭐ Average Rating:** `{recipe['average_rating']:.1f}/10`")
                st.write(f"**🛒 Ingredients:**")
                st.markdown("\n".join([f"- {ing}" for ing in recipe["ingredients"]]))
                st.write(f"**📜 Instructions:** {recipe['instructions']}")
            
            with col2:
                # User rating section
                if username not in recipe["ratings"]:
                    st.write("### ⭐ Rate this Recipe")
                    rating = st.slider(f"Rate {recipe['name']}", 1, 10, key=f"rate_{recipe['name']}")
                    feedback = st.text_area(f"Your Feedback (Optional)", key=f"feedback_{recipe['name']}")
                    if st.button(f"Submit Rating for {recipe['name']}", key=f"submit_{recipe['name']}"):
                        if rate_recipe(username, recipe['name'], rating, feedback):
                            st.success("✅ Rating and feedback submitted successfully!")
                            st.rerun()
                        else:
                            st.error("⚠️ You have already rated this recipe.")

                # Scrollable Reviews Section
                st.markdown("### 💬 User Reviews & Ratings")
                reviews = get_recipe_reviews(recipe['name'])
                
                if reviews:
                    sorted_reviews = sorted(reviews, key=lambda r: r["rating"], reverse=True)
                    
                    # Scrollable review box
                    st.markdown("""
                        <div style="max-height: 250px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
                    """, unsafe_allow_html=True)

                    for review in sorted_reviews:
                        st.markdown(f"**⭐ {review['rating']}/10** — {review['user']}", unsafe_allow_html=True)
                        if review["feedback"]:
                            st.markdown(f"""
                            <div style="background-color: #ffffff; padding: 8px; border-radius: 6px; margin-top: 5px;">
                                <i>💬 {review['feedback']}</i>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown("<hr>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)  # Closing the scrollable div
                    
                else:
                    st.info("🚫 No reviews yet. Be the first to review!")

    elif choice == "Search Recipes":
        st.markdown("### 🔍 Search Recipes")  # Adjusted heading size
        search_type = st.radio("Search by:", ["Ingredients", "Cuisine", "Cooking Time"])

        search_results = []

        if search_type == "Ingredients":
            ingredients = st.text_input("Enter ingredients (comma-separated)").strip()
            if st.button("Search"):
                recipes = get_all_recipes()
                search_results = [
                    recipe for recipe in recipes
                    if any(ing.lower() in [i.lower() for i in recipe["ingredients"]] for ing in ingredients.lower().split(", "))
                ]

        elif search_type == "Cuisine":
            cuisine = st.text_input("Enter cuisine type").strip()
            if st.button("Search"):
                recipes = get_all_recipes()
                search_results = [recipe for recipe in recipes if recipe["cuisine"].lower() == cuisine.lower()]

        elif search_type == "Cooking Time":
            max_time = st.number_input("Enter maximum cooking time (in mins)", min_value=1)
            if st.button("Search"):
                recipes = get_all_recipes()
                search_results = [recipe for recipe in recipes if recipe["cook_time"] <= max_time]

        if search_results:
            search_results.sort(key=lambda x: x["average_rating"], reverse=True)  # Sort by rating
            for recipe in search_results:
                st.markdown(f"## 🍽️ {recipe['name']}")
                
                col1, col2 = st.columns([2, 1])  # Layout for better visibility
                
                with col1:
                    st.write(f"**🌍 Cuisine:** {recipe['cuisine']}")
                    st.write(f"**⏳ Cook Time:** {recipe['cook_time']} mins")
                    st.write(f"**👤 Added By:** {recipe['added_by']}")
                    st.write(f"**⭐ Average Rating:** {recipe['average_rating']:.1f}/10")
                    st.write(f"**📝 Ingredients:** {', '.join(recipe['ingredients'])}")
                    st.write(f"**📖 Instructions:** {recipe['instructions']}")

                with col2:
                    st.markdown("#### 🏆 Top Reviews")
                    reviews = get_recipe_reviews(recipe['name'])
                    if reviews:
                        sorted_reviews = sorted(reviews, key=lambda r: r["rating"], reverse=True)
                        for review in sorted_reviews[:3]:  # Show top 3 reviews
                            st.markdown(f"**⭐ {review['rating']}/10** — {review['user']}")
                            if review["feedback"]:
                                st.markdown(f"""
                                <div style="background-color: #f8f9fa; padding: 8px; border-radius: 6px; margin-top: 5px;">
                                    <i>💬 {review['feedback']}</i>
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown("---")
                    else:
                        st.info("🚫 No reviews yet.")

                st.markdown("---")  # Divider for clarity
        else:
            st.warning("⚠️ No recipes found. Try refining your search!")

    elif choice == "Add Recipe":
        st.subheader("Add a New Recipe")
        with st.form("recipe_form"):
            name = st.text_input("Recipe Name")
            ingredients = st.text_area("Ingredients (comma-separated)")
            cuisine = st.text_input("Cuisine Type")
            cook_time = st.number_input("Cooking Time (minutes)", min_value=1)
            instructions = st.text_area("Instructions")
            submit = st.form_submit_button("Add Recipe")
        
        if submit and add_recipe(username, name, ingredients.split(", "), cuisine, cook_time, instructions):
            st.success(f"Recipe '{name}' added successfully!")

    elif choice == "Manage My Recipes":
        st.subheader("📌 Your Recipes")
        user_recipes = get_user_recipes(username)

        if not user_recipes:
            st.warning("⚠️ You haven't added any recipes yet.")
        else:
            for recipe in user_recipes:
                recipe_key = f"edit_mode_{recipe['name']}"  # Unique key for each recipe

                # Initialize edit mode in session state if not exists
                if recipe_key not in st.session_state:
                    st.session_state[recipe_key] = False

                st.markdown("---")
                
                if not st.session_state[recipe_key]:  # Normal view
                    st.markdown(f"## {recipe['name']}")

                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**🌍 Cuisine:** `{recipe['cuisine']}`")
                        st.write(f"**⏳ Cook Time:** `{recipe['cook_time']} mins`")
                        st.write(f"**🛒 Ingredients:** {', '.join(recipe['ingredients'])}")
                        st.write(f"**📜 Instructions:** {recipe['instructions']}")

                    with col2:
                        if st.button(f"✏️ Edit", key=f"edit_btn_{recipe['name']}"):
                            st.session_state[recipe_key] = True
                            st.rerun()

                        if st.button(f"🗑️ Delete", key=f"delete_{recipe['name']}"):
                            if delete_recipe(username, recipe["name"]):
                                st.success("🗑️ Recipe deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete recipe. Please try again.")

                else:  # Edit mode
                    with st.form(key=f"edit_form_{recipe['name']}"):
                        st.subheader(f"✏️ Editing {recipe['name']}")
                        
                        new_name = st.text_input("Recipe Name", recipe["name"])
                        new_ingredients = st.text_area(
                            "Ingredients (comma-separated)",
                            ", ".join(recipe["ingredients"])
                        )
                        new_cuisine = st.text_input("Cuisine", recipe["cuisine"])
                        new_cook_time = st.number_input(
                            "Cooking Time (mins)", min_value=1, value=recipe["cook_time"]
                        )
                        new_instructions = st.text_area("Instructions", recipe["instructions"])
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            submit_edit = st.form_submit_button("✅ Save Changes")
                        with col2:
                            cancel_edit = st.form_submit_button("❌ Cancel")

                        if submit_edit:
                            updated_data = {
                                "name": new_name.strip(),
                                "ingredients": [ing.strip() for ing in new_ingredients.split(",") if ing.strip()],
                                "cuisine": new_cuisine.strip(),
                                "cook_time": new_cook_time,
                                "instructions": new_instructions.strip(),
                            }

                            if edit_recipe(username, recipe["name"], updated_data):
                                st.success("🎉 Recipe updated successfully!")
                                st.session_state[recipe_key] = False
                                st.rerun()
                            else:
                                st.error("❌ Failed to update recipe. Please try again.")

                        if cancel_edit:
                            st.session_state[recipe_key] = False
                            st.rerun()

                st.markdown("---")

    elif choice == "Logout":
        st.session_state.authenticated = False
        st.rerun()
