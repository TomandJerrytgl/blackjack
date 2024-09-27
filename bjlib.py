import pygame
import random
import pdb
from tabulate import tabulate

pygame.init()
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack")
    
chipcolor_dict = {5: "RED",
         25: "GREEN",
         100: "BLACK",
         500: "ORANGE"}
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
    def is_clicked(self, mouse_pos):
        x,y=mouse_pos

        if (self.x - x) ** 2 + (self.y - y) ** 2 < self.size ** 2:
            return True
        return False

class Button:
    def __init__(self, position, text):
        self.x, self.y = position  # 按钮位置
        self.text = str(text)  # 按钮文本
        self.color = "WHITE"  # 按钮背景颜色
        self.width, self.height = 100, 50  # 按钮的宽度和高度
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # 定义按钮的矩形区域

    # 绘制按钮
    def draw_button(self, screen):
        # 绘制按钮矩形
        pygame.draw.rect(screen, self.color, self.rect, 0)

        # 渲染文本
        text_surf = font.render(self.text, True, "BLACK")
        text_rect = text_surf.get_rect(center=self.rect.center)  # 将文本居中

        # 在按钮上绘制文本
        screen.blit(text_surf, text_rect)

        # 绘制按钮的边框
        pygame.draw.rect(screen, "BLACK", self.rect, 3)

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
        # Keys: card_face, "total"
            # card_face = (card.suit, card.value)
            # "total" string
        # Value: Integer

    drawed_dict = {}
    
    deck_calc = [] # 以适合计算的方式记录牌堆情况
    # 数据结构.
    # deck_calc[i][k] 是一个整数.
        # 这个整数代表这个牌的数量.
        # i,j 对应大小和花色. 
            # i: 'A'=0, '2'=1, '3'=2, ..., 'J'=10, 'Q'=11, 'K'=12
            # j: '♠️'=0, '♥️'=1, '♦️'=2, '♣️'=3
    for i in range(13):
        deck_calc.append([0,0,0,0])

    def face_to_int(self, str):
        # 把 Card Face 转化成可以用在deck_calc数据结构中对应位置的 integer
        if str.isdigit():
            return int(str)
        else:
            face_map = {'♠️': 0, '♥️': 1, '♦️': 2, '♣️': 3, "A":0, "J":10, "Q":11, "K":12}
            return face_map.get(str, -1)  # Returns -1 if the suit is not found

    
    
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

            #初始化deck_calc
            self.deck_calc[self.face_to_int(card_tmp.value)]\
                [self.face_to_int(card_tmp.suit)] += 1
            
        self.deck_dict["total"] = total_tmp

        
        # Intiate key-values pairs for the drawed_dict variable
        self.drawed_dict["total"] = 0
        for card in self.cards:
            card_face = (card.suit, card.value)
            self.drawed_dict[card_face] = 0

        # Read the information of this fresh deck!
        self.read(self.deck_dict)
        self.read(self.drawed_dict)
    
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
        self.drawed_dict[(x.suit,x.value)] = self.drawed_dict[(x.suit,x.value)]+1

        self.read(self.deck_dict)
        self.read(self.drawed_dict)
        return x

    def calculate(self, hand, n):
        # Variables
            # hand: list of card
                # Coudl be player_hand, or dealer_hand
            # n: integer
                # Target total value

        # 根据已经被抽的牌, 算出未来牌的概率
        used_cards = self.deck_dict
        
        pdb.set_trace()

        # 计算手上牌的总和
        sum_hand = 0
        for i in range(len(hand)):
            if hand[i].value == "A":
                sum_hand += 1
            if hand[i].value in ("j", "q", "k"):
                sum_hand += 10
            else:
                sum_hand += hand[i].value

        # 手上牌到 target value 的差值
        diff = n - sum_hand
    

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
def initialize_hands(deck):
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

def check_reward(player_hand, dealer_hand):
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    if player_value > 21:
        
        return 0
    elif dealer_value > 21:
        
        return 2
    elif player_value == dealer_value:
        
        return 1
    elif player_value > dealer_value:
        
        return 2
    else:
        
        return 0
