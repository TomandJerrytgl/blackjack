"""Blackjack rules and one-frame stage handlers.

Only frame_events drains the event queue. Stages transition by updating
stage_name and returning; none calls another stage.
"""

import pygame

from deck import GeneralDeck
import gui
import save_manager


DEAL_INTERVAL_MS = 500
RESHUFFLE_THRESHOLD = 104


def value_of_ranks(ranks):
    total = sum(ranks)
    return total + 10 if 1 in ranks and total + 10 <= 21 else total


def get_hand_value(deck, hand):
    return value_of_ranks([deck.card_value(card) for card in hand])


def check_bust(deck, hand):
    return get_hand_value(deck, hand) > 21


def is_natural(deck, cards, from_split=False):
    return (not from_split and len(cards) == 2
            and get_hand_value(deck, cards) == 21)


def dealer_should_hit(deck, cards):
    return get_hand_value(deck, cards) < 17


def new_hand(cards, bet, from_split=False):
    return {"cards": list(cards), "bet": bet, "from_split": from_split,
            "done": False, "result": None, "settled": False}


def new_game():
    deck = GeneralDeck(5)
    deck.create_deck()
    deck.shuffle()
    return {
        "stage_name": "main menu", "current_money": 1000,
        "deck": deck, "bet_amount": 0, "hands": [], "active_hand": 0,
        "dealer_hand": [], "exposed_cards": [], "hole_revealed": False,
        "split_used": False, "insurance_bet": 0,
        "insurance_settled": False, "peek_no_blackjack": False,
        "round_settled": False, "round_start_money": 1000,
        "stats": {"rounds": 0, "wins": 0}, "message": "",
        "game_result": None, "odds_open": False,
    }


def cancel_odds(state):
    service = state.get("odds_service")
    if service:
        service.cancel()
    state["odds_open"] = False


def prepare_bet(state):
    cancel_odds(state)
    state.update(bet_amount=0, hands=[], dealer_hand=[], active_hand=0,
                 split_used=False, insurance_bet=0, insurance_settled=False,
                 hole_revealed=False, peek_no_blackjack=False,
                 round_settled=False, game_result=None, message="")
    if len(state["deck"].cards) < RESHUFFLE_THRESHOLD:
        state["deck"].create_deck()
        state["deck"].shuffle()
        state["exposed_cards"] = []
        state["message"] = "New five-deck shoe shuffled."
    state["stage_name"] = "bet stage"


def change_bet(state, amount):
    if -state["bet_amount"] <= amount <= state["current_money"]:
        state["bet_amount"] += amount
        state["current_money"] -= amount


def begin_round(state):
    if state["bet_amount"] <= 0:
        state["message"] = "Place a bet first."
        return
    state["round_start_money"] = (state["current_money"]
                                  + state["bet_amount"])
    state["hands"] = [new_hand([], state["bet_amount"])]
    state["deal_index"] = 0
    state["next_deal_time"] = 0
    state["message"] = ""
    state["stage_name"] = "dealing stage"


def draw_visible(state, cards):
    card = state["deck"].draw_card()
    cards.append(card)
    state["exposed_cards"].append(card)


def reveal_hole(state):
    if not state["hole_revealed"] and len(state["dealer_hand"]) >= 2:
        state["exposed_cards"].append(state["dealer_hand"][1])
        state["hole_revealed"] = True


def resolve_opening(state, buy_insurance=False):
    deck = state["deck"]
    upcard = deck.card_value(state["dealer_hand"][0])
    amount = state["bet_amount"] / 2
    if buy_insurance:
        if upcard != 1 or state["current_money"] < amount:
            raise ValueError("Insurance unavailable")
        if state["insurance_settled"]:
            return
        state["current_money"] -= amount
        state["insurance_bet"] = amount
    dealer_natural = is_natural(deck, state["dealer_hand"])
    if not state["insurance_settled"]:
        if dealer_natural:
            state["current_money"] += 3 * state["insurance_bet"]
        state["insurance_settled"] = True
    state["peek_no_blackjack"] = upcard in (1, 10) and not dealer_natural
    if dealer_natural or is_natural(deck, state["hands"][0]["cards"]):
        reveal_hole(state)
        state["stage_name"] = "end stage"
    else:
        state["stage_name"] = "player turn"


