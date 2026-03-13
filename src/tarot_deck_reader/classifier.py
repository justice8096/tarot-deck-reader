"""Card classification — infers arcana type, suit, and rank from card name."""

from __future__ import annotations

import re

from .enums import ArcanaType, Rank, Suit

# Major Arcana card names (as they appear in Deck.json)
MAJOR_ARCANA_NAMES: set[str] = {
    "The Fool",
    "The Magician",
    "High Priestess",
    "The Empress",
    "The Emperor",
    "Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
}

# Modern cards (non-traditional additions to this deck)
MODERN_CARD_NAMES: set[str] = {
    "Gig Worker",
    "Influencer (modern)",
    "Social Feed",
    "Streaming Binge",
    "Viral Post",
}

# Map rank words to enum values
_RANK_MAP: dict[str, Rank] = {r.value.lower(): r for r in Rank}

# Map suit words to enum values
_SUIT_MAP: dict[str, Suit] = {s.value.lower(): s for s in Suit}

# Pattern: "Rank of Suit" (e.g., "Ace of Cups", "Ten of Swords")
_MINOR_PATTERN = re.compile(
    r"^(" + "|".join(re.escape(r.value) for r in Rank) + r")\s+of\s+("
    + "|".join(re.escape(s.value) for s in Suit) + r")$",
    re.IGNORECASE,
)


def _normalize_name(name: str) -> str:
    """Normalize underscores and extra whitespace in card names."""
    return name.replace("_", " ").strip()


def classify_card(name: str) -> tuple[ArcanaType, Suit | None, Rank | None]:
    """Classify a card by its display name.

    Returns:
        Tuple of (arcana_type, suit_or_none, rank_or_none).

    Raises:
        ValueError: If the card name doesn't match any known pattern.
    """
    normalized = _normalize_name(name)

    # Check Major Arcana
    if normalized in MAJOR_ARCANA_NAMES:
        return (ArcanaType.MAJOR, None, None)

    # Check Modern cards
    if normalized in MODERN_CARD_NAMES:
        return (ArcanaType.MODERN, None, None)

    # Try Minor Arcana pattern
    match = _MINOR_PATTERN.match(normalized)
    if match:
        rank_str, suit_str = match.groups()
        rank = _RANK_MAP[rank_str.lower()]
        suit = _SUIT_MAP[suit_str.lower()]
        return (ArcanaType.MINOR, suit, rank)

    raise ValueError(
        f"Cannot classify card '{name}' (normalized: '{normalized}'). "
        f"Not recognized as Major Arcana, Modern, or Minor Arcana (Rank of Suit)."
    )
