"""Custom exceptions for the tarot deck reader."""


class DeckLoadError(Exception):
    """Raised when the deck or card JSON cannot be loaded."""


class CardLoadError(DeckLoadError):
    """Raised when an individual card JSON cannot be loaded."""
