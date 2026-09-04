"""Application logic for the recommendation endpoint."""

import math
from typing import Any

from matplotlib import artist

try:
    from .similarity_score import calculate_similarity_score
except ImportError:
    from similarity_score import calculate_similarity_score


class SongNotFoundError(Exception):
    """Raised when the recommendation engine cannot find the requested song."""


class RecommendationService:
    """Validate requests and translate engine results into API responses."""

    def __init__(self, recommendation_limit: int = 5, genre: str = "pop"):
        self.recommendation_limit = recommendation_limit
        self.genre = genre

    def validate_request(self, data: Any) -> tuple[str, float, float]:
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")

        song = data.get("song")
        if not isinstance(song, str):
            raise ValueError("song must be a string.")
        song = song.strip()
        if not song:
            raise ValueError("song is required.")
        if len(song) > 100:
            raise ValueError("song must be 100 characters or fewer.")

        minimum = self._number(data.get("min_monthly_listeners"), "min_monthly_listeners")
        maximum = self._number(data.get("max_monthly_listeners"), "max_monthly_listeners")
        if minimum > maximum:
            raise ValueError("min_monthly_listeners must not exceed max_monthly_listeners.")
        return song, minimum, maximum

    @staticmethod
    def _number(value: Any, field_name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a number.")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{field_name} must be a finite number greater than or equal to 0.")
        return float(value)

    def recommend(self, data: Any) -> dict[str, Any]:
        song, minimum, maximum = self.validate_request(data)
        try:
            recommendations = calculate_similarity_score(
                input_song=song,
                min_monthly_listeners=minimum,
                max_monthly_listeners=maximum,
                genre=self.genre,
            )
        except ValueError as error:
            if "Song was not found" in str(error):
                raise SongNotFoundError(str(error)) from error
            raise

        return {
            "song": song,
            "recommendations": [self._format_recommendation(item) for item in recommendations[: self.recommendation_limit]],
        }

    @staticmethod
    def _format_recommendation(recommendation: dict[str, Any]) -> dict[str, Any]:
        artists = str(recommendation.get("artists", "")).split(";")[0].strip()
        return {
            "artist": artists,
            "track": recommendation.get("track_name", ""),
            "similarity": round(float(recommendation.get("cosine_similarity", 0)), 4),
            "monthly_listeners": int(recommendation.get("monthly_listeners", 0)),
        }


recommendation_service = RecommendationService()