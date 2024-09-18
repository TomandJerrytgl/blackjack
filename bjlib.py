import pygame
import random
    
color = {5: "RED",
         25: "GREEN",
         100: "BLACK",
         500: "ORANGE"}


class Card:
    def __init__(self, suit, value):
        self.suit = suit  # 花色
        self.value = value  # 牌值
        self.width = 50  # 卡片宽度
        self.height = 80  # 卡片高度
        self.color = (255, 255, 255)  # 卡片颜色

    def __str__(self):
        return f"{self.value}{self.suit}"

class Chip:
    def __init__(self, position, value):
        self.x, self.y = position  
        self.value = value
        self.color = color[value]  
        self.size = 50  

    # 绘制芯片
    def draw_chip(self, screen, font, WHITE):
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
        # Print out the deck status
        total_tmp = 0
        for suit in self.suits:
            for value in self.values:
                card_face = (suit, value)
                print("{}: {}".format(card_face, dict[card_face])) # Print cards number of the same suit and value
                total_tmp += dict[card_face] # Count the cards into total number
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
