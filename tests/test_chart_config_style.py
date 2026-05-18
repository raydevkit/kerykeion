from app.schemas.common import ChartConfig


def test_chart_config_defaults_to_modern_style():
    config = ChartConfig()

    assert config.style == "modern"


def test_chart_config_accepts_classic_style():
    config = ChartConfig(style="classic")

    assert config.style == "classic"
