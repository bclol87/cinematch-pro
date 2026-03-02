import streamlit as st
# Import your backend logic from your other file
from recommender import load_data, train_model, make_stars, get_recommendations

# --- PAGE CONFIG ---
st.set_page_config(page_title="CineMatch Pro", page_icon="🎬", layout="wide")

# --- INITIALIZE DATA & AI ---
movies = load_data()
cosine_sim = train_model(movies)

if movies.empty:
    st.stop() # Stop running if the CSV is missing

# Helper variables for UI dropdowns and sliders
all_genres = sorted(list(set(movies['genres'].str.split(', ').explode().dropna())))
if '' in all_genres: all_genres.remove('')

min_year_data = int(movies['year'].min())
max_year_data = int(movies['year'].max())

# --- SIDEBAR (Filters) ---
with st.sidebar:
    st.header("⚙️ Filters")
    min_rating = st.slider("Min Rating", 0.0, 10.0, 5.0, 0.5)
    year_range = st.slider("Year Range", min_year_data, max_year_data, (1980, max_year_data))
    selected_genres = st.multiselect("Genre", all_genres)

# --- MAIN SCREEN ---
st.title("🎬 CineMatch Pro")
st.markdown("Search by **Movie Title** or **Actor Name**.")

col1, col2 = st.columns([4, 1])
search_query = col1.text_input("Search", placeholder="Type 'Robert Downey Jr' or 'Inception'...", label_visibility="collapsed")
search_btn = col2.button("🔍 Search", use_container_width=True, type="primary")

# --- EXECUTE LOGIC & DISPLAY ---
# Run the search when the button is clicked, or just show top movies by default
if search_btn or search_query or not search_query: 
    results, genre_counts = get_recommendations(
        search_query, min_rating, selected_genres, 
        year_range[0], year_range[1], movies, cosine_sim
    )

    if results.empty:
        st.warning("No movies found. Try adjusting your filters or search terms.")
    else:
        # 1. Show Visual Analytics
        if len(genre_counts) > 0:
            st.markdown("### 📊 Genre Breakdown in Results")
            st.bar_chart(genre_counts)

        # 2. Show Movie Cards
        st.markdown("### 🍿 Results")
        for _, row in results.iterrows():
            with st.container():
                c1, c2 = st.columns([1, 4])
                with c1:
                    st.markdown(f"**{row['year']}**")
                    st.markdown(make_stars(row['vote_average']))
                    st.caption(row['Why Shown?'])
                with c2:
                    st.subheader(row['title'])
                    st.caption(row['genres'])
                    st.write(row['overview'][:200] + "...")
                    st.link_button("🎬 Watch Intro / Info", f"https://www.themoviedb.org/movie/{row['id']}")
                st.divider()
