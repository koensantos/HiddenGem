import sqlite3

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from song_retrieval import db_to_pandas, get_track_from_api


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
RESPONSE_COLUMNS = [
    "track_name",
    "artists",
    "monthly_listeners",
    "cosine_similarity",
]
RECOMMENDATION_LIMIT = 5


def add_monthly_listeners_column(df):
    df = df.copy()
    df["primary_artist"] = df["artists"].str.split(";").str[0].str.strip()

    with sqlite3.connect("artist.db") as conn:
        artist_df = pd.read_sql_query(
            "SELECT artists, monthly_listeners FROM artist_table",
            conn,
        )

    artist_df["artists"] = artist_df["artists"].str.strip()
    artist_df = artist_df.drop_duplicates(subset=["artists"])
    artist_df = artist_df.rename(columns={"artists": "artist_name"})

    df = df.merge(
        artist_df,
        how="left",
        left_on="primary_artist",
        right_on="artist_name",
    )
    return df.drop(columns=["primary_artist", "artist_name"])


def filter_candidates(df, min_monthly_listeners, max_monthly_listeners, genre):
    df = add_monthly_listeners_column(df)
    df["monthly_listeners"] = pd.to_numeric(
        df["monthly_listeners"], errors="coerce"
    )
    df = df.dropna(subset=["monthly_listeners"])
    df = df[df["monthly_listeners"] > 0]
    df = df[
        (df["monthly_listeners"] >= min_monthly_listeners)
        & (df["monthly_listeners"] <= max_monthly_listeners)
    ]
    if not genre:
        raise ValueError("Genre does not exist.")
    df = df[df["track_genre"].str.casefold() == genre.casefold()]
    return df.drop_duplicates(subset=["track_name", "artists"], keep="first")


def calculate_similarity_score(song_1, min_monthly_listeners, max_monthly_listeners, genre):
    if min_monthly_listeners > max_monthly_listeners:
        raise ValueError("min_monthly_listeners must not exceed max_monthly_listeners.")

    song_features = get_track_from_api(song_1)
    if song_features is None:
        raise ValueError("Song was not found or its audio features could not be retrieved.")

    df = db_to_pandas()
    if df.empty:
        raise ValueError("No songs are available for recommendations.")

    candidates = filter_candidates(
        df, min_monthly_listeners, max_monthly_listeners, genre
    )
    if candidates.empty:
        raise ValueError("No songs were found within the listener range.")

    feature_df = candidates[FEATURE_COLUMNS]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_df)
    scaled_song_features = scaler.transform(song_features[FEATURE_COLUMNS])
    candidates["cosine_similarity"] = cosine_similarity(
        scaled_features, scaled_song_features
    ).flatten()

    recommendations = candidates.nlargest(
        RECOMMENDATION_LIMIT, "cosine_similarity"
    )
    return recommendations[RESPONSE_COLUMNS].to_dict(orient="records")
