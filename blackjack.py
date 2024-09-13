import pygame
import random

# 初始化Pygame
pygame.init()

# 定义屏幕尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
ORANGE=(255,165,0)

# 定义字体
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 48)

#定义筹码
class chip:
    def __init__(self,value,color):
        self.value=value
        self.color=color
        self.size=25
        


# 定义扑克牌
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.height = 140
        self.width= self.height/1.4
        self.color="white"
        
    
    def __repr__(self):
        return f"{self.value} {self.suit}"

# 定义牌堆
class Deck:
    suits = ['♥️', '♦️', '♣️', '♠️']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self):
        self.cards = [Card(suit, value) for suit in self.suits for value in self.values]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        return self.cards.pop()

# 绘制扑克牌
# Adjusted draw_card function to calculate card text width and space dynamically
def draw_card(card, x, y):
    pygame.draw.rect(screen, card.color, (x, y, card.width, card.height))
    card_text = str(card)
    text = font.render(card_text, True, BLACK)
    screen.blit(text, (x, y))
    return text.get_width()  # Return the width of the card text

#绘制筹码
def draw_chips(chip,x,y):
    pygame.draw.circle(screen,chip.color,(x,y),chip.size,0)
    value_text=str(chip.value)
    text=font.render(value_text,True,WHITE)
    screen.blit(text, (x, y))
    
    


# 绘制按钮
def draw_button(text, x, y, width, height, color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, (x + (width - text_surf.get_width()) // 2, y + (height - text_surf.get_height()) // 2))

# 初始化牌堆
deck = Deck()

# 初始化玩家和庄家的手牌
def initialize_hands():
    return [deck.deal(), deck.deal()], [deck.deal(), deck.deal()]

player_hand, dealer_hand = initialize_hands()

    # # Game loop: Displaying player's and dealer's cards with dynamic spacing
    # # Display player's cards
    # x_offset = 100  # Initial X position
    # spacing = 20    # Extra spacing between cards
    # for card in player_hand:
    #     card_width = draw_card(card, x_offset, 400)
    #     x_offset += card_width + spacing  # Move X position for the next card

    # # Display dealer's cards
    # x_offset = 100  # Initial X position
    # for card in dealer_hand:
    #     card_width = draw_card(card, x_offset, 100)
    # x_offset += card_width + spacing  # Move X position for the next card

# 计算手牌总值的函数
def calculate_hand_value(hand):
    value = 0
    num_aces = 0
    for card in hand:
        if card.value in ['J', 'Q', 'K']:
            value += 10
        elif card.value == 'A':
            num_aces += 1
            value += 11
        else:
            value += int(card.value)
    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1
    return value

# 判断胜负
def check_winner(player_hand, dealer_hand):
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    if player_value > 21:
        return "Player Busts! Dealer Wins!"
    elif dealer_value > 21:
        return "Dealer Busts! Player Wins!"
    elif player_value == dealer_value:
        return "It's a Tie!"
    elif player_value > dealer_value:
        return "Player Wins!"
    else:
        return "Dealer Wins!"

# 游戏主循环
running = True
player_turn = True
game_over = False
winner_text = ""
chipslist=[5,25,100,500]
chipscolor=["RED","GREEN","BLACK","ORANGE"]

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
        draw_button("Hit", 100, 500, 100, 50, WHITE)
        draw_button("Stand", 300, 500, 100, 50, WHITE)
    elif game_over:
        draw_button("Restart", 300, 500, 200, 50, WHITE)
    
    # 显示胜负结果
    if game_over:
        text_surf = large_font.render(winner_text, True, RED)
        screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, SCREEN_HEIGHT // 2 - text_surf.get_height() // 2))
    
    # 更新屏幕
    pygame.display.flip()

# 退出Pygame
pygame.quit()
