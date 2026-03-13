"""Deck and card JSON loading."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .classifier import classify_card
from .enums import Orientation
from .exceptions import CardLoadError, DeckLoadError
from .models import (
    Card,
    CardAssets,
    CardLevelAssets,
    CardRecord,
    Deck,
    DeckAssets,
)


def _resolve_path(directory: Path, filename: str | None) -> Path | None:
    """Resolve a filename against a directory, returning None if filename is empty."""
    if not filename:
        return None
    return directory / filename


def _resolve_paths(directory: Path, filenames: list[str]) -> list[Path]:
    """Resolve a list of filenames against a directory."""
    return [directory / f for f in filenames if f]


def _parse_keywords(raw_keywords: list[str]) -> list[str]:
    """Parse keywords — they may be comma-separated within a single string."""
    result: list[str] = []
    for item in raw_keywords:
        for kw in item.split(","):
            stripped = kw.strip()
            if stripped:
                result.append(stripped)
    return result


def _load_record(raw: dict[str, Any], directory: Path) -> CardRecord:
    """Parse a single orientation record from card JSON."""
    orientation = Orientation(raw["Orientation"])

    raw_assets = raw.get("Assets", {})
    assets = CardAssets(
        image=_resolve_path(directory, raw_assets.get("Image")),
        card_image=_resolve_path(directory, raw_assets.get("CardImage")),
        narration=_resolve_path(directory, raw_assets.get("Narration")),
        music=_resolve_path(directory, raw_assets.get("Music")),
        movie=_resolve_path(directory, raw_assets.get("Movie")),
        palette_image=_resolve_path(directory, raw_assets.get("PalletImage")),
        object_3d=_resolve_path(directory, raw_assets.get("Object")),
        card_image_upright=_resolve_path(directory, raw_assets.get("CardImageUpright")),
        focus_stills=_resolve_paths(
            directory,
            raw_assets.get("FocusUprightT", []) + raw_assets.get("FocusReversedT", []),
        ),
    )

    raw_prompts = raw.get("Prompts", {})
    character_name = raw_prompts.get("CharacterImage", {}).get("CharacterName")

    return CardRecord(
        orientation=orientation,
        description=raw.get("Description", ""),
        meanings=raw.get("Meanings", []),
        keywords=_parse_keywords(raw.get("Keywords", [])),
        advice=raw.get("Advice", ""),
        affirmation=raw.get("Affirmation", ""),
        categories=raw.get("Category", []),
        assets=assets,
        character_name=character_name,
    )


def _load_card_json(card_path: Path) -> Card:
    """Load a single card from its JSON file."""
    try:
        raw = json.loads(card_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise CardLoadError(f"Failed to load card JSON '{card_path}': {e}") from e

    # Card JSONs use "data.Cards" as a literal key (n8n Extract from File format)
    card_data = raw.get("data.Cards")
    if card_data is None:
        raise CardLoadError(
            f"Card JSON '{card_path}' missing 'data.Cards' key. "
            f"Available keys: {list(raw.keys())}"
        )

    name: str = card_data["Card"]
    slug = card_path.stem  # e.g., "Ace_of_Cups"
    directory = Path(card_data.get("Directory", str(card_path.parent)))

    # Classify by name
    arcana, suit, rank = classify_card(name)

    # Parse top-level card assets
    raw_assets = card_data.get("Assets", {})
    card_level_assets = CardLevelAssets(
        upright_image=_resolve_path(directory, raw_assets.get("UprightImage")),
        reversed_image=_resolve_path(directory, raw_assets.get("ReversedImage")),
        focus_upright=_resolve_paths(directory, raw_assets.get("FocusUpright", [])),
        focus_reversed=_resolve_paths(directory, raw_assets.get("FocusReversed", [])),
    )

    # Parse orientation records
    records: dict[Orientation, CardRecord] = {}
    for raw_record in card_data.get("records", []):
        record = _load_record(raw_record, directory)
        records[record.orientation] = record

    return Card(
        name=name,
        slug=slug,
        arcana=arcana,
        suit=suit,
        rank=rank,
        directory=directory,
        records=records,
        assets=card_level_assets,
    )


def _parse_deck_assets(raw_assets: dict[str, Any]) -> DeckAssets:
    """Parse deck-level assets section."""
    directory = Path(raw_assets.get("Directory", "."))
    return DeckAssets(
        directory=directory,
        back_image=_resolve_path(directory, None) if not raw_assets.get("BackImage") else Path(raw_assets["BackImage"]),
        front_image=Path(raw_assets["FrontImage"]) if raw_assets.get("FrontImage") else None,
        music=Path(raw_assets["Music"]) if raw_assets.get("Music") else None,
        narration=Path(raw_assets["Narration"]) if raw_assets.get("Narration") else None,
        cut_animation=Path(raw_assets["Cut"]) if raw_assets.get("Cut") else None,
        fan_animation=Path(raw_assets["Fan"]) if raw_assets.get("Fan") else None,
        merge_animation=Path(raw_assets["Merge"]) if raw_assets.get("Merge") else None,
        rotate_animation=Path(raw_assets["Rotate"]) if raw_assets.get("Rotate") else None,
    )


def load_deck(deck_json_path: str | Path) -> Deck:
    """Load a full deck from a Deck.json file.

    This reads the master Deck.json, then loads each individual card JSON
    referenced in the Cards array.

    Args:
        deck_json_path: Path to the Deck.json file.

    Returns:
        A fully-loaded Deck instance.

    Raises:
        DeckLoadError: If the deck JSON is invalid or cannot be read.
        CardLoadError: If any individual card JSON fails to load.
    """
    deck_path = Path(deck_json_path)

    try:
        raw = json.loads(deck_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise DeckLoadError(f"Failed to load deck JSON '{deck_path}': {e}") from e

    name = raw.get("Name", "Unknown")
    version = raw.get("Version", 0.0)

    # Parse deck-level assets
    assets = _parse_deck_assets(raw.get("Assets", {}))

    # Load each card
    cards_list = raw.get("Cards", [])
    if not cards_list:
        raise DeckLoadError(
            f"Deck JSON '{deck_path}' has no Cards array or it is empty."
        )

    cards: list[Card] = []
    for entry in cards_list:
        card_file = entry.get("File")
        if not card_file:
            raise DeckLoadError(
                f"Card entry missing 'File' key: {entry}"
            )
        card_path = deck_path.parent / card_file
        card = _load_card_json(card_path)
        cards.append(card)

    return Deck(
        name=name,
        version=version,
        cards=cards,
        assets=assets,
    )
