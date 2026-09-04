"""Flask API for HiddenGem recommendations."""

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from .service import SongNotFoundError, recommendation_service
except ImportError:
    from service import SongNotFoundError, recommendation_service


app = Flask(__name__)
CORS(app)


@app.post("/recommendations")
def run_recommendation():
    try:
        return jsonify(recommendation_service.recommend(request.get_json(silent=True)))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SongNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    except Exception:
        app.logger.exception("Recommendation request failed")
        return jsonify({"error": "Unable to generate recommendations."}), 500


if __name__ == "__main__":
    app.run(debug=True)
