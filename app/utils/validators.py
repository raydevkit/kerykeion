"""
Validation Utilities

Helper functions for validating and converting input data.
"""


# House system name to identifier mapping
HOUSE_SYSTEM_MAP = {
    # Full names
    "placidus": "P",
    "koch": "K",
    "whole sign": "W",
    "whole_sign": "W",
    "equal": "E",
    "campanus": "C",
    "regiomontanus": "R",
    "porphyrius": "O",
    "morinus": "M",
    "alcabitus": "B",
    "azimuthal": "H",
    "horizontal": "A",
    "polich page": "T",
    "topocentric": "T",
    "meridian": "X",
    "krusinski": "U",
    "gauquelin": "G",

    # Already correct identifiers (pass through)
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "F",
    "h": "H",
    "i": "I",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "O",
    "p": "P",
    "q": "Q",
    "r": "R",
    "s": "S",
    "t": "T",
    "u": "U",
    "v": "V",
    "w": "W",
    "x": "X",
    "y": "Y",
}


def normalize_house_system(house_system: str) -> str:
    """
    Convert house system name to Kerykeion identifier.

    Args:
        house_system: House system name or identifier

    Returns:
        Single letter identifier (e.g., "P" for Placidus)

    Raises:
        ValueError: If house system is not recognized
    """
    normalized = house_system.lower().strip()

    if normalized in HOUSE_SYSTEM_MAP:
        return HOUSE_SYSTEM_MAP[normalized]

    # If it's already a single uppercase letter, return it
    if len(house_system) == 1 and house_system.upper() in HOUSE_SYSTEM_MAP.values():
        return house_system.upper()

    raise ValueError(
        f"Invalid house system '{house_system}'. "
        f"Valid options: Placidus (P), Koch (K), Whole Sign (W), Equal (E), "
        f"Campanus (C), Regiomontanus (R), Porphyrius (O), Morinus (M), or single letter codes."
    )


def normalize_zodiac_type(zodiac_type: str) -> str:
    """
    Normalize zodiac type input.

    Args:
        zodiac_type: Zodiac type (e.g., "Tropical", "Tropic", "Sidereal")

    Returns:
        Normalized zodiac type: "Tropic" or "Sidereal"
    """
    normalized = zodiac_type.lower().strip()

    if normalized in ["tropic", "tropical", "western"]:
        return "Tropic"
    elif normalized in ["sidereal", "vedic"]:
        return "Sidereal"
    else:
        raise ValueError(
            f"Invalid zodiac type '{zodiac_type}'. "
            f"Valid options: 'Tropic' (Tropical/Western) or 'Sidereal' (Vedic)"
        )
