import sqlite3

import pandas as pd
import requests


FEATURE_COLUMNS = [
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "key",
    "liveness",
    "loudness",
    "mode",
    "speechiness",
    "tempo",
    "valence",
]


def db_to_pandas():
    query = """
        SELECT artists, track_name, track_genre,
               acousticness, danceability, energy, instrumentalness,
               key, liveness, loudness, mode, speechiness, tempo, valence
        FROM songs
    """
    with sqlite3.connect("song_dataset.db") as conn:
        return pd.read_sql_query(query, conn)


def get_track_from_api(query_text, page=0, size=5):
    if not isinstance(query_text, str) or len(query_text.strip()) < 3:
        return None

    query_text = query_text.strip()
    database_tracks = db_to_pandas()
    matching_tracks = database_tracks[
        database_tracks["track_name"].str.casefold() == query_text.casefold()
    ]
    if not matching_tracks.empty:
        return matching_tracks.iloc[[0]][FEATURE_COLUMNS]

    try:
        response = requests.get(
            "https://api.reccobeats.com/v1/track/search",
            headers={"Accept": "application/json", "User-Agent": "HiddenGem/1.0"},
            params={"searchText": query_text, "page": page, "size": size},
            timeout=10,
        )
        if response.status_code != 200 or "application/json" not in response.headers.get(
            "Content-Type", ""
        ):
            return None

        content = response.json().get("content", [])
        if not content:
            return None
        audio_features = get_audio_features(content[0].get("id"))
        if not audio_features or not all(
            column in audio_features for column in FEATURE_COLUMNS
        ):
            return None
        return pd.DataFrame([audio_features])[FEATURE_COLUMNS]
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


def get_audio_features(track_id):
    if not track_id:
        return None

    try:
        response = requests.get(
            f"https://api.reccobeats.com/v1/track/{track_id}/audio-features",
            headers={"Accept": "application/json", "User-Agent": "HiddenGem/1.0"},
            timeout=10,
        )
        if response.status_code != 200 or "application/json" not in response.headers.get(
            "Content-Type", ""
        ):
            return None
        return response.json()
    except (requests.RequestException, ValueError):
        return None
