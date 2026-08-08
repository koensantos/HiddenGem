import re
import requests


def monthly_listeners_func(artist_id: str) -> int:
    url = f"https://open.spotify.com/artist/{artist_id}"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise Exception(
            f"Spotify returned status code {response.status_code}"
        )

    html = response.text

    match = re.search(
        r"Artist · ([0-9.,]+)([KMB]) monthly listeners",
        html
    )

    if not match:
        raise Exception("Monthly listeners not found")

    number = match.group(1).replace(",", "")
    suffix = match.group(2)

    value = float(number)

    if suffix == "K":
        value *= 1_000
    elif suffix == "M":
        value *= 1_000_000
    elif suffix == "B":
        value *= 1_000_000_000

    return int(value)

