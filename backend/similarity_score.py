#Generates the similarity score between the user input and songs in the database using cosine similarity.
#Returns the top 5 most similar songs to the user input.

from song_retrieval import get_track_from_api, db_to_pandas
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity_score(song_1):
    song_features = get_track_from_api(song_1)

    if song_features is None:
        print("Error: Could not retrieve song features.")
        return None

    # Original dataframe (keep all columns)
    df = db_to_pandas()

    if df.empty:
        print("Error: Database is empty.")
        return None

    # Numeric features only for similarity calculation
    feature_df = df.drop(columns=[
        'track_id',
        'artists',
        'album_name',
        'track_name',
        'popularity',
        'duration_ms',
        'explicit',
        'time_signature',
        'track_genre'
    ]).sort_index(axis=1)

    # Calculate cosine similarity
    df["cosine_similarity"] = cosine_similarity(
        feature_df,
        song_features
    ).flatten()

    # Sort using the original dataframe
    df = df.sort_values(by="cosine_similarity", ascending=False)

    return df["track_name"][1:6].tolist()  # Return top 5 similar songs, excluding the input song itself

print(calculate_similarity_score("Shape of You"))