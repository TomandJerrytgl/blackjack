"""Probability correctness, information isolation and worker lifecycle tests."""

from dataclasses import replace
import threading
import time
import unittest
from unittest import mock

import pygame

import game_stage as gs
import main
from probability import OddsService, OddsState, calculate_odds, draw_rank
from test_blackjack import make_round


class HiddenHand:
    def __init__(self, upcard):
        self.upcard = upcard

    def __getitem__(self, index):
        if index != 0:
            raise AssertionError("Real dealer hole card was read")
        return self.upcard

    def __iter__(self):
        raise AssertionError("Real dealer hand was iterated")


class ProbabilityTests(unittest.TestCase):
    def test_snapshot_never_reads_real_hole_or_remaining_deck(self):
        state = make_round((8, 8), (10, 6))
        state["peek_no_blackjack"] = True
        snapshot = gs.public_odds_state(state)
        state["dealer_hand"] = HiddenHand(state["dealer_hand"][0])
        state["deck"].cards = None
        self.assertEqual(gs.public_odds_state(state), snapshot)
        self.assertEqual(sum(snapshot.counts), 257)
        self.assertEqual(snapshot.counts[7], 18)
        self.assertEqual(snapshot.counts[9], 79)
        first = calculate_odds(snapshot, samples=300)
        self.assertEqual(calculate_odds(gs.public_odds_state(state), 300), first)

    def test_different_actual_holes_produce_identical_results(self):
        first = make_round((8, 8), (10, 6))
        second = make_round((8, 8), (10, 7))
        a = gs.public_odds_state(first)
        b = gs.public_odds_state(second)
        self.assertEqual(a, b)
        self.assertEqual(calculate_odds(a, 250), calculate_odds(b, 250))

    def test_exact_degenerate_probabilities_and_unavailable_actions(self):
        state = OddsState((0,) * 9 + (12,), (10, 10), 10,
                          False, False, False, False)
        result = calculate_odds(state, 200)
        self.assertEqual(result["Stand"]["Push"], 1)
        self.assertEqual(result["Hit"]["Lose"], 1)
        self.assertNotIn("Double", result)
        self.assertNotIn("Split", result)

    def test_negative_peek_conditions_unknown_hole_distribution(self):
        state = OddsState((0,) * 8 + (1, 8), (10, 10), 1,
                          True, False, False, False)
        result = calculate_odds(state, 500)
        self.assertEqual(result["Stand"]["Push"], 1)
        unconditioned = calculate_odds(replace(state, peek_no_blackjack=False), 4000)
        self.assertAlmostEqual(unconditioned["Stand"]["Lose"], 8 / 9, delta=0.035)

    def test_distribution_sums_and_split_sample_semantics(self):
        snapshot = gs.public_odds_state(make_round((8, 8)))
        results = calculate_odds(snapshot, 600)
        self.assertEqual(set(results), {"Stand", "Hit", "Double", "Split"})
        for action, result in results.items():
            self.assertAlmostEqual(sum(result[key] for key in ("Win", "Push", "Lose")), 1)
            self.assertEqual(result["samples"], 600)
            self.assertEqual(result["observations"], 1200 if action == "Split" else 600)

    def test_split_aces_are_not_natural_in_simulation(self):
        state = OddsState((0,) * 9 + (12,), (1, 1), 1,
                          False, False, True, True)
        result = calculate_odds(state, 100)
        self.assertEqual(result["Split"]["Lose"], 1)

    def test_weighted_draw_and_removal(self):
        import random

        rng = random.Random(1234)
        tens = sum(draw_rank([1] + [0] * 8 + [3], rng) == 10
                   for _ in range(8000))
        self.assertAlmostEqual(tens / 8000, 0.75, delta=0.025)
        counts = [1] + [0] * 9
        self.assertEqual(draw_rank(counts, rng), 1)
        self.assertEqual(sum(counts), 0)

    def test_worker_cache_and_cancellation(self):
        state = gs.public_odds_state(make_round((8, 8)))
        service = OddsService(samples=300)
        self.addCleanup(service.cancel)
        service.start(state)
        service._thread.join(timeout=5)
        self.assertFalse(service._thread.is_alive())
        original = service.snapshot()
        self.assertTrue(original["complete"])
        self.assertIsNone(original["error"])
        service.cancel()
        with mock.patch("probability.calculate_odds", side_effect=AssertionError("Cache miss")):
            service.start(state)
            self.assertEqual(service.snapshot(), original)
        token = threading.Event()
        token.set()
        self.assertIsNone(calculate_odds(state, 300, cancel=token))

    def test_cancelled_job_cannot_publish_over_new_job(self):
        first = gs.public_odds_state(make_round((8, 8)))
        second = replace(first, player=(10, 9), split_available=False)
        entered = threading.Event()
        release = threading.Event()

        def fake_calculate(state, samples, progress, cancel):
            if state == first:
                entered.set()
                release.wait(3)
                progress({"stale": {}})
                return {"stale": {}}
            return {"fresh": {}}

        service = OddsService()
        self.addCleanup(service.cancel)
        with mock.patch("probability.calculate_odds", side_effect=fake_calculate):
            service.start(first)
            self.assertTrue(entered.wait(2))
            old_thread = service._thread
            service.start(second)
            service._thread.join(2)
            release.set()
            old_thread.join(2)
        self.assertEqual(service.snapshot()["results"], {"fresh": {}})

    def test_live_calculation_keeps_event_loop_responsive(self):
        screen, _ = main.window_initial()
        self.addCleanup(pygame.quit)
        pygame.event.clear()
        state = make_round((8, 8))
        state["odds_service"] = OddsService(samples=12_000)
        self.addCleanup(gs.cancel_odds, state)
        pygame.event.post(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=(1440, 855)))
        gs.player_turn(screen, mock.Mock(), state)
        self.assertTrue(state["odds_open"])
        started = time.monotonic()
        for _ in range(10):
            gs.player_turn(screen, mock.Mock(), state)
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        gs.player_turn(screen, mock.Mock(), state)
        self.assertEqual(state["stage_name"], "quit")
        self.assertLess(time.monotonic() - started, 2)
        state["odds_service"]._thread.join(2)
        self.assertFalse(state["odds_service"]._thread.is_alive())


if __name__ == "__main__":
    unittest.main()
