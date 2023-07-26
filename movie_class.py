from dataclasses import dataclass
import sqlite3
from typing import List, Optional


@dataclass
class Movie:
    title: str
    year: int
    imdb_id: str
    rank: int
    actors: Optional[str] = None
    aka: Optional[str] = None
    imdb_url: Optional[str] = None
    imdb_iv: Optional[str] = None
    img_poster: Optional[str] = None
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None


# Function to create movie instances from the provided JSON data
def create_movie_instances(data: List) -> List:
    # sourcery skip: inline-immediately-returned-variable, list-comprehension
    movie_instances = [
        Movie(
            title=movie_data.get("#TITLE"),
            year=movie_data.get("#YEAR"),
            imdb_id=movie_data.get("#IMDB_ID"),
            rank=movie_data.get("#RANK"),
            actors=movie_data.get("#ACTORS"),
            aka=movie_data.get("#AKA"),
            imdb_url=movie_data.get("#IMDB_URL"),
            imdb_iv=movie_data.get("#IMDB_IV"),
            img_poster=movie_data.get("#IMG_POSTER"),
            photo_width=movie_data.get("photo_width"),
            photo_height=movie_data.get("photo_height"),
        )
        for movie_data in data
    ]
    return movie_instances


# Function to store movie data in the SQLite database using concurrent.futures
def store_movies(movie_instances: list, database_name: str):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    # Create the table if it does not exist
    c.execute(
        """CREATE TABLE IF NOT EXISTS movies (
                title TEXT,
                year INTEGER,
                imdb_id TEXT UNIQUE,
                rank INTEGER,
                actors TEXT,
                aka TEXT,
                imdb_url TEXT,
                imdb_iv TEXT,
                img_poster TEXT,
                photo_width INTEGER,
                photo_height INTEGER
                )"""
    )

    # Insert movie data into the table
    for movie in movie_instances:
        c.execute(
            "INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                movie.title,
                movie.year,
                movie.imdb_id,
                movie.rank,
                movie.actors,
                movie.aka,
                movie.imdb_url,
                movie.imdb_iv,
                movie.img_poster,
                movie.photo_width,
                movie.photo_height,
            ),
        )

    # Commit changes and close the connection
    conn.commit()
    conn.close()


# Function to query the database for a movie by its title
def query_movie_by_title(title, database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    c.execute("SELECT * FROM movies WHERE title LIKE ?", (f"%{title}%",))
    result = c.fetchone()

    # Close the connection
    conn.close()

    return Movie(*result) if result else None
