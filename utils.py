from pathlib import Path
from call_api import get_data
from movie_class import (
    Movie,
    create_movie_instances,
    query_movie_by_title,
)
import os

headers = {
    "X-RapidAPI-Key": os.environ['X-RapidAPI-Key'],
    "X-RapidAPI-Host": os.environ['X-RapidAPI-Host']
}


DATABASE_NAME = Path("./database/movies_database.db")
COLUMNS = 7
K = COLUMNS * 2



# Function to get a movie instance by querying the database or API
def get_movie_instance(movie_name):
    movie_instance = query_movie_by_title(movie_name, database_name=DATABASE_NAME)

    if movie_instance:
        movie_instance = (
            movie_instance if isinstance(movie_instance, Movie) else movie_instance[0]
        )
    else:
        movie_response = get_data(movie_name, headers=headers)
        if movie_response["error_code"] != 200:
            return "error"

        movies_data = create_movie_instances(movie_response["description"])
        movie_instance = movies_data[0]
    return movie_instance
