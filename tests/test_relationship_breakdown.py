import pytest
import logging

logging.basicConfig(level=logging.CRITICAL)

from kerykeion import AstrologicalSubject
from app.services.relationship_service import calculate_relationship_score


class TestRelationshipBreakdown:
    def setup_class(self):
        self.john = AstrologicalSubject("John", 1940, 10, 9, 18, 30, lng=-2.98, lat=53.41, tz_str="Europe/London", city="Liverpool")
        self.yoko = AstrologicalSubject("Yoko", 1933, 2, 18, 20, 30, lng=139.69, lat=35.69, tz_str="Asia/Tokyo", city="Tokyo")

    def test_breakdown_not_all_100(self):
        result = calculate_relationship_score(self.john, self.yoko)
        breakdown = result['breakdown']

        values = list(breakdown.values())
        assert len(values) > 0, "Breakdown should have categories"

        all_100 = all(v == 100 for v in values)
        assert not all_100, (
            f"Category breakdown should not all be 100. Got: {breakdown}"
        )

    def test_breakdown_categories_vary(self):
        result = calculate_relationship_score(self.john, self.yoko)
        breakdown = result['breakdown']

        values = list(breakdown.values())
        unique_values = set(values)
        assert len(unique_values) > 1, (
            f"Category breakdown should have varying values. Got: {breakdown}"
        )

    def test_breakdown_within_0_100(self):
        result = calculate_relationship_score(self.john, self.yoko)
        breakdown = result['breakdown']

        for category, score in breakdown.items():
            assert 0 <= score <= 100, (
                f"Category {category} score {score} is out of [0, 100] range"
            )

    def test_breakdown_neutral_without_aspects(self):
        result = calculate_relationship_score(self.john, self.yoko)
        breakdown = result['breakdown']

        for category, score in breakdown.items():
            assert score >= 0, f"Category {category} should be >= 0, got {score}"

    def test_percentage_differs_from_all_categories(self):
        result = calculate_relationship_score(self.john, self.yoko)
        pct = result['percentage']
        breakdown = result['breakdown']

        assert pct != 100.0 or not all(v == 100 for v in breakdown.values()), (
            "Overall percentage and all categories shouldn't all be exactly 100"
        )


if __name__ == "__main__":
    pytest.main(["-vv", "--log-level=CRITICAL", "--log-cli-level=CRITICAL", __file__])
