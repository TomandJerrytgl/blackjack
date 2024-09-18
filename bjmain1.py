import pygame
import bjlib1
import random
import pdb

def main():
    # 初始化Pygame
    pygame.init()
    # 定义屏幕尺寸
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blackjack")

    #定义按键
    hit_pos=(100,500)
    hit_button=Button(hit_pos,"Hit")
    stand_pos=(300,500)
    stand_button=Button(stand_pos,"Stand")
    restart_pos=(300,500)
    restart_button=Button(restart_pos,"Restart")

    # 定义颜色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 128, 0)
    RED = (255, 0, 0)
    ORANGE=(255,165,0)

    # 定义字体
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)
    running = True
    player_turn = True
    game_over = False
    winner_text = ""
    chipslist=[5,25,100,500]
    chipscolor=["RED","GREEN","BLACK","ORANGE"]
    money=1000
    #pdb.set_trace()
    player_hand, dealer_hand = initialize_hands()

    while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if player_turn and not game_over:
                if 100 < x < 200 and 500 < y < 550:
                    player_hand.append(deck.deal())
                    if calculate_hand_value(player_hand) > 21:
                        player_turn = False
                        game_over = True
                        winner_text = check_winner(player_hand, dealer_hand)
                elif 300 < x < 400 and 500 < y < 550:
                    player_turn = False
                    while calculate_hand_value(dealer_hand) < 17:
                        dealer_hand.append(deck.deal())
                    game_over = True
                    winner_text = check_winner(player_hand, dealer_hand)
            elif game_over:
                if 300 < x < 500 and 500 < y < 550:
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
        draw_card(card, 100 + i * (card.width+Spacing), 400)
    for i, card in enumerate(dealer_hand):
        draw_card(card, 100 + i * (card.width+Spacing), 100)
    for i in range(len(chipslist)):
        chipp=chip(chipslist[i],chipscolor[i])
        draw_chips(chipp,300+i*60,300)    

    
    
    # 绘制按钮
    if player_turn and not game_over:
        hit_button.draw_button()


main()
