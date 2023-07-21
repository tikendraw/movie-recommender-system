import streamlit as st
import polars as pl
import numpy as np
import pickle
import os
from pathlib import Path
from helper import find_similar_movies 
import json
from call_api import get_data
from datetime import datetime
import concurrent.futures as cf
from movie_class import Movie, create_movie_instances, query_movie_by_title, store_movies
from st_keyup import st_keyup

DATABASE_NAME = Path('./database/movies_database.db')
# create a movie recommendation app using streamlit
st.set_page_config(layout="wide")

st.title('Movie Recommendation')



# read csv in dataset folder as movie_df using polar
@st.cache_data  
def load_data():
    return pl.read_csv(Path('./dataset/movies_clean_final.csv'))

@st.cache_data  
def load_vector():
    # Load pickel as vector
    with open('vector.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_data  
def load_movie_info():
    # Load pickel as vector
    with open('movie_info.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_data  
def load_secret():
    # read a json file
    with open('secret.json', 'r') as f:
        return json.load(f)


movie_df = load_data()
movies_list = pl.Series(movie_df['title'].to_list())
st.write("Movies:",len(movies_list))

#input




st.write('We have alot of similar movie title, try to type the Name and shortlist in the box below ')
user_movie = st_keyup("Enter city name")

if user_movie:
    filtered =  movie_df.filter(
        movie_df['title'].str.to_lowercase().str.contains(user_movie.lower()))['title'].to_list()
else:
    filtered = movies_list
    
# if user_movie:
#     st.write(filtered)

user_movie = st.selectbox(
    'Select your movie',
    filtered)

find = st.button('Search')

vector = load_vector()
movies_info = load_movie_info()
data = load_secret()

headers = data['headers']


COLUMNS = 5
K = 10

if find:
    st.write(f'you chose {user_movie}')
    

    # Find similar movie names
    recommended_movie_names = find_similar_movies(user_movie, movie_df, vector=vector, k=2*K)

    movies_entries = []
    cols = st.columns(COLUMNS)
    plot = 1
    for num, recommended_movie_name in enumerate(recommended_movie_names):
        if plot == K+1:
            break
        # Check if the movie exists in the database
        movie_instance = query_movie_by_title(recommended_movie_name, database_name=DATABASE_NAME)

        if movie_instance:
            # If the movie exists in the database, use it as a Movie instance
            movie_selected = movie_instance if isinstance(movie_instance, Movie) else movie_instance[0]
        else:
            # If the movie doesn't exist in the database, get data from the API
            movie_response = get_data(recommended_movie_name, headers=headers)
            if movie_response['ok']:
                movies_data = create_movie_instances(movie_response['description'])
                movie_selected = movies_data[0]  # pick the first one only

                movies_entries.extend(movies_data)
            else:
                st.write(f'Error code : {movie_response["error_code"]} for {recommended_movie_name}')

        if movie_selected.img_poster:
            with cols[(plot - 1) % COLUMNS]:
                st.write(f'{movie_selected.title} ({movie_selected.year})')
                st.image(movie_selected.img_poster)
                plot += 1
        else:
            continue
                # st.write('Image Unavailable')

    
    # Store the movie entry in the database
    store_movies(movies_entries, database_name=DATABASE_NAME)

    st.write('Movie instances: ', len(movies_entries))

 
