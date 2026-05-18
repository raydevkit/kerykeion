import pytest

from app.api.v1.birth_chart import generate_birth_chart
from app.schemas.common import ChartConfig, SubjectInput
from app.schemas.requests import BirthChartRequest


def make_request(style=None):
    config_kwargs = {} if style is None else {"style": style}
    return BirthChartRequest(
        subject=SubjectInput(
            name="Style Test",
            year=1990,
            month=5,
            day=15,
            hour=14,
            minute=30,
            longitude=12.4964,
            latitude=41.9028,
            timezone="Europe/Rome",
            city="Rome",
        ),
        config=ChartConfig(**config_kwargs),
    )


@pytest.mark.asyncio
async def test_birth_chart_route_uses_modern_style_by_default(monkeypatch):
    captured = {}

    def fake_create_astrological_subject(*args, **kwargs):
        return object()

    def fake_generate_birth_chart_svg(subject, *, theme, language, style):
        captured["style"] = style
        return "<svg />"

    monkeypatch.setattr(
        "app.api.v1.birth_chart.create_astrological_subject",
        fake_create_astrological_subject,
    )
    monkeypatch.setattr(
        "app.api.v1.birth_chart.generate_birth_chart_svg",
        fake_generate_birth_chart_svg,
    )
    monkeypatch.setattr("app.api.v1.birth_chart.subject_to_dict", lambda subject: {})

    await generate_birth_chart(make_request(), api_key="test")

    assert captured["style"] == "modern"


@pytest.mark.asyncio
async def test_birth_chart_route_passes_explicit_classic_style(monkeypatch):
    captured = {}

    def fake_create_astrological_subject(*args, **kwargs):
        return object()

    def fake_generate_birth_chart_svg(subject, *, theme, language, style):
        captured["style"] = style
        return "<svg />"

    monkeypatch.setattr(
        "app.api.v1.birth_chart.create_astrological_subject",
        fake_create_astrological_subject,
    )
    monkeypatch.setattr(
        "app.api.v1.birth_chart.generate_birth_chart_svg",
        fake_generate_birth_chart_svg,
    )
    monkeypatch.setattr("app.api.v1.birth_chart.subject_to_dict", lambda subject: {})

    await generate_birth_chart(make_request(style="classic"), api_key="test")

    assert captured["style"] == "classic"
