"""A80: wheel text fixes (seconds carry, German angle labels, translated synastry title)."""
from kerykeion.charts.charts_utils import convert_decimal_to_degree_string
from kerykeion.settings.translation_strings import LANGUAGE_SETTINGS


def test_seconds_never_read_60():
    # 24 + 2/60 + 59.7/3600 used to render 24°02'60"
    assert convert_decimal_to_degree_string(24 + 2 / 60 + 59.7 / 3600) == "24°03'00\""
    assert convert_decimal_to_degree_string(24 + 59 / 60 + 59.7 / 3600) == "25°00'00\""
    assert convert_decimal_to_degree_string(10 + 22 / 60 + 48 / 3600) == "10°22'48\""


def test_german_angle_labels_match_the_wheel_glyphs():
    points = LANGUAGE_SETTINGS["DE"]["celestial_points"]
    assert (points["Ascendant"], points["Descendant"]) == ("As", "Ds")


def test_every_language_has_a_synastry_title_label():
    for lang, strings in LANGUAGE_SETTINGS.items():
        assert strings.get("Synastry"), lang
