import pygame
import random
import pdb
from tabulate import tabulate
from decimal import Decimal, getcontext #更加精确的小数后多位计算
getcontext().prec = 30  # 小数点后30位
import copy #用于计算牌库概率时所需要的deepcopy

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

    def face_convert(self, str):
        # 把 Card Face 转化成可以用在deck_calc数据结构中对应位置的 integer
        if str.isdigit():
            return int(str)-1
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
            self.deck_calc[self.face_convert(card_tmp.value)]\
                [self.face_convert(card_tmp.suit)] += 1

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
        # print("total: {}".format(dict["total"]))

        print(self.deck_calc)



    def deal(self):
        print("_____________________dealling_______________")
        x = self.cards.pop()
        # 抽卡之后更新显示牌库(deck_dict), 计算牌库(deck_calc), 已抽卡片(drawed_dict)
        self.deck_dict[(x.suit,x.value)] = self.deck_dict[(x.suit,x.value)]-1
        self.drawed_dict[(x.suit,x.value)] = self.drawed_dict[(x.suit,x.value)]+1

        val_int = self.face_convert(x.value)
        suit_int = self.face_convert(x.suit)
        self.deck_calc[val_int][suit_int] -= 1

        self.read(self.deck_dict)
        self.read(self.drawed_dict)
        return x

    def deck_calc_convert(self, list):
        # 把 Deck_calc 里面每一种面值不同花色的牌都合并, 计算出 A, 1, ..., K 分别有多少张
        # Output: list
            # elements: int
            # len: 13
        list_tmp = []
        for i in range(len(list)):
            sum_tmp = 0
            for j in list[i]:
                sum_tmp += int(j)

            if i<=9:
                list_tmp.append(sum_tmp)
            else:
                list_tmp[9] += sum_tmp
        return list_tmp

    def get_prob_list(self, hand_start, calc_data):
        # 根据此刻面值(手上牌大小的总和), 以及牌库, 计算落在不同最终面值的概率
        # 输出: 最终面值概率
        #   len: 22.
        #   elements: 0-21
        #       0: 爆牌/超过21的概率
        #       1-21: 停留在这些手牌总和的概率

        # 初始化概率列表
        hand_end_prob = [0]*22

        # 计算最终面值概率的主循环. 结束条件: 牌库所有的牌都被计算一遍.
        deck = copy.deepcopy(calc_data)
        deck_total = sum(deck) # 牌库剩余总数量. 为了不重复计算总和而单独存一个变量.


        def pop_greatest():
            """
            例子: 变量变化
                deck: [20, 19, 20, 20, 20, 19, 20, 19, 20, 79] -> [20, 19, 20, 20, 20, 19, 20, 19, 20, 78]
                deck_total: 256 -> 255
            返回:
                card_face: 概率最大牌的卡面值
                card_prob: 抽到这张拍的概率
                    type: Decimal. 确保保留比较多的小数点后位数
            """
            nonlocal deck, deck_total #修改这个函数外的 deck 和 deck_total 变量

            index_of_greatest = deck.index(max(deck))
            deck[index_of_greatest] -= 1 #抽出这张卡
            deck_total -= 1

            # index_of_greatest +1, 因为卡面为10的牌是在 index 9. 这里要返回卡面
            card_face = index_of_greatest+1

            # deck[index_of_greatest] +1, 因为计算抽到的卡面的概率, 需要考虑刚刚它还在牌堆里的情况
            card_prob = Decimal(deck[index_of_greatest]+1)/Decimal(deck_total)
            return card_face, card_prob

        while deck_total != 0:
            next_card, next_card_prob =  pop_greatest()
            # 选出概率最大的牌
            print(f"卡: {next_card}, 概率: {next_card_prob}")

            #


        pdb.set_trace()
        # 算出抽到某张牌的概率. 然后加到对应的最终面值上.
        # 情况1: 没有爆
        #   将此刻的面值概率加上
        #   再次加上概率面值
        # 情况2: 爆了

        return


    def calculate_prob(self, hand, n):
        # Variables
            # hand: list of card
                # Coudl be player_hand, or dealer_hand
            # n: integer
                # Target total value

        # 根据已经被抽的牌, 算出未来牌的概率
        calc_data = self.deck_calc_convert(self.deck_calc)
        # 计算手上牌的总和
        sum_hand = 0
        for i in range(len(hand)):
            if hand[i].value in ("A"):
                sum_hand += 1
            elif hand[i].value in ("J", "Q", "K"):
                sum_hand += 10
            else:
                sum_hand += int(hand[i].value)


        prob_list = self.get_prob_list(sum_hand, calc_data)






        # # 邓壹凡写的算法(临时版)
        # final_list=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        # current_pt = sum_hand
        # while current_pt <= 16:
        #     for i in range(1,10):
        #         nextpoint=current_pt+i
        #         if nextpoint>=22:
        #             nextpoint=22
        #         if final_list[nextpoint-1]==0:
        #             final_list[nextpoint-1]=final_list[nextpoint-1]+prob_list[i-1]
        #         else:
        #             final_list[nextpoint-1]=final_list[nextpoint-1]+final_list[nextpoint-1]*prob_list[i-1]
        #
        #     current_pt=current_pt+1
        #     print(final_list)



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
