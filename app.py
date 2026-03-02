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
    /* Main app background */
    .stApp { background-color: #0e1117; }

    /* Target the Metric Containers */
    [data-testid="stMetric"] {
        background-color: #1e2130 !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 1px solid #3e425b !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Force the Big Number to be White */
    [data-testid="stMetricValue"] > div {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* Force the Label (e.g., "Movies Found") to be Light Gray */
    [data-testid="stMetricLabel"] > div > p {
        color: #00d4ff !important; /* Bright blue for labels */
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    /* Styling for movie cards below */
    .stAlert {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #ffffff !important;
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

# --- SIDEBAR (Filters) ---
with st.sidebar:
    st.image("https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.svg", width=50)
    st.header("⚙️ Preferences")
    
    st.markdown("---")
    min_rating = st.select_slider("Minimum Rating Score", options=[i/2 for i in range(21)], value=5.0)
    year_range = st.slider("Release Period", min_year_data, max_year_data, (2000, max_year_data))
    selected_genres = st.multiselect("Filter by Genres", all_genres, placeholder="Choose genres...")
    
    st.markdown("---")
    st.caption("AI-Powered by TF-IDF Content Similarity")

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
