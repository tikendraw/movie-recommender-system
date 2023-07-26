import json
import requests
import os

headers = {
    "X-RapidAPI-Key": os.environ['X-RapidAPI-Key'],
    "X-RapidAPI-Host": os.environ['X-RapidAPI-Host']
}

urls = [
    "https://imdb-search2.p.rapidapi.com/superman2",
    "https://imdb-search2.p.rapidapi.com/spiderman2",
    "https://imdb-search2.p.rapidapi.com/300",
]


def make_url(name: str):
    x = name.lower()
    x = name.strip()
    x = x.replace(" ", "%20")
    return f"https://imdb-search2.p.rapidapi.com/{x}"


def get_data(name: str, headers: dict = headers) -> json:
    url = make_url(name)
    response = requests.get(url, headers=headers)
    return response.json()
