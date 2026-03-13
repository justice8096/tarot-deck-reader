"""Tests for the deck loader against real card data."""

from pathlib import Path

import pytest

from tarot_deck_reader import (
    ArcanaType,
    Card,
    Deck,
    Orientation,
    Rank,
    Suit,
    load_deck,
)

DECK_JSON = Path("D:/data/cards/Standard/Deck.json")


@pytest.fixture(scope="module")
def deck() -> Deck:
    """Load the Standard deck once for all tests in this module."""
    return load_deck(DECK_JSON)


class TestDeckLoading:
    def test_deck_loads(self, deck: Deck) -> None:
        assert deck.name == "Standard"
        assert deck.version == 0.3

    def test_card_count(self, deck: Deck) -> None:
        # 56 Minor + 22 Major + 5 Modern = 83
        assert len(deck) >= 80  # at least 80 cards

    def test_deck_assets(self, deck: Deck) -> None:
        assert deck.assets.directory == Path("D:/data/cards/Standard")
        assert deck.assets.back_image is not None

    def test_iterable(self, deck: Deck) -> None:
        names = [c.name for c in deck]
        assert "Ace of Cups" in names
        assert "The Fool" in names


class TestCardClassification:
    def test_minor_arcana(self, deck: Deck) -> None:
        ace = deck.by_name("Ace of Cups")
        assert ace.arcana == ArcanaType.MINOR
        assert ace.suit == Suit.CUPS
        assert ace.rank == Rank.ACE

    def test_major_arcana(self, deck: Deck) -> None:
        fool = deck.by_name("The Fool")
        assert fool.arcana == ArcanaType.MAJOR
        assert fool.suit is None
        assert fool.rank is None

    def test_modern_card(self, deck: Deck) -> None:
        gig = deck.by_name("Gig Worker")
        assert gig.arcana == ArcanaType.MODERN
        assert gig.suit is None

    def test_hanged_man_underscore(self, deck: Deck) -> None:
        """The Hanged_Man has an underscore in Deck.json — lookup should still work."""
        hanged = deck.by_name("The Hanged Man")
        assert hanged.arcana == ArcanaType.MAJOR


class TestCardData:
    def test_orientations(self, deck: Deck) -> None:
        ace = deck.by_name("Ace of Cups")
        assert Orientation.UPRIGHT in ace.records
        assert Orientation.REVERSED in ace.records
        assert Orientation.BETWEEN in ace.records

    def test_record_content(self, deck: Deck) -> None:
        ace = deck.by_name("Ace of Cups")
        upright = ace.record(Orientation.UPRIGHT)
        assert len(upright.description) > 0
        assert len(upright.keywords) > 0
        assert len(upright.advice) > 0
        assert len(upright.affirmation) > 0

    def test_keywords_parsed(self, deck: Deck) -> None:
        """Keywords are stored as comma-separated in a single string; should be split."""
        ace = deck.by_name("Ace of Cups")
        upright = ace.record(Orientation.UPRIGHT)
        # Should be individual words, not one big comma-separated string
        assert all("," not in kw for kw in upright.keywords)
        assert len(upright.keywords) > 1

    def test_character_name(self, deck: Deck) -> None:
        ace = deck.by_name("Ace of Cups")
        upright = ace.record(Orientation.UPRIGHT)
        assert upright.character_name is not None

    def test_card_assets(self, deck: Deck) -> None:
        ace = deck.by_name("Ace of Cups")
        assert ace.assets.upright_image is not None
        assert ace.assets.reversed_image is not None

    def test_record_assets(self, deck: Deck) -> None:
        ace = deck.by_name("Ace of Cups")
        upright = ace.record(Orientation.UPRIGHT)
        assert upright.assets.image is not None
        assert upright.assets.card_image is not None


class TestFiltering:
    def test_by_suit(self, deck: Deck) -> None:
        cups = deck.by_suit(Suit.CUPS)
        assert len(cups) == 14  # Ace through King

    def test_minor_arcana_count(self, deck: Deck) -> None:
        minor = deck.minor_arcana()
        assert len(minor) == 55  # 4 suits * 14 - 1 (Ten of Wands absent from this deck)

    def test_major_arcana_count(self, deck: Deck) -> None:
        major = deck.major_arcana()
        assert len(major) == 22

    def test_modern_count(self, deck: Deck) -> None:
        modern = deck.modern()
        assert len(modern) == 5

    def test_by_name_case_insensitive(self, deck: Deck) -> None:
        card = deck.by_name("ace of cups")
        assert card.name == "Ace of Cups"

    def test_by_name_not_found(self, deck: Deck) -> None:
        with pytest.raises(KeyError):
            deck.by_name("Nonexistent Card")