def can_double(state):
    hand = state["hands"][state["active_hand"]]
    return (not hand["done"] and len(hand["cards"]) == 2
            and state["current_money"] >= hand["bet"])


def can_split(state):
    hand = state["hands"][state["active_hand"]]
    cards = hand["cards"]
    return (not state["split_used"] and not hand["done"]
            and len(cards) == 2 and (cards[0] - 1) % 13 == (cards[1] - 1) % 13
            and state["current_money"] >= hand["bet"])


def advance_hand(state):
    for index, hand in enumerate(state["hands"]):
        if not hand["done"]:
            state["active_hand"] = index
            return
    reveal_hole(state)
    state["next_deal_time"] = pygame.time.get_ticks() + DEAL_INTERVAL_MS
    if all(check_bust(state["deck"], h["cards"]) for h in state["hands"]):
        state["stage_name"] = "end stage"
    else:
        state["stage_name"] = "dealer turn"


def player_action(state, action):
    hand = state["hands"][state["active_hand"]]
    if hand["done"]:
        return
    if action == "double" and not can_double(state):
        return
    if action == "split" and not can_split(state):
        return
    cancel_odds(state)
    if action == "split":
        state["current_money"] -= hand["bet"]
        state["split_used"] = True
        state["hands"] = [new_hand([card], hand["bet"], True)
                          for card in hand["cards"]]
        split_aces = state["deck"].card_value(hand["cards"][0]) == 1
        for split_hand in state["hands"]:
            draw_visible(state, split_hand["cards"])
            split_hand["done"] = (split_aces or get_hand_value(
                state["deck"], split_hand["cards"]) == 21)
    elif action in ("hit", "double"):
        if action == "double":
            state["current_money"] -= hand["bet"]
            hand["bet"] *= 2
        draw_visible(state, hand["cards"])
        hand["done"] = (action == "double" or get_hand_value(
            state["deck"], hand["cards"]) >= 21)
    elif action == "stand":
        hand["done"] = True
    advance_hand(state)


def settle_round(state):
    if state["round_settled"]:
        return
    reveal_hole(state)
    deck = state["deck"]
    dealer_total = get_hand_value(deck, state["dealer_hand"])
    dealer_natural = is_natural(deck, state["dealer_hand"])
    for hand in state["hands"]:
        if hand["settled"]:
            continue
        total = get_hand_value(deck, hand["cards"])
        natural = is_natural(deck, hand["cards"], hand["from_split"])
        if total > 21:
            result, multiplier = "Lose", 0
        elif dealer_natural:
            result, multiplier = ("Push", 1) if natural else ("Lose", 0)
        elif natural:
            result, multiplier = "Blackjack", 2.5
        elif dealer_total > 21 or total > dealer_total:
            result, multiplier = "Win", 2
        elif total == dealer_total:
            result, multiplier = "Push", 1
        else:
            result, multiplier = "Lose", 0
        state["current_money"] += hand["bet"] * multiplier
        hand.update(result=result, settled=True, done=True)
    state["round_settled"] = True
    state["stats"]["rounds"] += 1
    profit = state["current_money"] - state["round_start_money"]
    state["stats"]["wins"] += int(profit > 0)
    state["game_result"] = " / ".join(h["result"] for h in state["hands"])
    state["message"] = f"Round net: ${profit:+g} (including insurance)"


def frame_events(state):
    events = pygame.event.get()
    if any(event.type == pygame.QUIT for event in events):
        cancel_odds(state)
        state["stage_name"] = "quit"
        return None
    return events


def finish_frame(clock):
    pygame.display.flip()
    clock.tick(60)


def clicked(events, buttons):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    return name
    return None


def status_text(state):
    stats = state["stats"]
    rate = f'{stats["wins"] / stats["rounds"]:.1%}' if stats["rounds"] else "--"
    return (f'Money: ${state["current_money"]:g}    '
            f'Rounds: {stats["rounds"]}    Wins: {stats["wins"]}    '
            f'Historical win rate: {rate}    Shoe: {len(state["deck"].cards)}')


