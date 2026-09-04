import unittest
from unittest.mock import patch

try:
    from . import service as service_module
    from .service import RecommendationService
except ImportError:
    import service as service_module
    from service import RecommendationService


class RecommendationServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = RecommendationService()
        self.valid_request = {
            "song": "I Ain't Worried",
            "min_monthly_listeners": 0,
            "max_monthly_listeners": 50_000_000,
        }

    def test_valid_song_is_accepted(self):
        song, minimum, maximum = self.service.validate_request(self.valid_request)
        self.assertEqual(song, "I Ain't Worried")
        self.assertEqual((minimum, maximum), (0.0, 50_000_000.0))

    def test_invalid_song_values_are_rejected(self):
        invalid_requests = (
            {},
            {"song": 123},
            {"song": ""},
            {"song": "x" * 101},
        )
        for request in invalid_requests:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    self.service.validate_request(request)

    def test_listener_range_validation_is_preserved(self):
        invalid_request = {**self.valid_request, "min_monthly_listeners": 10, "max_monthly_listeners": 1}
        with self.assertRaises(ValueError):
            self.service.validate_request(invalid_request)

    def test_response_uses_song_and_preserves_recommendation_artist(self):
        with patch.object(service_module, "calculate_similarity_score") as calculate:
            calculate.return_value = [
                {
                    "artists": "OneRepublic",
                    "track_name": "I Ain't Worried",
                    "cosine_similarity": 0.9086,
                    "monthly_listeners": 49_000_000,
                }
            ]

            response = self.service.recommend(self.valid_request)

        self.assertEqual(response["song"], "I Ain't Worried")
        self.assertNotIn("artist", response)
        self.assertEqual(response["recommendations"][0]["artist"], "OneRepublic")
        calculate.assert_called_once_with(
            input_song="I Ain't Worried",
            min_monthly_listeners=0.0,
            max_monthly_listeners=50_000_000.0,
            genre="pop",
        )


if __name__ == "__main__":
    unittest.main()
