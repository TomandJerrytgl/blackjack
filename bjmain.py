
import pygame
import random
import pdb
from tabulate import tabulate
from bjlib import Deck, Chip, Button,initialize_hands,draw_card,calculate_hand_value,check_winner,check_reward

def main():
    # 初始化Pygame
    pygame.init()
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blackjack")

     # 定义颜色字体
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 128, 0)
    RED = (255, 0, 0)
    ORANGE=(255,165,0)

    # 创建按钮,筹码和卡牌
    deck = Deck()
    
    chipslist=[5,25,100,500]
    chip_pos=[(300,300),(500,300),(700,300),(900,300)]
    chips_5=Chip(chip_pos[0],chipslist[0])
    chips_25=Chip(chip_pos[1],chipslist[1])
    chips_100=Chip(chip_pos[2],chipslist[2])
    chips_500=Chip(chip_pos[3],chipslist[3])

    ##可能修改的代码    
    #buttonlist=[]
    #buttton_pos=[]

    deal_button=Button((500, 500), "Deal")
    hit_button = Button((100, 500), "Hit")
    stand_button = Button((300, 500), "Stand")
    restart_button = Button((500, 500), "Restart")
    quit_button=Button((1400, 800), "Quit")
   
    #Setting bet设置金额
    current_money=1000
    bet_money=0
    putting_bet=False
    crmoney_button=Button((800,800),current_money)
    btmoney_button=Button((800,100),bet_money)
    rewardrate=0

    # 初始化玩家和庄家的手牌
    player_hand, dealer_hand = initialize_hands(deck)
    chipslist = [5, 25, 100, 500]
    chipscolor = ["RED", "GREEN", "BLACK", "ORANGE"]

    #设置全局变量
    running = True
    player_turn = True
    game_over = False
    
    

    while running:
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                deck = Deck()

            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if quit_button.is_clicked(event.pos):
                    running=False
                    pygame.quit()  # 关闭Pygame
                    sys.exit()
                if player_turn and not putting_bet and not game_over:
                    if chips_5.is_clicked(event.pos):
                        current_money=current_money-chips_5.value
                        bet_money=bet_money+chips_5.value
                    if chips_25.is_clicked(event.pos):
                        current_money=current_money-chips_25.value
                        bet_money=bet_money+chips_25.value
                    if chips_100.is_clicked(event.pos):
                        current_money=current_money-chips_100.value
                        bet_money=bet_money+chips_100.value
                    if chips_500.is_clicked(event.pos):
                        current_money=current_money-chips_500.value
                        bet_money=bet_money+chips_500.value
                    crmoney_button=Button((800,800),current_money)
                    btmoney_button=Button((800,100),bet_money)
                    if deal_button.is_clicked(event.pos):
                        putting_bet=True
                    
                if player_turn and putting_bet and not game_over:
                    hit_button.draw_button(screen)
                    stand_button.draw_button(screen)
                    
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
                        
                elif game_over:
                    if restart_button.is_clicked(event.pos):
                        player_hand, dealer_hand = initialize_hands(deck)
                        player_turn = True
                        game_over = False
                        putting_bet=False
                        winner_text = ""
                # deck.calculate_prob(player_hand,21)
        
        #结算金钱
        if game_over:
            rewardrate=check_reward(player_hand, dealer_hand)
            current_money=current_money+bet_money*rewardrate
            bet_money=0
            crmoney_button=Button((800,800),current_money)
            btmoney_button=Button((800,100),bet_money)
        


        
        
        #绘制背景
        screen.fill(GREEN)
        crmoney_button.draw_button(screen)
        btmoney_button.draw_button(screen)
        quit_button.draw_button(screen)

        

        

        #绘制筹码
        if player_turn and not putting_bet and not game_over:
            chips_5.draw_chip(screen)
            chips_25.draw_chip(screen)
            chips_100.draw_chip(screen)
            chips_500.draw_chip(screen)
            deal_button.draw_button(screen)

        

        #绘制按钮
        if player_turn and putting_bet and not game_over:
            hit_button.draw_button(screen)
            stand_button.draw_button(screen)
        #绘制卡牌
            Spacing = 50
            for i, card in enumerate(player_hand):
                draw_card(card, 100 + i * (card.width+Spacing), 400)
            for i, card in enumerate(dealer_hand):
                draw_card(card, 100 + i * (card.width+Spacing), 100)

        elif game_over:
            restart_button.draw_button(screen)

        if game_over:
            text_surf = large_font.render(winner_text, True, RED)
            screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, SCREEN_HEIGHT // 2 - text_surf.get_height() // 2))

        #更新屏幕
        pygame.display.flip()    
        
            
        
                        
                
                    
                        
                

                
            

main()
