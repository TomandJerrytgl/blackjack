import pygame
import bjlib
import random
import pdb
from bjlib import Button, Chip, Deck  # 确保正确导入

import pygame
from bjlib import initialize_hands, calculate_hand_value, check_winner, Deck, Button

def main():
    # 初始化Pygame
    pygame.init()
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blackjack")

     # 定义颜色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 128, 0)
    RED = (255, 0, 0)
    ORANGE=(255,165,0)

    # 创建按钮和卡牌
    deck = Deck()
    hit_button = Button((100, 500), "Hit")
    stand_button = Button((300, 500), "Stand")
    restart_button = Button((500, 500), "Restart")
   

    # 初始化玩家和庄家的手牌
    player_hand, dealer_hand = initialize_hands(deck)
    chipslist = [5, 25, 100, 500]
    chipscolor = ["RED", "GREEN", "BLACK", "ORANGE"]

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hit_button.is_clicked(event.pos):
                    player_hand.append(deck.deal())
                    if calculate_hand_value(player_hand) > 21:
                        player_turn = False
                        game_over = True
                        winner_text = check_winner(player_hand, dealer_hand)
                elif stand_button.is_clicked(event.pos):
                    player_turn = False
                    while calculate_hand_value(dealer_hand) < 17:
                        dealer_hand.append(deck.deal())
                    game_over = True
                    winner_text = check_winner(player_hand, dealer_hand)
                elif restart_button.is_clicked(event.pos) and game_over:
                    deck = Deck()
                    player_hand, dealer_hand = initialize_hands()
                    player_turn = True
                    game_over = False
                    winner_text = ""

        # 绘制背景
        screen.fill(GREEN)

        # 显示玩家和庄家的牌
        Spacing = 50
        for i, card in enumerate(player_hand):
            draw_card(card, 100 + i * (card.width + Spacing), 400)
        for i, card in enumerate(dealer_hand):
            draw_card(card, 100 + i * (card.width + Spacing), 100)
        for i in range(len(chipslist)):
            chipp = Chip(chipslist[i], chipscolor[i])
            draw_chips(chipp, 300 + i * 60, 300)

        # 绘制按钮
        hit_button.draw_button(screen, font, BLACK)
        stand_button.draw_button(screen, font, BLACK)
        restart_button.draw_button(screen, font, BLACK)

        # 更新显示
        pygame.display.flip()

main()
