from song_retrieval import get_track_from_api, db_to_pandas
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pandas as pd
import sqlite3


def add_monthly_listeners_column(df):
    df = df.copy()

    # Get the first artist from each song
    df["primary_artist"] = (
        df["artists"]
        .str.split(";")
        .str[0]
        .str.strip()
    )

    # Load artist data from SQLite
    conn = sqlite3.connect("artist.db")

    artist_df = pd.read_sql_query(
        "SELECT artists, monthly_listeners FROM artist_table",
        conn
    )

    conn.close()

    # Clean artist names
    artist_df["artists"] = (
        artist_df["artists"]
        .str.strip()
    )

    # Keep only one row per artist
    artist_df = artist_df.drop_duplicates(
        subset=["artists"]
    )

    # Rename artist column for the merge
    artist_df = artist_df.rename(
        columns={
            "artists": "artist_name"
        }
    )

    # Match each song to its primary artist
    df = df.merge(
        artist_df,
        how="left",
        left_on="primary_artist",
        right_on="artist_name"
    )

    # Remove temporary columns
    df = df.drop(
        columns=[
            "primary_artist",
            "artist_name"
        ]
    )

    return df


def calculate_similarity_score(
    song_1,
    min_monthly_listeners=10000,
    max_monthly_listeners=100000
):

    # Get audio features for the user's song
    song_features = get_track_from_api(song_1)

    if song_features is None:
        print("Error: Could not retrieve song features.")
        return None

    print("\nSong feature columns:")
    print(song_features.columns.tolist())

    # Load song database
    df = db_to_pandas()

    if df.empty:
        print("Error: Database is empty.")
        return None

    print("\nOriginal database size:")
    print(len(df))

    # Add monthly listeners
    df = add_monthly_listeners_column(df)

    # Convert listener values to numeric
    df["monthly_listeners"] = pd.to_numeric(
        df["monthly_listeners"],
        errors="coerce"
    )

    # Remove missing listener values
    df = df.dropna(
        subset=["monthly_listeners"]
    )

    # Remove invalid zero/negative listener values
    df = df[
        df["monthly_listeners"] > 0
    ]

    # Apply monthly listener range
    df = df[
        (df["monthly_listeners"] >= min_monthly_listeners) &
        (df["monthly_listeners"] <= max_monthly_listeners)
    ]

    # Remove duplicate songs
    df = df.drop_duplicates(
        subset=["track_name", "artists"],
        keep="first"
    )

    print("\nDuplicate track names/artists:")
    print(
        df[
            df.duplicated(
                subset=["track_name", "artists"],
                keep=False
            )
        ][
            [
                "track_id",
                "track_name",
                "artists",
                "monthly_listeners"
            ]
        ].sort_values(
            by=["track_name", "artists"]
        ).head(20).to_string(index=False)
    )

    print(
        f"\nSongs between "
        f"{min_monthly_listeners:,} and "
        f"{max_monthly_listeners:,} monthly listeners:"
    )
    print(len(df))

    if df.empty:
        print(
            "No songs found within the selected "
            "monthly listener range."
        )
        return None

    # Select audio features
    feature_df = df.drop(columns=[
        "Unnamed: 0",
        "track_id",
        "artists",
        "album_name",
        "track_name",
        "popularity",
        "duration_ms",
        "explicit",
        "time_signature",
        "track_genre",
        "monthly_listeners"
    ]).sort_index(axis=1)

    # Match API feature order to database feature order
    song_features = song_features[
        feature_df.columns
    ]

    # Standardize audio features
    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        feature_df
    )

    scaled_song_features = scaler.transform(
        song_features
    )

    # Calculate cosine similarity
    df["cosine_similarity"] = cosine_similarity(
        scaled_features,
        scaled_song_features
    ).flatten()

    # Rank by similarity
    df = df.sort_values(
        by="cosine_similarity",
        ascending=False
    )

    # Display top 20 results
    print("\nTop 20 results:")

    print(
        df[
            [
                "track_name",
                "artists",
                "monthly_listeners",
                "cosine_similarity"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    # Return top 5 recommendations
    return df[
        [
            "track_name",
            "artists",
            "monthly_listeners",
            "cosine_similarity"
        ]
    ].head(5)

print(calculate_similarity_score(
    song_1="Shape of You",
    min_monthly_listeners=10000,
    max_monthly_listeners=100000
))