"""Enumerations for tarot card classification."""

from enum import Enum


class Orientation(Enum):
    """Card orientation in a reading."""
    UPRIGHT = "upright"
    REVERSED = "reversed"
    BETWEEN = "between"


class Suit(Enum):
    """Minor Arcana suits."""
    CUPS = "Cups"
    PENTACLES = "Pentacles"
    SWORDS = "Swords"
    WANDS = "Wands"


class ArcanaType(Enum):
    """Card arcana classification."""
    MAJOR = "major"
    MINOR = "minor"
    MODERN = "modern"


class Rank(Enum):
    """Minor Arcana ranks."""
    ACE = "Ace"
    TWO = "Two"
    THREE = "Three"
    FOUR = "Four"
    FIVE = "Five"
    SIX = "Six"
    SEVEN = "Seven"
    EIGHT = "Eight"
    NINE = "Nine"
    TEN = "Ten"
    PAGE = "Page"
    KNIGHT = "Knight"
    QUEEN = "Queen"
    KING = "King"
