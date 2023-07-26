import streamlit as st
import polars as pl
import pickle, os
from pathlib import Path
from datetime import date
from st_keyup import st_keyup
import webbrowser
from helper import find_similar_movies
from movie_class import store_movies
from utils import get_movie_instance
from scipy import sparse
from scipy.sparse import _csr

st.set_page_config(layout="wide", page_title="Movie recommender App")

DATABASE_NAME = Path("./database/movies_database.db")
COLUMNS = 7
K = COLUMNS * 2


# caching important data
@st.cache_data
def load_data():
    return pl.read_csv(Path("./dataset/movies_clean_final.csv"))


# @st.cache_data
def load_vector():
    # Load pickel as vector
    with open("vector.pkl", "rb") as f:
        return pickle.load(f)


@st.cache_data
def load_movie_info():
    # Load pickel as vector2
    with open("movie_info.pkl", "rb") as f:
        return pickle.load(f)


# Function to show latest movies
def show_latest_movies(movie_df, k=10):
    return (
        movie_df.filter(pl.col("year") <= date.today().year)
        .sort("year", descending=True)
        .head(k)["title"]
        .to_list()
    )


# Function to get popular movies
def show_popular_movies(movie_df, year=None, k=10):
    if year is None:
        x = movie_df.sort(["votes", "rating"], descending=True)["title"].to_list()
    else:
        x = movie_df.filter(pl.col("year") == year)
        x = x.sort(["votes", "rating"], descending=True)["title"].to_list()

    return x[:k]


# Function to get movie recommendations and display them
def movies_show(list_of_movies, K, COLUMNS):
    # Process and display movie recommendations
    movies_entries = []
    cols = st.columns(COLUMNS)
    plot = 1
    for num, recommended_movie_name in enumerate(list_of_movies):
        if plot == K + 1:
            break

        movie_instance = get_movie_instance(recommended_movie_name)

        if movie_instance:
            if movie_instance.img_poster:
                with cols[(plot - 1) % COLUMNS]:
                    st.write(
                        movie_poster_iframe(
                            movie_instance.title,
                            movie_instance.year,
                            movie_instance.img_poster,
                        ),
                        unsafe_allow_html=True,
                    )
                    plot += 1

            movies_entries.append(movie_instance)

    # Store the movie entries in the database
    store_movies(movies_entries, database_name=DATABASE_NAME)
    
    
# Function to get movie recommendations and display them
def get_movie_recommendations(user_movie, movie_df, vector, K, COLUMNS):
    # Find similar movie names
    recommended_movie_names = find_similar_movies(
        user_movie, movie_df, vector=vector, k=3 * K
    )

    movies_show(recommended_movie_names, K, COLUMNS)






def movie_poster_iframe(
    movie_name, movie_year, poster_url, movie_page_url="url unavailable"
):
    return f"""
    <div style="position: relative; width: 200px; height: 300px;">
        <a href="{movie_page_url}" target="_blank">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.3));"></div>
            <img src="{poster_url}" alt="{movie_name}" style="width: 100%; height: 100%;">
            <p style="position: absolute; bottom: 5px; left: 5px; color: white; font-weight: bold; padding: 5px;">{movie_name} ({movie_year})</p>
        </a>
    </div>
    """


# create a movie recommendation app using streamlit
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden; }
    </style>
    """


def main():
    st.title("Movie Recommendation")




    st.markdown(hide_menu_style, unsafe_allow_html=True)

    # sidebar
    if st.sidebar.button("Code/Github"):
        webbrowser.open("https://github.com/tikendraw/movie-recommender-system")

    st.sidebar.success("Star the Repo for Moral Support")

    st.sidebar.write("Connect with Tikendra")
    if st.sidebar.button("LinkedIn"):
        webbrowser.open("www.linkedin.com/in/tikendraw")

    if st.sidebar.button("Github"):
        webbrowser.open("https://github.com/tikendraw")

    st.sidebar.info(
        """
                The system determines movie similarity primarily through the analysis of movie synopsis or plot summaries. 
                
                While this approach allows us to identify movies with similar themes, plots, or storylines, it might occasionally lead to 
                recommendations for lesser-known or niche films. 
                
                Such movies may not have garnered significant popularity or exposure among the general audience.
                """
    )

    # read csv in dataset folder as movie_df using polar
    movie_df = load_data()
    movies_list = pl.Series(movie_df["title"].to_list())
    st.write("Movies:", len(movies_list))

    # input
    st.write(
        f"We have {len(movies_list)} Movies, try to type the Name and shortlist in the box below "
    )
    if keywords := st_keyup(" "):
        filtered = movie_df.filter(
            movie_df["title"].str.to_lowercase().str.contains(keywords.lower())
        )["title"].to_list()
    else:
        filtered = movies_list

    user_movie = st.selectbox(
        "Select your movie, (Shortlist above, then select below)", filtered
    )

    find = st.button("Recommend")

    vector = load_vector()
    movies_info = load_movie_info()

    latest_mov = show_latest_movies(movie_df=movie_df, k=K)
    popular_mov = show_popular_movies(movie_df=movie_df, k=K)
    popular_mov_this_year = show_popular_movies(
        movie_df=movie_df, year=date.today().year, k=K
    )

    # st.write(latest_mov)

    if find:
        st.write(f"you chose : '{user_movie}'")

        with st.spinner(
            "Finding Movies for you...(Close you eyes and count to 10 slowly.🫣)"
        ):
            get_movie_recommendations(user_movie, movie_df, vector, K, COLUMNS)

    st.header(f"Latest Movies({date.today().year})")
    movies_show(latest_mov, K, COLUMNS)

    st.header(f"Popular Movies({date.today().year})")
    movies_show(popular_mov_this_year, K, COLUMNS)

    st.header("All time Popular Movies")
    movies_show(popular_mov, K, COLUMNS)


if __name__ == "__main__":
    main()
