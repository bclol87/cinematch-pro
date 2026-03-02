import streamlit as st
from recommender import load_data, train_model, make_stars, get_recommendations

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CineMatch Pro", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    /* Main app background - keeping it slightly off-white for contrast */
    .stApp { background-color: #f8f9fa; }

    /* Target the Metric Containers */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }

    /* Force the Big Number to be BLACK */
    [data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }

    /* Force the Label (e.g., "Movies Found") to be Dark Gray/Blue */
    [data-testid="stMetricLabel"] > div > p {
        color: #555555 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    /* Adjust the Search Bar and Button colors for the light theme */
    .stTextInput input {
        color: #000000 !important;
    }
    
    /* Movie card styling for light mode */
    .stAlert {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE DATA & AI ---
movies = load_data()
cosine_sim = train_model(movies)

if movies.empty:
    st.error("Dataset not found. Please ensure 'movies_lite.csv' is in your GitHub folder.")
    st.stop()

# UI Helpers
all_genres = sorted(list(set(movies['genres'].str.split(', ').explode().dropna())))
if '' in all_genres: all_genres.remove('')

min_year_data = int(movies['year'].min())
max_year_data = int(movies['year'].max())

# --- SEARCH BAR AREA ---
st.markdown("### 🔍 Search Engine")

# 1. Add the toggle switch
search_type = st.radio("What are you looking for?", ["Movie Title", "Actor Name"], horizontal=True, label_visibility="collapsed")

# 2. Change the placeholder text dynamically based on what they picked
with st.container():
    col1, col2 = st.columns([4, 1])
    
    if search_type == "Actor Name":
        hint = "Type an Actor (e.g., Robert Downey Jr, Tom Holland)..."
    else:
        hint = "Type a Movie Title (e.g., Inception, Spirited Away)..."
        
    search_query = col1.text_input("Search Input", placeholder=hint, label_visibility="collapsed")
    search_btn = col2.button("Find Movies", use_container_width=True, type="primary")

# --- RESULTS TABS ---
tab1, tab2 = st.tabs(["🍿 Recommendations", "📊 Genre Insights"])

# --- EXECUTE LOGIC ---
# Notice we added `search_type` as the second argument here!
if search_btn or search_query or not search_query: 
    results, genre_counts = get_recommendations(
        search_query, search_type, min_rating, selected_genres, 
        year_range[0], year_range[1], movies, cosine_sim
    )

# --- MAIN HERO SECTION ---
st.title("🎬 CineMatch Pro")
st.subheader("Discover your next favorite movie in seconds.")

# --- SEARCH BAR AREA ---
with st.container():
    col1, col2 = st.columns([4, 1])
    search_query = col1.text_input("Search Engine", placeholder="Type an Actor (e.g. Robert Downey Jr) or Movie Title...", label_visibility="collapsed")
    search_btn = col2.button("🔍 Find Movies", use_container_width=True, type="primary")

# --- RESULTS TABS ---
tab1, tab2 = st.tabs(["🍿 Recommendations", "📊 Genre Insights"])

# --- EXECUTE LOGIC ---
if search_btn or search_query or not search_query: 
    results, genre_counts = get_recommendations(
        search_query, min_rating, selected_genres, 
        year_range[0], year_range[1], movies, cosine_sim
    )

    with tab1:
        if results.empty:
            st.warning("No matches found. Try lowering the rating or broadening the year range.")
        else:
            # Stats Summary
            m1, m2, m3 = st.columns(3)
            m1.metric("Movies Found", len(results))
            m2.metric("Avg Rating", f"{results['vote_average'].mean():.1f} / 10")
            m3.metric("Year Range", f"{results['year'].min()} - {results['year'].max()}")

            st.markdown("---")

            # Movie Cards
            for _, row in results.iterrows():
                with st.container():
                    c1, c2 = st.columns([1, 5])
                    with c1:
                        st.markdown(f"### {row['year']}")
                        st.markdown(make_stars(row['vote_average']))
                        st.info(row['Why Shown?'])
                    with c2:
                        st.subheader(row['title'])
                        st.markdown(f"**🏷️ Genres:** *{row['genres']}*")
                        st.write(row['overview'])
                        st.link_button(f"🎬 View on TMDB", f"https://www.themoviedb.org/movie/{row['id']}")
                    st.divider()

    with tab2:
        if not results.empty and len(genre_counts) > 0:
            st.markdown("### Which genres dominate your search?")
            st.bar_chart(genre_counts, color="#00d4ff")
            
            st.markdown("#### Detailed Stats")
            st.table(genre_counts)
        else:
            st.write("Perform a search to see genre analytics.")
