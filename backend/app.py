import math

from similarity_score import calculate_similarity_score
from flask import Flask, jsonify, request

app = Flask(__name__)

RECOMMENDATION_LIMIT = 5
DEFAULT_GENRE = "pop"
RESPONSE_FIELDS = (
    "track_name",
    "artists",
    "monthly_listeners",
    "cosine_similarity",
)


def validate_recommendation_request(data):
    """Validate and normalize the public recommendation request body."""
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")

    song_name = data.get("song_name")
    if not isinstance(song_name, str) or len(song_name.strip()) < 3:
        raise ValueError("song_name must be a string with at least 3 characters.")

    min_monthly_listeners = data.get("min_monthly_listeners")
    max_monthly_listeners = data.get("max_monthly_listeners")
    if isinstance(min_monthly_listeners, bool) or not isinstance(min_monthly_listeners, (int, float)):
        raise ValueError("min_monthly_listeners must be a number.")
    if isinstance(max_monthly_listeners, bool) or not isinstance(max_monthly_listeners, (int, float)):
        raise ValueError("max_monthly_listeners must be a number.")
    if not math.isfinite(min_monthly_listeners) or not math.isfinite(max_monthly_listeners):
        raise ValueError("Listener counts must be finite numbers.")
    if min_monthly_listeners < 0 or max_monthly_listeners < 0:
        raise ValueError("Listener counts must be zero or greater.")
    if min_monthly_listeners > max_monthly_listeners:
        raise ValueError("min_monthly_listeners must not exceed max_monthly_listeners.")

    return song_name.strip(), min_monthly_listeners, max_monthly_listeners

def get_recommendations(song_name, min_monthly_listeners, max_monthly_listeners, genre):
    return calculate_similarity_score(
        song_1=song_name,
        min_monthly_listeners=min_monthly_listeners,
        max_monthly_listeners=max_monthly_listeners,
        genre=genre
    )

@app.post("/recommendations")
def run_recommendation():
    try:
        song_name, min_monthly_listeners, max_monthly_listeners = validate_recommendation_request(
            request.get_json(silent=True)
        )
        recommendations = get_recommendations(
            song_name,
            min_monthly_listeners,
            max_monthly_listeners,
            DEFAULT_GENRE
        )
        public_recommendations = [
            {field: recommendation[field] for field in RESPONSE_FIELDS}
            for recommendation in recommendations[:RECOMMENDATION_LIMIT]
        ]
        return jsonify({"recommendations": public_recommendations})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("Recommendation request failed")
        return jsonify({"error": "Unable to generate recommendations."}), 500

if __name__ == '__main__':
    app.run(debug=True)