
import polars as pl
import re
from typing import List
from sklearn.metrics.pairwise import cosine_similarity
import string
import csv
import concurrent.futures

def remove_newline_chars(text):
    """Removes `\n` characters from a text string."""
    text_str = re.sub(r"\n", "", text)
    text_str = text_str.strip()
    return text_str

def remove_punctuations(text):
    # text = str(text).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.strip()
    return text

def join_names(text):
    # text = str(text).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.replace(' ','')
    text = text.strip()
    return text

def flatten_nested_list(nested_list):
    return [item for sublist in nested_list for item in (flatten_nested_list(sublist) if isinstance(sublist, list) else [sublist])]


def clean_year(x):
    x = remove_punctuations(x)
    x = re.sub(r'[^0-9]', '', x)
    if x == '':
        x = 0
    return int(x)

def clean_genre(x):
    x = str(x)
    x = [remove_newline_chars(i) for i in x.split()]
    x = ' '.join(x)
    return x.strip()


def concatenate_names(sentence):
    nlp = spacy.load("en_core_web_lg")
    ner_dict = {}

    # Extract names from the sentence using NER
    doc = nlp(sentence)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            new_name = name.replace(' ','')
            ner_dict[name] = new_name

    # Replace names with names without spaces in the sentence
    for i, j in ner_dict.items():
        sentence = sentence.replace(i,j)

    return sentence


def find_similar_movies(x:str, dff, vector, k = 5) -> List[str]:
    movie_id  = dff.filter(pl.col('title') == x)['movies_id'].to_list()[0]
    # print(movie_id)
    sim_vec  = cosine_similarity(vector, vector[movie_id])
    y = sorted(enumerate(sim_vec), key=lambda x: x[1], reverse=True)
    recommended_movies_ids = [i[0] for i in y[1:k+1]]
    return [
        dff.filter(pl.col('movies_id') == i)['title'].to_list()[0]
        for i in recommended_movies_ids
    ]

    



# Function to save movie entry in CSV file
def save_movie_entry_to_csv(movie_entry, csv_file):
    # Define the CSV fieldnames (column names)
    fieldnames = [
        "#TITLE",
        "#YEAR",
        "#IMDB_ID",
        "#RANK",
        "#ACTORS",
        "#AKA",
        "#IMDB_URL",
        "#IMDB_IV",
        "#IMG_POSTER",
        "photo_width",
        "photo_height",
    ]

    # Check if the CSV file exists, if not, create a new one and write header
    file_exists = False
    try:
        with open(csv_file, "r", newline="") as csvfile:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(csv_file, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        # Fill missing details with "unavailable"
        for field in fieldnames:
            if field not in movie_entry:
                movie_entry[field] = "unavailable"

        # Write the movie entry data to CSV
        writer.writerow(movie_entry)

# Function to save movie entries in CSV file using ThreadPoolExecutor
def save_movie_entries_to_csv_parallel(json_data, csv_file):
    if not json_data.get("ok", False):
        print("Error: 'ok' is not True in the JSON response.")
        return

    movie_entries = json_data.get("description", [])
    if not movie_entries:
        print("Error: No movie entries found in the JSON response.")
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(save_movie_entry_to_csv, entry, csv_file) for entry in movie_entries]
        
        # Wait for all futures to complete
        concurrent.futures.wait(futures)