def table(screen, state, title, actions):
    labels = []
    for index, hand in enumerate(state["hands"]):
        prefix = "> " if index == state["active_hand"] else ""
        total = get_hand_value(state["deck"], hand["cards"])
        result = hand["result"] or ("Done" if hand["done"] else "")
        labels.append(f'{prefix}Hand {index + 1}: {total} | '
                      f'Bet ${hand["bet"]:g} {result}')
    return gui.draw_table(screen, state, title, actions, labels, status_text(state))


def main_menu(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    buttons = gui.draw_menu(screen, "Welcome to Blackjack",
                            [("start", "Start"), ("quit", "Quit")])
    action = clicked(events, buttons)
    if action:
        stage_info["stage_name"] = "start menu" if action == "start" else "quit"
    finish_frame(clock)


def start_menu(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    buttons = gui.draw_menu(screen, "Blackjack",
                            [("new", "New Game"), ("load", "Load Game"),
                             ("back", "Back")])
    action = clicked(events, buttons)
    if action == "new":
        cancel_odds(stage_info)
        stage_info.clear()
        stage_info.update(new_game())
        prepare_bet(stage_info)
    elif action == "load":
        open_slots(stage_info, "load", "start menu")
    elif action == "back":
        stage_info["stage_name"] = "main menu"
    finish_frame(clock)


def open_slots(state, mode, return_stage):
    state.update(stage_name="slots", slot_mode=mode,
                 slot_return=return_stage, overwrite_slot=None,
                 slot_entries=save_manager.list_slots(), message="")


def slots_stage(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    mode = stage_info["slot_mode"]
    choices = [(str(i), entry) for i, entry in
               enumerate(stage_info["slot_entries"], 1)]
    if stage_info["overwrite_slot"]:
        choices = [("confirm", "Confirm overwrite"), ("cancel", "Cancel")]
    choices.append(("back", "Back"))
    buttons = gui.draw_menu(screen, f'{mode.title()} Game', choices,
                            stage_info["message"], wide=True)
    action = clicked(events, buttons)
    try:
        if action == "back":
            stage_info["stage_name"] = stage_info["slot_return"]
        elif action == "cancel":
            stage_info["overwrite_slot"] = None
        elif action == "confirm":
            save_manager.save_game(stage_info, stage_info["overwrite_slot"])
            stage_info["overwrite_slot"] = None
            stage_info["slot_entries"] = save_manager.list_slots()
            stage_info["message"] = "Game saved."
        elif action and action.isdigit():
            slot = int(action)
            if mode == "load":
                loaded = save_manager.load_game(slot)
                cancel_odds(stage_info)
                stage_info.clear()
                stage_info.update(new_game())
                stage_info.update(loaded)
                prepare_bet(stage_info)
            elif save_manager.slot_path(slot).exists():
                stage_info["overwrite_slot"] = slot
                stage_info["message"] = f"Overwrite slot {slot}?"
            else:
                save_manager.save_game(stage_info, slot)
                stage_info["slot_entries"] = save_manager.list_slots()
                stage_info["message"] = "Game saved."
    except (OSError, ValueError) as error:
        stage_info["message"] = f"Save/load failed: {error}"
    finish_frame(clock)


def bet_stage(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    actions = [("deal", "Deal", True), ("save", "Save Game", True),
               ("menu", "Back to Menu", True), ("quit", "Quit", True)]
    buttons = table(screen, stage_info,
                    f'Current Bet: ${stage_info["bet_amount"]:g}', actions)
    chip_rects = gui.draw_chips(screen, gui.CHIPS)
    action = clicked(events, buttons)
    if action == "deal":
        begin_round(stage_info)
    elif action == "save":
        change_bet(stage_info, -stage_info["bet_amount"])
        open_slots(stage_info, "save", "bet stage")
    elif action == "menu":
        change_bet(stage_info, -stage_info["bet_amount"])
        stage_info["stage_name"] = "main menu"
    elif action == "quit":
        stage_info["stage_name"] = "quit"
    else:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                for value, rect in chip_rects.items():
                    if rect.collidepoint(event.pos):
                        change_bet(stage_info, value if event.button == 1 else -value)
    if stage_info["current_money"] + stage_info["bet_amount"] < 1:
        stage_info["message"] = "Insufficient funds. Load a save or start a new game."
    finish_frame(clock)


def dealing_stage(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    now = pygame.time.get_ticks()
    if now >= stage_info["next_deal_time"]:
        index = stage_info["deal_index"]
        if index in (0, 2):
            draw_visible(stage_info, stage_info["hands"][0]["cards"])
        elif index == 1:
            draw_visible(stage_info, stage_info["dealer_hand"])
        else:
            stage_info["dealer_hand"].append(stage_info["deck"].draw_card())
        stage_info["deal_index"] += 1
        stage_info["next_deal_time"] = now + DEAL_INTERVAL_MS
        if stage_info["deal_index"] == 4:
            if stage_info["deck"].card_value(stage_info["dealer_hand"][0]) == 1:
                stage_info["stage_name"] = "insurance"
            else:
                resolve_opening(stage_info)
    table(screen, stage_info, "Dealing Cards...", [])
    finish_frame(clock)


def insurance_stage(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    cost = stage_info["bet_amount"] / 2
    allowed = stage_info["current_money"] >= cost
    buttons = table(screen, stage_info, f"Insurance: ${cost:g}?",
                    [("yes", "Insurance", allowed), ("no", "No Insurance", True)])
    action = clicked(events, buttons)
    if action == "no" or (action == "yes" and allowed):
        resolve_opening(stage_info, action == "yes")
    finish_frame(clock)


def public_odds_state(state):
    from probability import OddsState

    counts = [4 * state["deck"].deck_number] * 9
    counts.append(16 * state["deck"].deck_number)
    for card in state["exposed_cards"]:
        counts[GeneralDeck.card_value(card) - 1] -= 1
    hand = state["hands"][state["active_hand"]]
    return OddsState(tuple(counts), tuple(GeneralDeck.card_value(c)
                                        for c in hand["cards"]),
                     GeneralDeck.card_value(state["dealer_hand"][0]),
                     state["peek_no_blackjack"], hand["from_split"],
                     can_double(state), can_split(state),
                     tuple(tuple(GeneralDeck.card_value(c) for c in h["cards"])
                           for h in state["hands"][state["active_hand"] + 1:]
                           if not h["done"]))


def player_turn(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    buttons = table(screen, stage_info, "Your Turn",
                    [("hit", "Hit", True), ("stand", "Stand", True),
                     ("double", "Double", can_double(stage_info)),
                     ("split", "Split", can_split(stage_info)),
                     ("odds", "Show Odds", True)])
    if stage_info["odds_open"]:
        service = stage_info["odds_service"]
        close = gui.draw_odds(screen, service.snapshot(),
                              public_odds_state(stage_info).counts)
        if clicked(events, {"close": close}):
            stage_info["odds_open"] = False
    else:
        action = clicked(events, buttons)
        if action == "odds":
            from probability import OddsService

            if "odds_service" not in stage_info:
                stage_info["odds_service"] = OddsService()
            stage_info["odds_service"].start(public_odds_state(stage_info))
            stage_info["odds_open"] = True
        elif action:
            player_action(stage_info, action)
    finish_frame(clock)


def dealer_turn(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    cards = stage_info["dealer_hand"]
    if dealer_should_hit(stage_info["deck"], cards):
        now = pygame.time.get_ticks()
        if now >= stage_info["next_deal_time"]:
            draw_visible(stage_info, cards)
            stage_info["next_deal_time"] = now + DEAL_INTERVAL_MS
    if not dealer_should_hit(stage_info["deck"], cards):
        stage_info["stage_name"] = "end stage"
    total = get_hand_value(stage_info["deck"], cards)
    table(screen, stage_info, f"Dealer: {total}", [])
    finish_frame(clock)


def end_stage(screen, clock, stage_info):
    events = frame_events(stage_info)
    if events is None:
        return
    settle_round(stage_info)
    buttons = table(screen, stage_info, stage_info["game_result"],
                    [("next", "Next Round", True),
                     ("save", "Save Game", True), ("menu", "Menu", True)])
    action = clicked(events, buttons)
    if action == "next":
        prepare_bet(stage_info)
    elif action == "save":
        open_slots(stage_info, "save", "end stage")
    elif action == "menu":
        stage_info["stage_name"] = "main menu"
    finish_frame(clock)
