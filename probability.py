"""Reproducible Monte Carlo from a public-information snapshot only.

No live deck, dealer hand, or game state enters this module. Hit and Split
continue by hitting below 17 and standing on all 17s, with no later doubles.
"""

from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import random
import threading
import time

from game_stage import value_of_ranks


DEFAULT_SAMPLES = 12_000
BATCH_SIZE = 200


@dataclass(frozen=True)
class OddsState:
    counts: tuple
    player: tuple
    upcard: int
    peek_no_blackjack: bool
    from_split: bool
    double_available: bool
    split_available: bool
    future_hands: tuple = ()


def available_actions(state):
    actions = ["Stand", "Hit"]
    if state.double_available:
        actions.append("Double")
    if state.split_available:
        actions.append("Split")
    return actions


def draw_rank(counts, rng, excluded=None):
    total = sum(counts) - (counts[excluded - 1] if excluded else 0)
    if total <= 0:
        raise ValueError("No cards consistent with the public information")
    pick = rng.randrange(total)
    for index, count in enumerate(counts):
        if index + 1 == excluded:
            continue
        if pick < count:
            counts[index] -= 1
            return index + 1
        pick -= count
    raise AssertionError("Invalid rank counts")


def continue_hand(cards, counts, rng):
    while value_of_ranks(cards) < 17:
        cards.append(draw_rank(counts, rng))


def outcome(player, dealer, from_split):
    player_total = value_of_ranks(player)
    dealer_total = value_of_ranks(dealer)
    player_natural = len(player) == 2 and player_total == 21 and not from_split
    dealer_natural = len(dealer) == 2 and dealer_total == 21
    if player_total > 21:
        return "Lose"
    if dealer_natural:
        return "Push" if player_natural else "Lose"
    if player_natural or dealer_total > 21 or player_total > dealer_total:
        return "Win"
    return "Push" if player_total == dealer_total else "Lose"


def simulate_once(state, action, rng):
    counts = list(state.counts)
    excluded = None
    if state.peek_no_blackjack:
        excluded = 10 if state.upcard == 1 else 1 if state.upcard == 10 else None
    hole = draw_rank(counts, rng, excluded)
    dealer = [state.upcard, hole]
    if action == "Split":
        hands = [[state.player[0]], [state.player[1]]]
        # Match real dealing order: give both hands one card before playing.
        for hand in hands:
            hand.append(draw_rank(counts, rng))
        if state.player[0] != 1:
            for hand in hands:
                continue_hand(hand, counts, rng)
    else:
        hands = [list(state.player)]
        if action in ("Hit", "Double"):
            hands[0].append(draw_rank(counts, rng))
        if action == "Hit":
            continue_hand(hands[0], counts, rng)
    # Other unfinished split hands consume cards before the dealer plays.
    for pending in state.future_hands:
        continue_hand(list(pending), counts, rng)
    continue_hand(dealer, counts, rng)
    return [outcome(hand, dealer, state.from_split or action == "Split")
            for hand in hands]


def calculate_odds(state, samples=DEFAULT_SAMPLES, progress=None, cancel=None):
    if type(samples) is not int or samples < 1:
        raise ValueError("samples must be a positive integer")
    if (len(state.counts) != 10
            or any(type(n) is not int or n < 0 for n in state.counts)):
        raise ValueError("Invalid public card counts")
    actions = available_actions(state)
    totals = {action: {"Win": 0, "Push": 0, "Lose": 0} for action in actions}
    generators = {}
    for action in actions:
        digest = hashlib.sha256(repr((state, action)).encode("utf-8")).digest()
        generators[action] = random.Random(int.from_bytes(digest[:16], "big"))
    result = None
    for start in range(0, samples, BATCH_SIZE):
        stop = min(start + BATCH_SIZE, samples)
        for _ in range(start, stop):
            if cancel and cancel.is_set():
                return None
            for action in actions:
                for result_name in simulate_once(state, action, generators[action]):
                    totals[action][result_name] += 1
        result = {}
        for action, counts in totals.items():
            observations = sum(counts.values())
            result[action] = {key: value / observations
                              for key, value in counts.items()}
            result[action].update(samples=stop, observations=observations)
        if progress:
            progress(result)
        if cancel:
            # Yield between bounded batches; the worker never calls Pygame.
            time.sleep(0.001)
    return result


class OddsService:
    """One cancellable daemon job, bounded completed-state cache."""

    def __init__(self, samples=DEFAULT_SAMPLES):
        self.samples = samples
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._key = None
        self._cache = OrderedDict()
        self._view = {"results": {}, "complete": False, "error": None}
        self._thread = None

    def cancel(self):
        self._cancel.set()

    def start(self, state):
        if self._key == state and not self._cancel.is_set():
            return
        self.cancel()
        token = threading.Event()
        with self._lock:
            self._cancel = token
            self._key = state
            if state in self._cache:
                self._view = {"results": deepcopy(self._cache[state]),
                              "complete": True, "error": None,
                              "available": available_actions(state)}
                self._cache.move_to_end(state)
                return
            self._view = {"results": {}, "complete": False, "error": None,
                          "available": available_actions(state)}
        self._thread = threading.Thread(target=self._run, args=(state, token),
                                        daemon=True, name="blackjack-odds")
        self._thread.start()

    def _run(self, state, token):
        def publish(results):
            with self._lock:
                if self._cancel is token and not token.is_set():
                    self._view["results"] = deepcopy(results)

        try:
            results = calculate_odds(state, self.samples, publish, token)
            with self._lock:
                if results is not None and self._cancel is token and not token.is_set():
                    self._cache[state] = results
                    if len(self._cache) > 32:
                        self._cache.popitem(last=False)
                    self._view.update(results=results, complete=True)
        except Exception as error:
            with self._lock:
                if self._cancel is token and not token.is_set():
                    self._view.update(error=str(error), complete=True)

    def snapshot(self):
        with self._lock:
            return deepcopy(self._view)
