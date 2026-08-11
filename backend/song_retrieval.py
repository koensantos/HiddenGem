from unittest import result
import warnings
import requests
import sqlite3
import pandas as pd
from monthly_listeners import monthly_listeners_func
# Cleanly suppresses version mismatch warnings from your terminal window
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

def get_monthly_listeners(artist_name):
    url = "https://api.reccobeats.com/v1/artist/search"
    
    params = {
        "searchText": artist_name.strip(),
        "page": 0,
        "size": 1
    }

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if 'application/json' not in response.headers.get('Content-Type', ''):
            print(f"Error: Server returned unexpected '{response.headers.get('Content-Type')}' layout.")
            return None

        if response.status_code == 200:
            print(response.json())
            artist_url = response.json()["content"][0]["href"]
            artist_id = artist_url.replace("https://open.spotify.com/artist/", "") #Extract artist ID from Spotify URL
            monthy_listeners = monthly_listeners_func(artist_id) #Get monthly listeners from Spotify API

            return monthy_listeners
        else:
            print(f"Failed to fetch audio features (Status {response.status_code}): {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network connection failure: {e}")
        return None

#def add_monthly_listeners_column():
    conn = sqlite3.connect("song_dataset.db")
    df = pd.read_sql_query("SELECT * FROM songs", conn)

    for row in df.itertuples():
        artist_name = row.artists
        print(artist_name)
        monthly_listeners = get_monthly_listeners(artist_name)
        if monthly_listeners is not None:
            df.at[row.Index, 'monthly_listeners'] = monthly_listeners

    # Save the updated DataFrame back to the database
    df.to_sql("songs", conn, if_exists="replace", index=False)
    conn.close()

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
    print(df.columns)
    result = df.loc[df["track_name"] == query_text].drop(columns=['track_id','album_name'])
    #result = pd.DataFrame()  # Placeholder for database query result
    # 2. Check if the result contains any rows
    if not result.empty:
        try:
            #Get artist spotify href from API, then add to result.
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                reponse = response.json()
                spotify_href = reponse["content"][0]["href"]
                result['spotify_href'] = spotify_href
                return result.iloc[[0]].drop(columns=['track_name', 'popularity', 'duration_ms', 'explicit', 'time_signature', 'track_genre', 'artists', 'spotify_href']).sort_index(axis=1)
            else:
                print(f"Failed to fetch data (Status {response.status_code}): {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network connection failure: {e}")
            return None

    try:
        response = requests.get(url, headers=headers, params=params)

        
        # Verify Content-Type explicitly verifies incoming JSON data arrays
        if 'application/json' not in response.headers.get('Content-Type', ''):
            print(f"Error: Server returned unexpected '{response.headers.get('Content-Type')}' layout.")
            return None
            
        if response.status_code == 200:
            response = response.json()
            print(response["content"][0]["artists"])
            id = response["content"][0]["id"]
            audio_features = get_audio_features(id)
            df = pd.DataFrame([audio_features]).drop(columns=['id', 'href', 'isrc'])
            return df.sort_index(axis=1)  # Sort columns alphabetically for consistency
        else:
            print(f"Failed to fetch data (Status {response.status_code}): {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network connection failure: {e}")
        return None


#def get_song_from_api

#def check_song_in_database

#def add_song_to_database

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



def main():
    add_monthly_listeners_column()
#API columns: ['id', 'href', 'isrc', 'acousticness', 'danceability', 'energy',
#       'instrumentalness', 'key', 'liveness', 'loudness', 'mode',
#       'speechiness', 'tempo', 'valence']
#Database Columns: track_name', 'popularity', 'duration_ms', 'explicit',
#       'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
#       'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
#       'time_signature', 'track_genre']



if __name__ == "__main__":
    main()