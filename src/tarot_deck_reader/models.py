"""Core data models for tarot card data."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .enums import ArcanaType, Orientation, Rank, Suit


@dataclass(frozen=True)
class CardAssets:
    """Asset file paths for one orientation of a card."""
    image: Path | None = None
    card_image: Path | None = None
    narration: Path | None = None
    music: Path | None = None
    movie: Path | None = None
    palette_image: Path | None = None
    object_3d: Path | None = None
    card_image_upright: Path | None = None
    focus_stills: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class CardRecord:
    """One orientation's reading data for a card."""
    orientation: Orientation
    description: str
    meanings: list[str]
    keywords: list[str]
    advice: str
    affirmation: str
    categories: list[str]
    assets: CardAssets
    character_name: str | None = None


@dataclass(frozen=True)
class CardLevelAssets:
    """Top-level assets for a card (not per-orientation)."""
    upright_image: Path | None = None
    reversed_image: Path | None = None
    focus_upright: list[Path] = field(default_factory=list)
    focus_reversed: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class Card:
    """A single tarot card with all orientations."""
    name: str
    slug: str  # Filename-safe version: "Ace_of_Cups"
    arcana: ArcanaType
    suit: Suit | None  # None for Major/Modern
    rank: Rank | None  # None for Major/Modern
    directory: Path
    records: dict[Orientation, CardRecord]
    assets: CardLevelAssets

    def record(self, orientation: Orientation) -> CardRecord:
        """Get the reading data for a specific orientation."""
        if orientation not in self.records:
            raise KeyError(
                f"Card '{self.name}' has no record for orientation '{orientation.value}'. "
                f"Available: {[o.value for o in self.records]}"
            )
        return self.records[orientation]

    @property
    def orientations(self) -> list[Orientation]:
        """Return available orientations for this card."""
        return list(self.records.keys())


@dataclass
class DeckAssets:
    """Deck-level asset paths."""
    directory: Path
    back_image: Path | None = None
    front_image: Path | None = None
    music: Path | None = None
    narration: Path | None = None
    cut_animation: Path | None = None
    fan_animation: Path | None = None
    merge_animation: Path | None = None
    rotate_animation: Path | None = None


@dataclass
class Deck:
    """The full deck loaded from Deck.json + individual card JSONs."""
    name: str
    version: float
    cards: list[Card]
    assets: DeckAssets

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __getitem__(self, index: int) -> Card:
        return self.cards[index]

    def by_name(self, name: str) -> Card:
        """Look up a card by display name (case-insensitive, underscore-tolerant)."""
        normalized = name.replace("_", " ").strip().lower()
        for card in self.cards:
            if card.name.replace("_", " ").lower() == normalized:
                return card
        raise KeyError(f"Card not found: '{name}'")

    def by_slug(self, slug: str) -> Card:
        """Look up a card by its slug (filename-safe name)."""
        for card in self.cards:
            if card.slug == slug:
                return card
        raise KeyError(f"Card not found by slug: '{slug}'")

    def by_suit(self, suit: Suit) -> list[Card]:
        """Get all cards of a given suit."""
        return [c for c in self.cards if c.suit == suit]

    def by_arcana(self, arcana: ArcanaType) -> list[Card]:
        """Get all cards of a given arcana type."""
        return [c for c in self.cards if c.arcana == arcana]

    def minor_arcana(self) -> list[Card]:
        return self.by_arcana(ArcanaType.MINOR)

    def major_arcana(self) -> list[Card]:
        return self.by_arcana(ArcanaType.MAJOR)

    def modern(self) -> list[Card]:
        return self.by_arcana(ArcanaType.MODERN)
