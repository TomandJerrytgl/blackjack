"""Pygame initialization and stage dispatch."""

import pygame

import game_stage
import gui


def window_initial(width=gui.DESIGN_WIDTH, height=gui.DESIGN_HEIGHT):
    pygame.init()
    gui.FONT_CACHE.clear()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Blackjack")
    return screen, pygame.time.Clock()


STAGES = {
    "main menu": game_stage.main_menu,
    "start menu": game_stage.start_menu,
    "slots": game_stage.slots_stage,
    "bet stage": game_stage.bet_stage,
    "dealing stage": game_stage.dealing_stage,
    "insurance": game_stage.insurance_stage,
    "player turn": game_stage.player_turn,
    "dealer turn": game_stage.dealer_turn,
    "end stage": game_stage.end_stage,
}


def run_game_stage(screen, clock, stage_info):
    STAGES[stage_info["stage_name"]](screen, clock, stage_info)


def main():
    stage_info = game_stage.new_game()
    try:
        screen, clock = window_initial()
        while stage_info["stage_name"] != "quit":
            run_game_stage(screen, clock, stage_info)
    finally:
        game_stage.cancel_odds(stage_info)
        pygame.quit()


if __name__ == "__main__":
    main()
