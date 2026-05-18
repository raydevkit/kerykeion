"""
Chart Service

Handles SVG chart generation using Kerykeion's ChartDrawer (v5).
Falls back to legacy KerykeionChartSVG for compatibility.
"""

from typing import Optional
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from kerykeion.charts.chart_drawer import ChartDrawer
from kerykeion.chart_data_factory import ChartDataFactory
import tempfile
import os
import logging
import warnings

logger = logging.getLogger(__name__)


def _to_model(subject):
    if hasattr(subject, 'model'):
        return subject.model()
    return subject


def generate_birth_chart_svg(
    subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN",
    style: str = "modern",
) -> str:
    if style == "modern":
        return generate_birth_chart_svg_modern(subject, theme=theme, language=language)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = KerykeionChartSVG(
                subject,
                chart_type="Natal",
                new_output_directory=temp_dir,
                theme=theme,
                chart_language=language,
            )

            chart.makeSVG()

            svg_filename = f"{subject.name} - Natal Chart.svg"
            svg_path = os.path.join(temp_dir, svg_filename)

            if os.path.exists(svg_path):
                with open(svg_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
                if svg_files:
                    with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    raise FileNotFoundError("Failed to generate SVG chart")


def generate_birth_chart_svg_modern(
    subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN",
) -> str:
    model = _to_model(subject)
    chart_data = ChartDataFactory.create_natal_chart_data(model)
    drawer = ChartDrawer(chart_data, theme=theme, chart_language=language, style="modern")
    return drawer.generate_svg_string()


def generate_synastry_chart_svg(
    subject_one: AstrologicalSubject,
    subject_two: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN",
    style: str = "modern",
) -> str:
    if style == "modern":
        chart_data = ChartDataFactory.create_synastry_chart_data(
            _to_model(subject_one),
            _to_model(subject_two),
        )
        drawer = ChartDrawer(chart_data, theme=theme, chart_language=language, style="modern")
        return drawer.generate_svg_string()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = KerykeionChartSVG(
                subject_one,
                chart_type="Synastry",
                second_obj=subject_two,
                new_output_directory=temp_dir,
                theme=theme,
                chart_language=language,
            )

            chart.makeSVG()

            svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
            if svg_files:
                with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise FileNotFoundError("Failed to generate synastry SVG chart")


def generate_transit_chart_svg(
    natal_subject: AstrologicalSubject,
    transit_subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN",
    style: str = "modern",
) -> str:
    if style == "modern":
        chart_data = ChartDataFactory.create_transit_chart_data(
            _to_model(natal_subject),
            _to_model(transit_subject),
        )
        drawer = ChartDrawer(chart_data, theme=theme, chart_language=language, style="modern")
        return drawer.generate_svg_string()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = KerykeionChartSVG(
                natal_subject,
                chart_type="Transit",
                second_obj=transit_subject,
                new_output_directory=temp_dir,
                theme=theme,
                chart_language=language,
            )

            chart.makeSVG()

            svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
            if svg_files:
                with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise FileNotFoundError("Failed to generate transit SVG chart")


def generate_composite_chart_svg(
    composite_subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN",
    style: str = "modern",
) -> str:
    if style == "modern":
        chart_data = ChartDataFactory.create_composite_chart_data(_to_model(composite_subject))
        drawer = ChartDrawer(chart_data, theme=theme, chart_language=language, style="modern")
        return drawer.generate_svg_string()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = KerykeionChartSVG(
                composite_subject,
                chart_type="Composite",
                new_output_directory=temp_dir,
                theme=theme,
                chart_language=language,
            )

            chart.makeSVG()

            svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
            if svg_files:
                with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise FileNotFoundError("Failed to generate composite SVG chart")


def generate_chart_wheel_only(
    subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN",
) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = KerykeionChartSVG(
                subject,
                new_output_directory=temp_dir,
                theme=theme,
                chart_language=language,
            )

            chart.makeWheelOnlySVG()

            svg_filename = f"{subject.name}_Wheel_Only.svg"
            svg_path = os.path.join(temp_dir, svg_filename)

            if os.path.exists(svg_path):
                with open(svg_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise FileNotFoundError("Failed to generate wheel SVG")
