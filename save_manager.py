"""Five versioned, validated JSON save slots; no executable serialization."""

from datetime import datetime
import json
import math
from pathlib import Path

from deck import GeneralDeck


SAVE_DIR = Path(__file__).resolve().parent / "saves"
SAVE_VERSION = 1
SLOT_COUNT = 5


def slot_path(slot):
    if type(slot) is not int or not 1 <= slot <= SLOT_COUNT:
        raise ValueError("Slot must be between 1 and 5")
    return SAVE_DIR / f"slot_{slot}.json"


def validate_save(data):
    if (not isinstance(data, dict) or type(data.get("version")) is not int
            or data["version"] != SAVE_VERSION):
        raise ValueError("Unsupported save version")
    if type(data.get("deck_number")) is not int or data["deck_number"] != 5:
        raise ValueError("Save requires a five-deck shoe")
    money = data.get("current_money")
    try:
        finite_money = type(money) in (int, float) and math.isfinite(money)
    except OverflowError:
        finite_money = False
    if (not finite_money
            or money < 0 or money % 0.5 != 0):
        raise ValueError("Invalid balance")
    stats = data.get("stats")
    if (not isinstance(stats, dict)
            or any(type(stats.get(key)) is not int for key in ("rounds", "wins"))
            or not 0 <= stats["wins"] <= stats["rounds"]):
        raise ValueError("Invalid statistics")
    cards = data.get("cards")
    exposed = data.get("exposed_cards")
    if (not isinstance(cards, list) or not isinstance(exposed, list)
            or any(type(card) is not int for card in cards + exposed)
            or len(cards) + len(exposed) != 260
            or set(cards + exposed) != set(range(1, 261))):
        raise ValueError("Invalid shoe or public card history")
    timestamp = data.get("saved_at")
    if not isinstance(timestamp, str):
        raise ValueError("Invalid save timestamp")
    try:
        datetime.fromisoformat(timestamp)
    except ValueError as error:
        raise ValueError("Invalid save timestamp") from error
    return data


def read_save(slot):
    path = slot_path(slot)
    if path.stat().st_size > 100_000:
        raise ValueError("Save file is too large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("Damaged save file") from error
    return validate_save(data)


def save_game(state, slot):
    path = slot_path(slot)
    stage = state["stage_name"]
    if stage == "slots":
        stage = state["slot_return"]
    if not ((stage == "bet stage" and state["bet_amount"] == 0)
            or (stage == "end stage" and state["round_settled"])):
        raise ValueError("Save is only available between rounds")
    data = {
        "version": SAVE_VERSION,
        "saved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "deck_number": state["deck"].deck_number,
        "cards": list(state["deck"].cards),
        "exposed_cards": list(state["exposed_cards"]),
        "current_money": state["current_money"],
        "stats": dict(state["stats"]),
    }
    validate_save(data)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    try:
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def load_game(slot):
    data = read_save(slot)
    deck = GeneralDeck(data["deck_number"])
    deck.cards = list(data["cards"])
    return {"deck": deck, "exposed_cards": list(data["exposed_cards"]),
            "current_money": data["current_money"], "stats": dict(data["stats"])}


def list_slots():
    entries = []
    for slot in range(1, SLOT_COUNT + 1):
        try:
            data = read_save(slot)
            timestamp = datetime.fromisoformat(data["saved_at"]).strftime(
                "%Y-%m-%d %H:%M:%S")
            entries.append(f'Slot {slot} | ${data["current_money"]:g} | '
                           f'{data["stats"]["rounds"]} rounds | {timestamp}')
        except FileNotFoundError:
            entries.append(f"Slot {slot} | Empty")
        except (OSError, ValueError):
            entries.append(f"Slot {slot} | Damaged or incompatible")
    return entries
