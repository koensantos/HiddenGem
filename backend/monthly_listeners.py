import re
import requests


def monthly_listeners_func(artist_id: str) -> int:
    url = f"https://open.spotify.com/artist/{artist_id}"

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

        response.raise_for_status()

        html = response.text

        # Handles:
        # Artist · 114,600,000 monthly listeners
        # Artist · 114.6M monthly listeners
        # Artist · 114.6 million monthly listeners

        match = re.search(
            r"Artist\s*·\s*([0-9.,]+)\s*([KMB])?\s*(?:monthly listeners)",
            html,
            re.IGNORECASE
        )

        if not match:
            raise Exception("Monthly listeners not found")

        number = match.group(1).replace(",", "")
        suffix = match.group(2)

        value = float(number)

        if suffix:
            suffix = suffix.upper()

            if suffix == "K":
                value *= 1_000
            elif suffix == "M":
                value *= 1_000_000
            elif suffix == "B":
                value *= 1_000_000_000

        return int(value)

    except requests.exceptions.RequestException as e:
        print(f"Spotify request failed for {artist_id}: {e}")
        return None

    except Exception as e:
        print(f"Could not get monthly listeners for {artist_id}: {e}")
        return None

