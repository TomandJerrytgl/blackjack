"""Behavior and headless Pygame regression tests."""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import pygame

from deck import GeneralDeck
import game_stage as gs
import main
import save_manager


def make_round(player=(10, 9), dealer=(10, 8), bet=100):
    state = gs.new_game()
    gs.prepare_bet(state)
    gs.change_bet(state, bet)
    gs.begin_round(state)
    used = {}

    def cards(ranks):
        result = []
        for rank in ranks:
            card = rank + used.get(rank, 0) * 13
            used[rank] = used.get(rank, 0) + 1
            state["deck"].cards.remove(card)
            result.append(card)
        return result

    state["hands"][0]["cards"] = cards(player)
    state["dealer_hand"] = cards(dealer)
    state["exposed_cards"] = (state["hands"][0]["cards"][:]
                              + state["dealer_hand"][:1])
    state["stage_name"] = "player turn"
    return state


def rig_draws(state, ranks):
    """Move available cards of requested ranks to the top without changing IDs."""
    cards = state["deck"].cards
    selected = []
    for rank in ranks:
        card = next(card for card in cards if (card - 1) % 13 + 1 == rank)
        cards.remove(card)
        selected.append(card)
    cards.extend(reversed(selected))


class RuleTests(unittest.TestCase):
    def test_multiple_aces(self):
        for ranks, expected in [((1, 1), 12), ((1, 1, 9), 21),
                                ((1, 1, 9, 10), 21), ((1, 1, 1, 8), 21),
                                ((1, 1, 1, 10, 10), 23)]:
            with self.subTest(ranks=ranks):
                self.assertEqual(gs.value_of_ranks(ranks), expected)

    def test_bust_and_natural(self):
        deck = GeneralDeck()
        self.assertTrue(gs.check_bust(deck, [10, 23, 5]))
        self.assertFalse(gs.check_bust(deck, [1, 10, 23]))
        self.assertTrue(gs.is_natural(deck, [1, 13]))
        self.assertFalse(gs.is_natural(deck, [1, 5, 15]))
        self.assertFalse(gs.is_natural(deck, [1, 13], from_split=True))

    def test_soft_17_stands(self):
        deck = GeneralDeck()
        self.assertFalse(gs.dealer_should_hit(deck, [1, 6]))
        self.assertFalse(gs.dealer_should_hit(deck, [1, 14, 5]))
        self.assertTrue(gs.dealer_should_hit(deck, [1, 5]))
        self.assertTrue(gs.dealer_should_hit(deck, [10, 6]))

    def test_end_stage_payout_for_dealer_win(self):
        state = make_round((10, 7), (10, 9))
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 900)
        self.assertEqual(state["hands"][0]["result"], "Lose")

    def test_end_stage_payout_for_player_win(self):
        state = make_round()
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 1100)
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 1100)
        self.assertEqual(state["stats"], {"rounds": 1, "wins": 1})

    def test_push_and_blackjack_payouts(self):
        for player, dealer, bet, money in [
                ((10, 9), (10, 9), 100, 1000),
                ((1, 13), (10, 9), 100, 1150),
                ((1, 13), (10, 9), 1, 1001.5),
                ((1, 13), (1, 10), 100, 1000),
                ((7, 7, 7), (1, 10), 100, 900)]:
            with self.subTest(player=player, dealer=dealer):
                state = make_round(player, dealer, bet)
                gs.settle_round(state)
                self.assertEqual(state["current_money"], money)

    def test_opening_peek_and_natural(self):
        for upcard in (10, 11, 12, 13):
            state = make_round((10, 9), (upcard, 1))
            gs.resolve_opening(state)
            self.assertEqual(state["stage_name"], "end stage")
        state = make_round((1, 10), (9, 8))
        gs.resolve_opening(state)
        self.assertEqual(state["stage_name"], "end stage")
        state = make_round((10, 9), (10, 7))
        gs.resolve_opening(state)
        self.assertTrue(state["peek_no_blackjack"])
        self.assertEqual(state["stage_name"], "player turn")

    def test_insurance_win_loss_and_no_duplicate_payment(self):
        state = make_round((10, 9), (1, 10))
        gs.resolve_opening(state, True)
        self.assertEqual(state["current_money"], 1000)
        gs.resolve_opening(state, True)
        self.assertEqual(state["current_money"], 1000)
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 1000)
        self.assertEqual(state["stats"], {"rounds": 1, "wins": 0})
        state = make_round((10, 9), (1, 8))
        gs.resolve_opening(state, True)
        self.assertEqual(state["current_money"], 850)
        self.assertTrue(state["peek_no_blackjack"])
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 950)
        state = make_round((10, 9), (1, 10), 1000)
        with self.assertRaises(ValueError):
            gs.resolve_opening(state, True)
        self.assertEqual(state["current_money"], 0)

    def test_double_cost_one_card_and_forced_stand(self):
        state = make_round((5, 6), (10, 8))
        rig_draws(state, [10])
        gs.player_action(state, "double")
        self.assertEqual(state["current_money"], 800)
        self.assertEqual(state["hands"][0]["bet"], 200)
        self.assertEqual(len(state["hands"][0]["cards"]), 3)
        self.assertTrue(state["hands"][0]["done"])
        self.assertEqual(state["stage_name"], "dealer turn")
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 1200)

    def test_double_unavailable_after_hit_or_without_money(self):
        state = make_round((2, 3, 4))
        self.assertFalse(gs.can_double(state))
        state = make_round((5, 6), bet=600)
        self.assertFalse(gs.can_double(state))
        gs.player_action(state, "double")
        self.assertEqual(state["current_money"], 400)
        self.assertEqual(len(state["hands"][0]["cards"]), 2)

    def test_bust_immediately_ends_single_hand(self):
        state = make_round()
        rig_draws(state, [10])
        before = len(state["deck"].cards)
        gs.player_action(state, "hit")
        self.assertEqual(state["stage_name"], "end stage")
        self.assertEqual(len(state["deck"].cards), before - 1)
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 900)

    def test_split_cost_independent_actions_and_settlement(self):
        state = make_round((8, 8), (10, 8))
        rig_draws(state, [10, 2, 10])
        gs.player_action(state, "split")
        self.assertEqual(state["current_money"], 800)
        self.assertEqual(len(state["hands"]), 2)
        self.assertFalse(gs.can_split(state))
        gs.player_action(state, "stand")
        self.assertEqual(state["active_hand"], 1)
        self.assertEqual(state["stage_name"], "player turn")
        gs.player_action(state, "double")
        self.assertEqual(state["current_money"], 700)
        self.assertEqual(state["stage_name"], "dealer turn")
        gs.settle_round(state)
        self.assertEqual([h["result"] for h in state["hands"]], ["Push", "Win"])
        self.assertEqual(state["current_money"], 1200)
        self.assertEqual(state["stats"], {"rounds": 1, "wins": 1})

    def test_split_requires_same_rank_and_funds(self):
        self.assertFalse(gs.can_split(make_round((10, 11))))
        self.assertFalse(gs.can_split(make_round((8, 8), bet=600)))
        self.assertFalse(gs.can_split(make_round((8, 8, 8))))
        self.assertTrue(gs.can_split(make_round((12, 12))))

    def test_split_aces_one_card_no_natural(self):
        state = make_round((1, 1), (10, 9))
        rig_draws(state, [10, 13])
        gs.player_action(state, "split")
        self.assertTrue(all(h["done"] for h in state["hands"]))
        self.assertFalse(gs.can_double(state))
        self.assertEqual(state["stage_name"], "dealer turn")
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 1200)
        self.assertEqual([h["result"] for h in state["hands"]], ["Win", "Win"])

    def test_split_bust_continues_other_hand(self):
        state = make_round((8, 8))
        rig_draws(state, [10, 9, 10])
        gs.player_action(state, "split")
        gs.player_action(state, "hit")
        self.assertEqual(state["active_hand"], 1)
        self.assertEqual(state["stage_name"], "player turn")
        gs.player_action(state, "stand")
        gs.settle_round(state)
        self.assertEqual(state["current_money"], 800)

    def test_shuffle_threshold_and_next_round_cleanup(self):
        state = gs.new_game()
        state["deck"].cards = list(range(1, 105))
        state["exposed_cards"] = list(range(105, 261))
        gs.prepare_bet(state)
        self.assertEqual(len(state["deck"].cards), 104)
        state["exposed_cards"].append(state["deck"].draw_card())
        gs.prepare_bet(state)
        self.assertEqual(len(state["deck"].cards), 260)
        self.assertEqual(state["exposed_cards"], [])
        self.assertEqual(state["current_money"], 1000)
        self.assertEqual(state["hands"], [])

    def test_bet_cannot_overdraw_and_can_cancel(self):
        state = gs.new_game()
        gs.prepare_bet(state)
        gs.change_bet(state, 1001)
        self.assertEqual(state["bet_amount"], 0)
        gs.change_bet(state, 100)
        gs.change_bet(state, -100)
        self.assertEqual(state["current_money"], 1000)


class SaveTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.patch = mock.patch.object(save_manager, "SAVE_DIR", Path(self.directory.name))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_roundtrip_preserves_shoe_money_public_history_and_stats(self):
        state = make_round((1, 10), (10, 9))
        gs.settle_round(state)
        state["stage_name"] = "end stage"
        save_manager.save_game(state, 1)
        restored = save_manager.load_game(1)
        self.assertEqual(restored["deck"].cards, state["deck"].cards)
        self.assertEqual(restored["current_money"], 1150)
        self.assertEqual(restored["exposed_cards"], state["exposed_cards"])
        self.assertEqual(restored["stats"], {"rounds": 1, "wins": 1})
        fresh = gs.new_game()
        fresh.update(restored)
        gs.prepare_bet(fresh)
        self.assertEqual(fresh["current_money"], 1150)
        self.assertEqual(fresh["stage_name"], "bet stage")

    def test_five_slots_and_midround_rejection(self):
        state = gs.new_game()
        gs.prepare_bet(state)
        for slot in range(1, 6):
            save_manager.save_game(state, slot)
        self.assertEqual(len(save_manager.list_slots()), 5)
        for slot in (0, 6, True):
            with self.assertRaises(ValueError):
                save_manager.save_game(state, slot)
        with self.assertRaises(ValueError):
            save_manager.save_game(make_round(), 1)
        self.assertEqual(len(list(Path(self.directory.name).glob("*.json"))), 5)

    def test_corrupt_save_rejected_without_overwrite(self):
        path = save_manager.slot_path(1)
        path.write_text('{"version": 999}', encoding="utf-8")
        with self.assertRaises(ValueError):
            save_manager.load_game(1)
        self.assertIn("Damaged", save_manager.list_slots()[0])
        state = gs.new_game()
        gs.prepare_bet(state)
        save_manager.save_game(state, 1)
        original = json.loads(path.read_text())
        for key, value in [("current_money", float("nan")), ("cards", [1] * 260),
                           ("stats", {"rounds": 1, "wins": 2})]:
            broken = dict(original)
            broken[key] = value
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(ValueError):
                save_manager.load_game(1)


class PygameFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.screen, _ = main.window_initial()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        pygame.event.clear()
        self.clock = mock.Mock()

    def frame(self, state, position=None):
        if position:
            pygame.event.post(pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=position))
        main.run_game_stage(self.screen, self.clock, state)

    def test_menu_to_next_round_real_rendering(self):
        state = gs.new_game()
        self.frame(state, (800, 260))
        self.assertEqual(state["stage_name"], "start menu")
        self.frame(state, (800, 260))
        self.assertEqual(state["stage_name"], "bet stage")
        rig_draws(state, [10, 10, 9, 8])
        self.frame(state, (960, 720))
        self.assertEqual(state["bet_amount"], 100)
        self.frame(state, (200, 855))
        self.assertEqual(state["stage_name"], "dealing stage")
        with mock.patch.object(pygame.time, "get_ticks", side_effect=[0, 500, 1000, 1500]):
            for _ in range(4):
                self.frame(state)
        self.assertEqual(state["stage_name"], "player turn")
        self.frame(state, (480, 855))
        self.assertEqual(state["stage_name"], "dealer turn")
        self.frame(state)
        self.assertEqual(state["stage_name"], "end stage")
        self.frame(state)
        self.assertEqual(state["current_money"], 1100)
        self.frame(state, (266, 855))
        self.assertEqual(state["stage_name"], "bet stage")
        self.assertEqual(state["bet_amount"], 0)
        self.assertEqual(state["stats"]["rounds"], 1)
        self.frame(state, (960, 720))
        self.assertEqual(state["current_money"], 1000)
        rig_draws(state, [10, 10, 7, 9])
        self.frame(state, (200, 855))
        with mock.patch.object(pygame.time, "get_ticks",
                               side_effect=[0, 500, 1000, 1500]):
            for _ in range(4):
                self.frame(state)
        self.frame(state, (480, 855))
        self.frame(state)
        self.frame(state)
        self.assertEqual(state["current_money"], 1000)
        self.assertEqual(state["stats"], {"rounds": 2, "wins": 1})

    def test_dealer_soft_17_frame_draws_no_card(self):
        state = make_round((10, 8), (1, 6))
        gs.player_action(state, "stand")
        before = list(state["deck"].cards)
        self.frame(state)
        self.assertEqual(state["stage_name"], "end stage")
        self.assertEqual(state["deck"].cards, before)

    def test_main_startup_and_shutdown(self):
        with mock.patch.object(pygame.event, "get", return_value=[
                pygame.event.Event(pygame.QUIT)]):
            main.main()
        self.assertFalse(pygame.get_init())
        type(self).screen, _ = main.window_initial()

    def test_failed_load_keeps_current_progress(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
                save_manager, "SAVE_DIR", Path(directory)):
            save_manager.slot_path(1).write_text("broken", encoding="utf-8")
            state = gs.new_game()
            state["current_money"] = 1234
            deck = state["deck"]
            gs.open_slots(state, "load", "start menu")
            self.frame(state, (800, 260))
            self.assertEqual(state["current_money"], 1234)
            self.assertIs(state["deck"], deck)
            self.assertIn("failed", state["message"])

    def test_quit_and_one_event_poll_every_stage(self):
        for stage in main.STAGES:
            with self.subTest(stage=stage):
                state = make_round()
                state["stage_name"] = stage
                with mock.patch.object(pygame.event, "get", return_value=[
                        pygame.event.Event(pygame.QUIT)]) as poll:
                    self.frame(state)
                poll.assert_called_once()
                self.assertEqual(state["stage_name"], "quit")

    def test_insurance_ui_and_split_render(self):
        state = make_round((8, 8), (1, 6))
        state["stage_name"] = "insurance"
        self.frame(state, (1200, 855))
        self.assertEqual(state["stage_name"], "player turn")
        rig_draws(state, [10, 9])
        self.frame(state, (1120, 855))
        self.frame(state)
        self.assertEqual(len(state["hands"]), 2)

    def test_save_overwrite_confirmation_and_load_menu(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
                save_manager, "SAVE_DIR", Path(directory)):
            state = gs.new_game()
            gs.prepare_bet(state)
            self.frame(state, (600, 855))
            self.assertEqual(state["stage_name"], "slots")
            self.frame(state, (800, 260))
            self.assertEqual(save_manager.load_game(1)["current_money"], 1000)
            state["current_money"] = 1200
            self.frame(state, (800, 260))
            self.assertEqual(save_manager.load_game(1)["current_money"], 1000)
            self.frame(state, (800, 260))
            self.assertEqual(save_manager.load_game(1)["current_money"], 1200)
            gs.open_slots(state, "load", "start menu")
            self.frame(state, (800, 260))
            self.assertEqual(state["stage_name"], "bet stage")
            self.assertEqual(state["current_money"], 1200)


if __name__ == "__main__":
    unittest.main()
