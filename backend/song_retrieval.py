from unittest import result
import warnings
import requests
import sqlite3
import pandas as pd
from monthly_listeners import monthly_listeners_func
warnings.filterwarnings("ignore", message=".*doesn't match a supported version.*")

def db_to_pandas():
    # 1. Connect to the SQLite database file
    conn = sqlite3.connect("song_dataset.db")

    # 2. Write your SQL query
    query = "SELECT * FROM songs"

    # 3. Read the data directly into a DataFrame
    df = pd.read_sql_query(query, conn)

    # 4. Always close the connection when finished
    conn.close()

    # View the data
    return df

def get_track_from_api(query_text, search_type="track", page=0, size=5):
    # Dynamically select endpoint based on your design intentions
    url = "https://api.reccobeats.com/v1/track/search"

    # Input length validation to guarantee an API crash isn't forced 
    if not query_text or len(query_text.strip()) < 3:
        print("Error: Search query must be at least 3 characters long.")
        return None

    # Map variables smoothly to request arguments 
    params = {
        "searchText": query_text.strip(),
        "page": page,
        "size": size
    }

    # CRITICAL: Retaining the browser configuration header sequence that worked
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }


    df = db_to_pandas()
    result = df.loc[df["track_name"] == query_text].drop(columns=['track_id','album_name'])
    result = pd.DataFrame()  # Placeholder for database query result
    # 2. Check if the result contains any rows
    if not result.empty:
        return result.iloc[[0]].drop(columns=['track_name', 'popularity', 'duration_ms', 'explicit', 'time_signature', 'track_genre', 'artists']).sort_index(axis=1)

    try:
        response = requests.get(url, headers=headers, params=params)

        
        # Verify Content-Type explicitly verifies incoming JSON data arrays
        if 'application/json' not in response.headers.get('Content-Type', ''):
            print(f"Error: Server returned unexpected '{response.headers.get('Content-Type')}' layout.")
            return None
            
        if response.status_code == 200:
            response = response.json()
            id = response["content"][0]["id"]
            audio_features = pd.DataFrame([get_audio_features(id)])
            return audio_features.drop(columns=["id", "href", "isrc"])
        else:
            print(f"Failed to fetch data (Status {response.status_code}): {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network connection failure: {e}")
        return None

def get_audio_features(id):
    url = f"https://api.reccobeats.com/v1/track/{id}/audio-features"

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)

        if 'application/json' not in response.headers.get('Content-Type', ''):
            print(f"Error: Server returned unexpected '{response.headers.get('Content-Type')}' layout.")
            return None

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch audio features (Status {response.status_code}): {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network connection failure: {e}")
        return None

print(get_track_from_api("Say Something"))