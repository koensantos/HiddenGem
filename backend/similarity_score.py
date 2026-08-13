from song_retrieval import get_track_from_api, db_to_pandas
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import sqlite3
import pandas as pd

def add_monthly_listeners_column(df):
    df = df.copy()

    # Extract the primary artist from each song
    df["primary_artist"] = (
        df["artists"]
        .str.split(";")
        .str[0]
        .str.strip()
    )

    # Load artist listener data
    conn = sqlite3.connect("artist.db")

    artist_df = pd.read_sql_query(
        "SELECT artists, monthly_listeners FROM artist_table",
        conn
    )

    conn.close()

    # Clean and deduplicate artist records
    artist_df["artists"] = (
        artist_df["artists"]
        .str.strip()
    )

    artist_df = artist_df.drop_duplicates(
        subset=["artists"]
    )

    artist_df = artist_df.rename(
        columns={
            "artists": "artist_name"
        }
    )

    # Attach monthly listeners to each song
    df = df.merge(
        artist_df,
        how="left",
        left_on="primary_artist",
        right_on="artist_name"
    )

    return df.drop(
        columns=["primary_artist", "artist_name"]
    )


def calculate_similarity_score(
    song_1,
    min_monthly_listeners,
    max_monthly_listeners,
    genre
):
    if min_monthly_listeners >= max_monthly_listeners:
        print("The minimum listeners are greater than the max listeners. Please update your range.")
        return None

    print("\n" + "=" * 60)
    print("HIDDENGEM RECOMMENDATION ENGINE")
    print("=" * 60)

    print(f"\nInput song: {song_1}")
    print(
        f"Hidden Gem range: "
        f"{min_monthly_listeners:,} - "
        f"{max_monthly_listeners:,} monthly listeners"
    )

    # Retrieve audio features for the input song
    song_features = get_track_from_api(song_1)

    if song_features is None:
        print("\nError: Could not retrieve song features.")
        return None

    # Load the song database
    df = db_to_pandas()

    if df.empty:
        print("\nError: Song database is empty.")
        return None

    original_size = len(df)

    # Add artist popularity data
    df = add_monthly_listeners_column(df)

    # Clean listener data
    df["monthly_listeners"] = pd.to_numeric(
        df["monthly_listeners"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["monthly_listeners"]
    )

    df = df[
        df["monthly_listeners"] > 0
    ]

    # Filter songs based on the user's Hidden Gem range
    df = df[
        (df["monthly_listeners"] >= min_monthly_listeners) &
        (df["monthly_listeners"] <= max_monthly_listeners)
    ]

    if genre is not None:
        df = df[
            df["track_genre"].str.lower() == genre.lower()
        ]
    else:
        print("This genre does not exist. Please try again.")
        return None

    # Treat the same song/artist combination as one recommendation
    df = df.drop_duplicates(
        subset=["track_name", "artists"],
        keep="first"
    )

    if df.empty:
        print("\nNo songs found within the selected listener range.")
        return None

    print("\nCandidate filtering")
    print("-" * 60)
    print(f"Songs in database:       {original_size:,}")
    print(f"Eligible recommendations: {len(df):,}")

    # Select only audio features used for similarity
    feature_columns = [
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
        "valence"
    ]

    feature_df = df[
        feature_columns
    ]

    song_features = song_features[
        feature_columns
    ]

    # Standardize features so large-scale features do not dominate
    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        feature_df
    )

    scaled_song_features = scaler.transform(
        song_features
    )

    # Calculate similarity between input song and candidates
    similarities = cosine_similarity(
        scaled_features,
        scaled_song_features
    ).flatten()

    df["cosine_similarity"] = similarities

    # Rank candidates by similarity
    recommendations = (
        df.sort_values(
            by="cosine_similarity",
            ascending=False
        )
        .head(5)
    )

    if len(recommendations) < 5:
        print("There are less than 5 songs present. For better recommendations, please change the listener range or the genre.")
        return None

    print("\nTop Hidden Gem Recommendations")
    print("-" * 60)

    print(
        recommendations[
            [
                "track_name",
                "artists",
                "monthly_listeners",
                "cosine_similarity"
            ]
        ].to_string(index=False)
    )

    print("\n" + "=" * 60)

    recommendations_json = recommendations.to_json(orient="records")
    return recommendations_json