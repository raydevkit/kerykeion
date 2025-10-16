"""
Chart Service

Handles SVG chart generation using Kerykeion's KerykeionChartSVG.
"""

from typing import Optional, Tuple
from kerykeion import AstrologicalSubject, KerykeionChartSVG
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


def generate_birth_chart_svg(
    subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN"
) -> str:
    """
    Generate birth chart SVG.

    Args:
        subject: AstrologicalSubject instance
        theme: Chart theme (light, dark, classic, dark_high_contrast)
        language: Chart language (EN, ES, FR, PT, IT, DE, RU, TR, CN, HI)

    Returns:
        SVG string content
    """
    # Create a temporary directory for SVG output
    with tempfile.TemporaryDirectory() as temp_dir:
        chart = KerykeionChartSVG(
            subject,
            chart_type="Natal",
            new_output_directory=temp_dir,
            theme=theme,
            chart_language=language
        )

        # Generate SVG
        chart.makeSVG()

        # Kerykeion uses " - " (space-dash-space) in filename, not underscore
        svg_filename = f"{subject.name} - Natal Chart.svg"
        svg_path = os.path.join(temp_dir, svg_filename)

        if os.path.exists(svg_path):
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            return svg_content
        else:
            # Try to find any SVG file in the directory
            svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
            if svg_files:
                logger.info(f"Found SVG file: {svg_files[0]}")
                with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                return svg_content
            else:
                logger.error(f"SVG file not found. Expected: {svg_path}")
                raise FileNotFoundError(f"Failed to generate SVG chart")


def generate_synastry_chart_svg(
    subject_one: AstrologicalSubject,
    subject_two: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN"
) -> str:
    """
    Generate synastry chart SVG.

    Args:
        subject_one: First AstrologicalSubject
        subject_two: Second AstrologicalSubject
        theme: Chart theme
        language: Chart language

    Returns:
        SVG string content
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        chart = KerykeionChartSVG(
            subject_one,
            chart_type="Synastry",
            second_obj=subject_two,
            new_output_directory=temp_dir,
            theme=theme,
            chart_language=language
        )

        chart.makeSVG()

        # Find generated SVG file (Kerykeion uses various naming patterns)
        svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
        if svg_files:
            with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                svg_content = f.read()
            return svg_content
        else:
            logger.error(f"Synastry SVG file not found in: {temp_dir}")
            raise FileNotFoundError("Failed to generate synastry SVG chart")


def generate_transit_chart_svg(
    natal_subject: AstrologicalSubject,
    transit_subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN"
) -> str:
    """
    Generate transit chart SVG.

    Args:
        natal_subject: Natal AstrologicalSubject
        transit_subject: Transit AstrologicalSubject (current date/time)
        theme: Chart theme
        language: Chart language

    Returns:
        SVG string content
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        chart = KerykeionChartSVG(
            natal_subject,
            chart_type="Transit",
            second_obj=transit_subject,
            new_output_directory=temp_dir,
            theme=theme,
            chart_language=language
        )

        chart.makeSVG()

        # Find generated SVG file
        svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
        if svg_files:
            with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                svg_content = f.read()
            return svg_content
        else:
            logger.error(f"Transit SVG file not found in: {temp_dir}")
            raise FileNotFoundError("Failed to generate transit SVG chart")


def generate_composite_chart_svg(
    composite_subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN"
) -> str:
    """
    Generate composite chart SVG.

    Args:
        composite_subject: Composite AstrologicalSubject (CompositeSubjectModel)
        theme: Chart theme
        language: Chart language

    Returns:
        SVG string content
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        chart = KerykeionChartSVG(
            composite_subject,
            chart_type="Composite",  # Use "Composite" chart type for proper handling
            new_output_directory=temp_dir,
            theme=theme,
            chart_language=language
        )

        chart.makeSVG()

        # Find generated SVG file
        svg_files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
        if svg_files:
            with open(os.path.join(temp_dir, svg_files[0]), 'r', encoding='utf-8') as f:
                svg_content = f.read()
            return svg_content
        else:
            logger.error(f"Composite SVG file not found in: {temp_dir}")
            raise FileNotFoundError("Failed to generate composite SVG chart")


def generate_chart_wheel_only(
    subject: AstrologicalSubject,
    theme: str = "light",
    language: str = "EN"
) -> str:
    """
    Generate chart wheel only (without aspect grid).

    Args:
        subject: AstrologicalSubject instance
        theme: Chart theme
        language: Chart language

    Returns:
        SVG string content
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        chart = KerykeionChartSVG(
            subject,
            new_output_directory=temp_dir,
            theme=theme,
            chart_language=language
        )

        chart.makeWheelOnlySVG()

        svg_filename = f"{subject.name}_Wheel_Only.svg"
        svg_path = os.path.join(temp_dir, svg_filename)

        if os.path.exists(svg_path):
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            return svg_content
        else:
            logger.error(f"Wheel SVG file not found: {svg_path}")
            raise FileNotFoundError("Failed to generate wheel SVG")
