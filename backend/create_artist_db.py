import pandas as pd

from sqlalchemy import create_engine
from monthly_listeners import monthly_listeners_func
import requests
import sqlite3

def check_for_multiple_artists(df):
    df = df.copy()
    df['artists'] = df['artists'].str.split(';')
    df = df.explode('artists')
    df['artists'] = df['artists'].str.strip()
    df = df.reset_index(drop=True)

    return df

import time
import random
import requests


def get_monthly_listeners(artist_name):
    url = "https://api.reccobeats.com/v1/artist/search"

    params = {
        "searchText": artist_name.strip(),
        "page": 0,
        "size": 1
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        # Rate limited
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")

            if retry_after:
                wait_time = int(retry_after)
            else:
                wait_time = 10

            print(
                f"Rate limited. Waiting {wait_time} seconds..."
            )

            time.sleep(wait_time)

            # Try the request again
            return get_monthly_listeners(artist_name)

        response.raise_for_status()

        data = response.json()

        if not data.get("content"):
            print(f"Artist not found: {artist_name}")
            return None

        artist_url = data["content"][0]["href"]

        artist_id = artist_url.replace(
            "https://open.spotify.com/artist/",
            ""
        )

        return monthly_listeners_func(artist_id)

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {artist_name}: {e}")
        return None

def add_monthly_listeners_column(df):
    df = df.copy()

    cache = {}
    monthly_listeners = []

    for artist_name in df['artists']:

        # Use cached result if we've already looked up this artist
        if artist_name in cache:
            listeners = cache[artist_name]

        else:
            print(f"Fetching: {artist_name}")

            listeners = get_monthly_listeners(artist_name)

            cache[artist_name] = listeners

            # Random delay between requests
            wait_time = random.uniform(2.0, 5.0)

            print(f"Waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)

        monthly_listeners.append(listeners)

    df['monthly_listeners'] = monthly_listeners

    return df

engine = create_engine('sqlite:///song_dataset.db')
sql_query = "SELECT artists FROM songs"

df = pd.read_sql_query(sql_query, engine)
df = check_for_multiple_artists(df).drop_duplicates(subset=['artists']).dropna()


    