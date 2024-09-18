import pygame
import random
import pdb
from tabulate import tabulate

# 初始化Pygame
pygame.init()

# 定义屏幕尺寸
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

# 定义字体
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 48)

#定义筹码
class Chip:
    def __init__(self, position, value):
        self.x, self.y = position  
        self.value = value
        self.color = chipcolor_dict[value]  
        self.size = 50  

    # 绘制芯片
    def draw_chip(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size, 0)  # 绘制芯片
        value_text = str(self.value)
        text = font.render(value_text, True, WHITE)  
        screen.blit(text, (self.x, self.y))  

    # 判断芯片是否被点击
    def chip_is_clicked(self, x, y):

        if (self.x - x) ** 2 + (self.y - y) ** 2 < self.size ** 2:
            return True
        return False

class Button:
    def __init__(self, position, text):
        self.x, self.y = position  # 按钮位置
        self.text = text  # 按钮文本
        self.color = "WHITE"  # 按钮背景颜色
        self.width, self.height = 100, 50  # 按钮的宽度和高度
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # 定义按钮的矩形区域

    # 绘制按钮
    def draw_button(self, screen, font, BLACK):
        # 绘制按钮矩形
        pygame.draw.rect(screen, self.color, self.rect, 0)

        # 渲染文本
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)  # 将文本居中

        # 在按钮上绘制文本
        screen.blit(text_surf, text_rect)

        # 绘制按钮的边框
        pygame.draw.rect(screen, "BLACK", self.rect, 5)

    # 检查按钮是否被点击
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

        


# 定义扑克牌
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.height = 140
        self.width= self.height/1.4
        self.color="white"
        
    
    def __repr__(self):
        return f"{self.suit} {self.value}"

# 定义牌堆
class Deck:
    '''
    Deck: type
	self.Cards: list
		Card: type
    '''
    suits = ['♠️', '♥️', '♦️', '♣️']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck_num = 5 #number of card decks used.
    
    deck_dict = {} #Data type: Dictionary. Number of cards
    # Keys: card faces, "total"
    
    showed_dict = {}
    
    
    def __init__(self):
        self.cards = []
        # Add 5 decks of cards
        for i in range(self.deck_num):
            cards_tmp = [Card(suit, value) for suit in self.suits for value in self.values]
            self.cards.extend(cards_tmp)
        
        self.shuffle()
        
        # Intiate key-values pairs for the deck_dict variable
        self.deck_dict["total"] = 0
        for card in self.cards:
            card_face = (card.suit, card.value)
            self.deck_dict[card_face] = 0
        # Initializing the deck status
        total_tmp = 0
        for card_tmp in self.cards:
            card_face = (card_tmp.suit, card_tmp.value)
            self.deck_dict[card_face] = self.deck_dict[card_face]+1
            total_tmp += 1
        self.deck_dict["total"] = total_tmp

        
        # Intiate key-values pairs for the showed_dict variable
        self.showed_dict["total"] = 0
        for card in self.cards:
            card_face = (card.suit, card.value)
            self.showed_dict[card_face] = 0

        # Read the information of this fresh deck!
        self.read(self.deck_dict)
        self.read(self.showed_dict)
    
    def shuffle(self):
        random.shuffle(self.cards)

    
    def read(self, dict):
        # Counting number of cards
        # Print out the deck status in table format
        total_tmp = 0
        dict_table = []
        inside_b = True
        for suit in self.suits:
            row_counter = 0
            for value in self.values:
                card_face = (suit, value)
                len_values, len_suits = len(self.values), len(self.suits)
                
                if inside_b:
                    dict_table.append(["Cards: ", dict[card_face], suit+"  "+value])
                else:
                    dict_table[row_counter].extend(["|", dict[card_face], suit+"  "+value])
                    row_counter += 1
                
                # print("{}: {}".format(card_face, dict[card_face])) # Print cards number of the same suit and value
                total_tmp += dict[card_face] # Count the cards into total number
            inside_b = False
        print(tabulate(dict_table))

        dict["total"] = total_tmp
        print("total: {}".format(dict["total"]))


    
    def deal(self):
        print("_____________________dealling_______________")
        x = self.cards.pop()
        # Update the status (remove the poped card from the status)
        self.deck_dict[(x.suit,x.value)] = self.deck_dict[(x.suit,x.value)]-1
        self.showed_dict[(x.suit,x.value)] = self.showed_dict[(x.suit,x.value)]+1

        self.read(self.deck_dict)
        self.read(self.showed_dict)
        return x
    

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

# 初始化玩家和庄家的手牌
def initialize_hands():
    return [deck.deal(), deck.deal()], [deck.deal(), deck.deal()]

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
## 初始化牌堆
deck = Deck()

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


running = True
player_turn = True
game_over = False
winner_text = ""
chipslist=[5,25,100,500]
chip_pos=[(300,300),(500,300),(700,300),(900,300)]
chipscolor=["RED","GREEN","BLACK","ORANGE"]
chipp=[]


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
        chipp.append(Chip(chip_pos[i],chipslist[i]))
        chipp[i].draw_chip(screen)   

    
    
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
