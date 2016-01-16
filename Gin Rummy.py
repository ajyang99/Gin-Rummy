# Gin Rummy
# Recreation of the classic card game Gin Rummy
# Design based on AI Factory's version (available on Google Play)
# Rules: http://www.pagat.com/rummy/ginrummy.html
# Coded by Joyce Yang
# Submitted on June 14 2015
# Special thanks to Ms. Stusiak for all the help!

import simplegui
import random
import math

# load card sprite - 949x392 - source: jfitz.com
CARD_SIZE_ORIGINAL = (73, 98)
CARD_CENTER_ORIGINAL = (36.5, 49)
CARD_SIZE = (CARD_SIZE_ORIGINAL[0] * 1.2, CARD_SIZE_ORIGINAL[1] * 1.2)
CARD_CENTER = (CARD_SIZE[0] / 2, CARD_SIZE[1] / 2)
card_images = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/cards.jfitz.png")

CARD_BACK_SIZE_ORIGINAL = (71, 96)
CARD_BACK_CENTER_ORIGINAL = (35.5, 48)
card_back = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/card_back.png") 

# define globals for cards:
# tuples for suits and ranks
# dictionary of rank-number converter (for sorting): A = 1, J = 11, Q = 12, K = 13
# dictionary of values
SUITS = ('Club', 'Spade', 'Heart', 'Diamond')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
RANKS_CONVERTER = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                   'J': 11, 'Q': 12, 'K': 13}
CARD_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
               'J': 10, 'Q': 10, 'K': 10}

# define the positions for the stock, discarded and knock pile, player's & computer's hand
STOCK_PILE_POS = (310, 270)
DISCARD_PILE_POS = (172, 260)
KNOCK_CARD_POS = (445, 258)
PLAYER_HAND_POS = (100, 455)
COMPUTER_HAND_POS = (100, 75)
COMPUTER_HAND_CENTER = (250, 75)
# define velocity for each computer animation
# Animation1: drawing card from the discard pile to the computer hand
# Animation2: drawing card from the stock pile to the computer hand
# Animation3: discarding card from the computer hand
ANIMATION1_VEL = [(COMPUTER_HAND_CENTER[0] - DISCARD_PILE_POS[0]) / 50.0, 
                  (COMPUTER_HAND_CENTER[1] - DISCARD_PILE_POS[1]) / 50.0]
ANIMATION2_VEL = [(COMPUTER_HAND_CENTER[0] - STOCK_PILE_POS[0]) / 50.0, 
                  (COMPUTER_HAND_CENTER[1] - STOCK_PILE_POS[1]) / 50.0]
ANIMATION3_VEL = [(DISCARD_PILE_POS[0] - COMPUTER_HAND_CENTER[0]) / 50.0,
                  (DISCARD_PILE_POS[1] - COMPUTER_HAND_CENTER[1]) / 50.0]

# initialize global variables
player_draw = True # True when it is player's turn to draw; False when it is not
player_discard = False # True when it is player's turn to discard; False when it is not
computer_draw = False # True when it is computer's turn to draw; False when it is not
card_popped = False # True when a card is "popped" up
decline_round = True # the first round
animation_draw_from_discard = False
animation_draw_from_stock = False
animation_discard = False
knock_message_display = False
lay_off_message_display = False
score_display_initiator = False # transitioning between knock / lay off and score display
score_display = False # controls the display of scores
in_play = False
computer_knock = False
player_knock = False
drawing_from_discard = False
game_over = True
strike_one = False
short_of_card = False
# initialize the message on the screen
message1 = ''
message2 = ''
message3 = ''
message4 = ''
message5 = ''
# initialize scores and round #
player_score = 0
computer_score = 0
round_num = 0

# start a new game
def new_game():
    global player_score, computer_score, game_over, round_num, strike_one, message4, message5
    if game_over:
        game_over = False
        strike_one = False
        player_score = 0
        computer_score = 0
        round_num = 0
        deal()
        return
    
    # strike_one: give the player a chance to regret when they hit the "New Game" button
    if not game_over and not strike_one:
        message4 = 'The Game is Still On. Are You Sure to Forfeit the Game?'
        message5 = 'Hit the New Game button again if you are sure to forfeit'
        strike_one = True
        return
    
    if strike_one:
        message4 = 'You forfeit, the computer won the previous game'
        message5 = ''
        strike_one = False
        player_score = 0
        computer_score = 0
        round_num = 0
        game_over = False
        deal()

# helper function that decides if the mouse clicks on a card
def click_on_card(mouse_pos, card_pos, card_size):
    cond1 = mouse_pos[0] > card_pos[0]
    cond2 = mouse_pos[0] < (card_pos[0] + card_size[0])
    if not card_popped or player_discard:
        cond3 = mouse_pos[1] > card_pos[1]
        cond4 = mouse_pos[1] < (card_pos[1] + card_size[1])
    else: # when the card is popped up, it is moved up by 1/2 card_size[1]
        cond3 = mouse_pos[1] > (card_pos[1] - card_size[1] / 2)
        cond4 = mouse_pos[1] < (card_pos[1] + card_size[1] / 2)
    if cond1 and cond2 and cond3 and cond4: # the mouse pos is inside the card
        return True
    else:
        return False

# helper function that swaps two objects in a list
def swap(i, j, list):
    temp = list[i]
    list[i] = list[j]
    list[j] = temp
    
# helper function that update scores for the player and computer
def score_update(score1, score2, val1, val2, val_diff):
    if val_diff > 0:
        if val1 != 0:
            return [score1 + val_diff, score2]
        elif val2 != 0:
            return [score1 + val_diff + 20, score2]
        else:
            return [score1, score2 + 10]
    else:
        if val2 == 0:
            return [score1, score2 - val_diff + 30]
        else:
            return [score1, score2 - val_diff + 10]

# define card class
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        # self.pop records whether the card is "popped" up
        self.pop = False
        # self.meld is a list recording the meld#'s the card can be in
        self.meld = []
        # self.meld_num is the final meld# the card decides to be in
        # ex: Heart Q.meld = [0, 1] but self.meld_num can only be either
        # 0 or 1
        self.meld_num = -1 # -1 represents that the card is not in a meld
        # self.meld_status indicates whether the card is counted in a meld or not
        self.meld_status = False
        # for animation uses
        self.pos = [0, 0]
        self.vel = [0, 0]
        # lay_off_meld_num is the # of the meld in which the card can be laid off
        self.lay_off_meld_num = -1
    
    def initialize_pop(self):
        self.pop = False
        
    def reverse_pop(self):
        self.pop = not self.pop
    
    def clear_previous_melds(self):
        self.meld = []
    
    def add_meld_num(self, meld_num):
        self.meld.append(meld_num)
    
    def set_meld_num(self, meld_num):
        self.meld_num = meld_num
    
    def set_meld_status_true(self):
        self.meld_status = True
    
    def set_meld_status_false(self):
        self.meld_status = False
    
    # for animation uses - to set the moving card's initial pos
    def set_pos(self, pos):
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
    
    # for animation uses - to set the moving card's velocity
    def set_vel(self, vel):
        self.vel[0] = vel[0]
        self.vel[1] = vel[1]
        
    def set_lay_off_meld_num(self, num):
        self.lay_off_meld_num = num
    
    # for animation uses - to update the moving card's pos
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

    def __str__(self):
        return self.suit + self.rank 

    def get_suit(self):
        return self.suit 

    def get_rank(self):
        return self.rank
    
    def get_pop(self):
        return self.pop
    
    def get_meld(self):
        return self.meld
    
    def get_meld_num(self):
        return self.meld_num
    
    def get_meld_status(self):
        return self.meld_status
    
    # for animation uses
    def get_pos(self):
        return self.pos
    
    def get_lay_off_meld_num(self):
        return self.lay_off_meld_num

    def draw(self, canvas, pos):
        width = CARD_SIZE_ORIGINAL[0]
        height = CARD_SIZE_ORIGINAL[1]
        row = SUITS.index(self.suit)
        column = RANKS.index(self.rank)
        card_location = (CARD_CENTER_ORIGINAL[0] + column * width ,
                         CARD_CENTER_ORIGINAL[1] + row * height)
        # position is top left corner of card
        canvas.draw_image(card_images, card_location, CARD_SIZE_ORIGINAL,
                          [pos[0] + CARD_CENTER[0], 
                           pos[1] + CARD_CENTER[1]], CARD_SIZE)

# define hand class
class Hand:
    def __init__(self):
        self.cards = []
        # self.cards_sorted_by_suit stores the cards sorted by suit and then ranks
        self.cards_sorted_by_suit = []
        # self.cards[self.cards_suit_index[i]] is the ith card in self.cards_sorted_by_suit
        self.cards_suit_index = []
        self.melds = []
        self.deadwood = []
    
    def __str__(self):
        s = ''
        for card in self.cards:
            s += str(card) + ' '
        return s
    
    def draw(self, canvas, pos):
        for card in self.cards:
            pos_x = pos[0] + CARD_SIZE[0] / 3 * self.cards.index(card)
            # the card moves up by CARD_SIZE[1] / 3 if it is popped
            if card.get_pop():
                pos_y = pos[1] - CARD_SIZE[1] / 3
            else:
                pos_y = pos[1]
            card.draw(canvas, [pos_x, pos_y])
            if card.get_lay_off_meld_num() != -1:
                # draw a red equilateral triangle with side length 10 under the card that can be laid off
                triangle_pos_x = pos_x + CARD_SIZE[0] / 6
                triangle_pos_y = pos_y + CARD_SIZE[1]
                canvas.draw_polygon([[triangle_pos_x, triangle_pos_y],
                                    [triangle_pos_x - 5, triangle_pos_y + 5 * math.sqrt(3)],
                                    [triangle_pos_x + 5, triangle_pos_y + 5 * math.sqrt(3)]],
                                    1, 'red', 'red')
    
    def change_pop_status(self, index):
        self.cards[index].reverse_pop()
   
    def change_lay_off_meld_num(self, index, num):
        self.cards[index].set_lay_off_meld_num(num)
    
    # finds index of a card in the hand
    def find_index(self, card):
        return self.cards.index(card)
    
    # replicate the hand
    def replicate(self, new_hand):
        for card in self.cards:
            new_hand.add_card(card)
    
    # calculate deadwood value for function find_best_meld_combo
    def calc_deadwood_value_for_unsorted(self):
        value = 0
        for card in self.cards:
            if not card.get_meld_status(): # the card is not in a meld
                value += CARD_VALUES[card.get_rank()]
        return value
    
    # calculate deadwood value for a sorted hand
    def calc_deadwood_value(self):
        value = 0
        for card in self.deadwood:
            value += CARD_VALUES[card.get_rank()]
        return value
    
    def add_card(self, new_card):
        self.cards.append(new_card)
    
    def insert_card(self, index, new_card):
        self.cards.insert(index, new_card)
    
    def discard(self, card_index):
        # Use the number of the card in the list to get the card
        # the player wants to discard and .pop() to return it
        return self.cards.pop(card_index)   
    
    # insert self.cards[index2] before self.cards[index1]
    def reorganize_card(self, index1, index2):
        self.cards.insert(index1, self.cards.pop(index2))
    
    # check if the mouse clicks on any card in the hand
    # if so, return the card index
    # if not, return "No Match Found"
    def check_clicked_card_index(self, mouse_pos):
        global player_discard
        
        for card in self.cards:
            if card != self.cards[-1]:
                if click_on_card(mouse_pos, [PLAYER_HAND_POS[0] + CARD_SIZE[0] / 3 * self.cards.index(card),
                                             PLAYER_HAND_POS[1]], [CARD_SIZE[0] / 3, CARD_SIZE[1]]):
                    return self.cards.index(card)
            else:
                if click_on_card(mouse_pos, [PLAYER_HAND_POS[0] + CARD_SIZE[0] / 3 * self.cards.index(card),
                                             PLAYER_HAND_POS[1]], CARD_SIZE):
                    return -1
        return "No Match Found"
    
    # sort self.cards according to ranks and then suits
    # selection sorting algorithm
    def sort_by_rank(self, start, end):
        for i in range(start, end - 1):
            for j in range(i + 1, end):
                rank1 = RANKS_CONVERTER[self.cards[i].get_rank()]
                rank2 = RANKS_CONVERTER[self.cards[j].get_rank()]
                suit1 = self.cards[i].get_suit()
                suit2 = self.cards[j].get_suit()
                if rank1 > rank2:
                    swap(i, j, self.cards)
                elif rank1 == rank2:
                    if SUITS.index(suit1) > SUITS.index(suit2):
                        swap(i, j, self.cards)
    
    # sort self.cards_sorted_by_suit according to suits and then ranks
    # selection sorting algorithm
    def sort_by_suit(self):
        for i in range(len(self.cards_sorted_by_suit) - 1):
            for j in range(i + 1, len(self.cards_sorted_by_suit)):
                rank1 = RANKS_CONVERTER[self.cards_sorted_by_suit[i].get_rank()]
                rank2 = RANKS_CONVERTER[self.cards_sorted_by_suit[j].get_rank()]
                suit1 = self.cards_sorted_by_suit[i].get_suit()
                suit2 = self.cards_sorted_by_suit[j].get_suit()
                if SUITS.index(suit1) > SUITS.index(suit2):
                    swap(i, j, self.cards_sorted_by_suit)
                    swap(i, j, self.cards_suit_index)
                elif SUITS.index(suit1) == SUITS.index(suit2):
                    if rank1 > rank2:
                        swap(i, j, self.cards_sorted_by_suit)
                        swap(i, j, self.cards_suit_index)
    
    # brute-force searching algorithm that finds the best meld combo in the current hand 
    # with the least number of deadwood
    def find_best_meld_combo(self, index):
        global meld_num, same_rank_meld_num, meld_num_freq, min_deadwood_val 
        global best_meld_index_list, card_meld_num_list
        if index == len(self.cards):
            # check failed same-suit melds and reset the meld_num of the cards in the
            # failed same-suit melds to -1 (meaning that these cards cannot form a meld)
            for num in range(same_rank_meld_num, meld_num):
                index_list = []
                for card in self.cards:
                    if card.get_meld_num() == num:
                        index_list.append(self.cards.index(card))
                meld_failed = False
                i = 0
                while not meld_failed and i < len(index_list)- 1:
                    rank1 = RANKS_CONVERTER[self.cards[index_list[i]].get_rank()]
                    rank2 = RANKS_CONVERTER[self.cards[index_list[i + 1]].get_rank()]
                    if rank1 + 1 != rank2:
                        meld_failed = True
                    i += 1
                if meld_failed:
                    for i in index_list:
                        self.cards[i].set_meld_num(-1)
            
            # set meld_status for each card in self.cards to calculate deadwood value for
            # current combo
            for card in self.cards:
                if card.get_meld_num() == -1:
                    card.set_meld_status_false()
                elif meld_num_freq[card.get_meld_num()] < 3: # failed same-rank melds
                    card.set_meld_num(-1)
                    card.set_meld_status_false()
                else:
                    card.set_meld_status_true()
                
            current_hand_val = self.calc_deadwood_value_for_unsorted()

            if current_hand_val < min_deadwood_val: # a better combo than the current meld combo
                # update current best meld combo
                min_deadwood_val = current_hand_val
                best_meld_index_list = []
                for i in range(meld_num):
                    if meld_num_freq[i] >= 3:
                        best_meld_index_list.append(i)
                card_meld_num_list = []
                for i in range(len(self.cards)):
                    card_meld_num_list.append(self.cards[i].get_meld_num())
            
            # backtrack the changed meld_num (now -1) of cards in the failed same-suit melds
            for card in self.cards:
                if len(card.get_meld()) == 1:
                    card.set_meld_num(card.get_meld()[0])                    
            return
        
        if self.cards[index].get_meld() == []: # the card cannot be in a meld whatsoever
            self.cards[index].set_meld_num(-1)
            self.find_best_meld_combo(index + 1)
            return
        
        if len(self.cards[index].get_meld()) == 1: # the card only belongs to one meld
            x = self.cards[index].get_meld()[0]
            self.cards[index].set_meld_num(x)
            meld_num_freq.insert(x, meld_num_freq.pop(x) + 1)
            self.find_best_meld_combo(index + 1)
            meld_num_freq.insert(x, meld_num_freq.pop(x) - 1) # backtracking
            return
        
        if len(self.cards[index].get_meld()) == 2: # the card can be present in either melds
                                                   # (either a same-rank or a same-suit meld)
            x = self.cards[index].get_meld()[0]
            self.cards[index].set_meld_num(x)
            meld_num_freq.insert(x, meld_num_freq.pop(x) + 1)
            self.find_best_meld_combo(index + 1)
            meld_num_freq.insert(x, meld_num_freq.pop(x) - 1) # backtracking
            
            x = self.cards[index].get_meld()[1]
            self.cards[index].set_meld_num(x)
            meld_num_freq.insert(x, meld_num_freq.pop(x) + 1)
            self.find_best_meld_combo(index + 1)
            meld_num_freq.insert(x, meld_num_freq.pop(x) - 1) # backtracking
            return
    
    # sort the hand with melds first and then deadwoods sorted by ranks and then suits
    def sort(self):
        global meld_num, same_rank_meld_num, meld_num_freq, min_deadwood_val
        global best_meld_index_list, card_meld_num_list, card_popped
        
        # initialization
        card_popped = False # popped card comes back when "sort" is hit
        for card in self.cards:
            card.clear_previous_melds()
            card.initialize_pop()
     
        # sort self.cards by ranks then suits
        self.sort_by_rank(0, len(self.cards))
        
        # detect same-rank sequences and add the meld number to each card in the sequence
        # ex: if the hand is Heart A, Diamond A, Spade A, Heart 2, Diamond 3, Club 3, Spade 3...
        # then Heart A, Diamond A and Spade A belong to meld #0 and Diamond 3, Club 3, Spade 3 belong to meld #1
        # 0's are added to Heart A, Diamond A and Spade A's meld lists, and 1's are added to Diamond 3, Club 3 and
        # Spade 3's meld lists
        meld_num = 0
        i = 0
        while i < len(self.cards):
            j = i + 1
            while j < len(self.cards) and self.cards[i].get_rank() == self.cards[j].get_rank():
                j += 1
            if i + 2 < j:
                while i < j:
                    self.cards[i].add_meld_num(meld_num)
                    i += 1
                meld_num += 1
            else:
                i = j
        same_rank_meld_num = meld_num
        
        # sort self.cards_sorted_by_suit by suits then ranks
        self.cards_sorted_by_suit = []
        for card in self.cards:
            self.cards_sorted_by_suit.append(card)
        self.cards_suit_index = []
        for i in range(len(self.cards)):
            self.cards_suit_index.append(i)
        self.sort_by_suit()
        
        # detect same-suits sequences and add the meld number to each card in the sequence
        # ex: if the hand is Heart A, Heart 2, Heart 3, Diamond 3, Diamond 4, Diamond 5...
        # then Heart A, Heart 2, Heart 3 belong to meld # 3 and Diamond 3, Diamond 4, Diamond 5 belong to meld #4
        # 3's are added to Heart A, Heart B and Heart 3's meld lists, and 4's are added to Diamond 3, Diamond 4 and
        # Diamond 5's meld lists      
        i = 0
        while i < len(self.cards_sorted_by_suit):
            j = i + 1
            in_sequence = True
            while j < len(self.cards_sorted_by_suit) and in_sequence:
                cond1 = self.cards_sorted_by_suit[i].get_suit() == self.cards_sorted_by_suit[j].get_suit()
                cond2 = RANKS_CONVERTER[self.cards_sorted_by_suit[j - 1].get_rank()] + 1 == RANKS_CONVERTER[self.cards_sorted_by_suit[j].get_rank()]
                if cond1 and cond2:
                    j += 1
                else:
                    in_sequence = False
            if i + 2 < j:
                while i < j:
                    self.cards[self.cards_suit_index[i]].add_meld_num(meld_num)
                    i += 1
                meld_num += 1
            else:
                i = j
        
        # initialize meld_num_freq, min_deadwood_val, min_meld_num_list and card_meld_num_list
        # call a recursive function self.find_best_meld_combo(index) to find out a best
        # combination of melds with the smallest deadwood value
        meld_num_freq = [] # meld_num_freq[i] indicates how many cards choose to stay in 
                           # meld #i (helps detect failed same-rank melds)
        for i in range(meld_num):
            meld_num_freq.append(0)
        min_deadwood_val = 1000 # initialize the min_dead_wood_val with a large value
        best_meld_index_list = [] # stores the meld #'s in the best combo
        card_meld_num_list = [] # records the meld # each card is in in the best meld combo
        
        self.find_best_meld_combo(0)
        # update the best meld #'s in self.cards
        for i in range(len(self.cards)):
            self.cards[i].set_meld_num(card_meld_num_list[i])
        
        # self.melds stores the cards in the melds and self.deadwood stores the deadwood cards
        # update self.cards by merging self.melds and self.deadwood together
        self.melds = []
        for num in best_meld_index_list:
            for i in range(len(card_meld_num_list)):
                if card_meld_num_list[i] == num:
                    self.melds.append(self.cards[i])
        self.deadwood = []
        for i in range(len(card_meld_num_list)):
            if card_meld_num_list[i] == -1:
                self.deadwood.append(self.cards[i])
        self.cards = self.melds + self.deadwood
    
    # check if there are cards that can be laid off from hand to self
    def check_if_laid_off(self, hand):
        global meld_num, lay_off_message_display
        
        i = 0
        while i < len(self.melds):
            j = i + 1
            while j < len(self.melds) and self.melds[i].get_meld_num() == self.melds[j].get_meld_num():
                j += 1
            if i < len(self.melds) - 1:
                if self.melds[i].get_rank() == self.melds[i + 1].get_rank(): # same-rank
                    for card in hand.get_deadwood():
                        if self.melds[i].get_rank() == card.get_rank():
                            hand.change_lay_off_meld_num(hand.find_index(card), self.cards[i].get_meld_num())
                            lay_off_message_display = True
                else:
                    current_suit = self.melds[i].get_suit()
                    head_rank = RANKS_CONVERTER[self.melds[i].get_rank()]
                    tail_rank = RANKS_CONVERTER[self.melds[j - 1].get_rank()]
                    for index in range(len(hand.get_deadwood())):
                        index2 = len(hand.get_deadwood()) - index - 1
                        if hand.get_deadwood()[index].get_suit() == current_suit: # same-suit
                            if RANKS_CONVERTER[hand.get_deadwood()[index].get_rank()] == tail_rank + 1:
                                tail_rank += 1
                                hand.change_lay_off_meld_num(index + len(hand.get_melds()), self.cards[i].get_meld_num())
                                lay_off_message_display = True
                        if hand.get_deadwood()[index2].get_suit() == current_suit:
                            if RANKS_CONVERTER[hand.get_deadwood()[index2].get_rank()] == head_rank - 1:
                                head_rank -= 1
                                hand.change_lay_off_meld_num(index2 + len(hand.get_melds()), self.cards[i].get_meld_num())
                                lay_off_message_display = True
            i = j
    
    # lay off the cards according to their lay_off_meld_num
    def lay_off(self, receiver_hand):
        for i in range(len(self.cards) - 1, len(self.melds) - 1, -1):
            if self.cards[i].get_lay_off_meld_num() != -1:
                head = 0
                while receiver_hand.get_card(head).get_meld_num() != self.cards[i].get_lay_off_meld_num():
                    head += 1
                tail = head
                while receiver_hand.get_card(tail).get_meld_num() == self.cards[i].get_lay_off_meld_num():
                    tail += 1
                # insert the card into the meld in receiver_hand that has the same lay_off_meld_num
                receiver_hand.insert_card(tail, self.discard(i))
                # sort the specific meld in receiver_hand by rank then suit
                receiver_hand.sort_by_rank(head, tail + 1)

        self.sort() # update itself to calc the new deadwood value
    
    def get_melds(self):
        return self.melds
    
    def get_deadwood(self):
        return self.deadwood
    
    def get_card(self, index):
        return self.cards[index]
    
    def get_cards(self):
        return self.cards

# define deck class 
class Deck:
    def __init__(self):
        self.cards = []
    
    def __str__(self):
        s = ''
        for card in self.cards:
            s += str(card) + ' '
        return s
    
    def add_card(self, new_card):
        self.cards.append(new_card)
    
    # draw the image of the stock pile
    def draw_stock_pile(self, canvas, pos):
        global stock_first_card_pos
        
        # draw_card_num is the number of card backs drawn on the screen
        # for the stock pile
        if len(self.cards) >= 10:
            draw_card_num = 10 # only draw 10 cards on the screen if the pile has more than 10 cards
        else:
            draw_card_num = len(self.cards)
        
        # the position of the top card in the stock pile drawn on the screen
        stock_first_card_pos = [pos[0] - (draw_card_num - 1) * 2,
                                pos[1] - (draw_card_num - 1) * 2]
        
        for i in range(draw_card_num):
            canvas.draw_image(card_back, CARD_BACK_CENTER_ORIGINAL,
                              CARD_BACK_SIZE_ORIGINAL, 
                              [pos[0] - i * 2 + CARD_CENTER[0], 
                               pos[1] - i * 2 + CARD_CENTER[1]],
                              CARD_SIZE)
    
    # draw the image of the discard pile / knock pile
    def draw_discard_or_knock_pile(self, canvas, pos):
        if self.cards != []:
            self.cards[-1].draw(canvas, pos)
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal_card(self):
        # Use index - 1 to get the last card
        # in the list and .pop() to return it
        if self.cards != []:
            return self.cards.pop(-1)
    
    def last_card(self):
        return self.cards[-1]
    
    def get_card_num(self):
        return len(self.cards)

# checks if the computer wants the face-up card from the discard pile
def computer_draw_from_discard():    
    global computer_hand, message1, message2, decline_round, deadwood_value, computer_draw, temp_card
    global animation_draw_from_discard, animated_card_draw, animated_card_discard, discard_pile
    
    deadwood_value_current = computer_hand.calc_deadwood_value()
    face_up_card = discard_pile.last_card()
    # computer_hand_trial is a replicate of computer_hand testing to see if the computer wants
    # the card or not by taking the face-up card and discarding the largest deadwood value and 
    # checking if the new deadwood value is smaller
    computer_hand_trial = Hand()
    computer_hand.replicate(computer_hand_trial)
    computer_hand_trial.add_card(face_up_card)
    computer_hand_trial.sort()
    if len(computer_hand_trial.get_deadwood()) > 0:
        discarded_card = computer_hand_trial.discard(-1)
        computer_hand_trial.sort()
        deadwood_value = computer_hand_trial.calc_deadwood_value()
    else:
        deadwood_value = 110
        for card in computer_hand_trial.get_cards():
            computer_hand_trial2 = Hand()
            computer_hand_trial.replicate(computer_hand_trial2)
            computer_hand_trial2.discard(computer_hand_trial2.find_index(card))
            computer_hand_trial2.sort()
            deadwood_value_trial = computer_hand_trial2.calc_deadwood_value()
            if deadwood_value_trial < deadwood_value:
                discarded_card = card
                deadwood_value = deadwood_value_trial
    
    if deadwood_value < deadwood_value_current: # then take the card
        computer_draw = False
        animated_card_draw = discard_pile.deal_card()
        animated_card_draw.set_pos(DISCARD_PILE_POS)
        animated_card_draw.set_vel(ANIMATION1_VEL)
        computer_hand.add_card(animated_card_draw)
        animated_card_discard = computer_hand.discard(computer_hand.find_index(discarded_card))
        animated_card_discard.set_pos(COMPUTER_HAND_CENTER)
        animated_card_discard.set_vel(ANIMATION3_VEL)
        computer_hand.sort()
        # initiate the animation
        animation_draw_from_discard = True
    elif decline_round:
        message1 = 'CPU declines'
        message2 = 'Please draw a card'

# computer draws a card from the stock and discards a card from its hand
def computer_draw_from_stock():
    global computer_hand, deck, deadwood_value, stock_first_card_pos
    global animation_draw_from_stock, animated_card_draw, animated_card_discard, computer_draw
    
    computer_draw = False
    temp_card = deck.deal_card()
    computer_hand.add_card(temp_card)
    animated_card_draw = Card(temp_card.get_suit(), temp_card.get_rank())
    computer_hand.sort()
  
    animated_card_draw.set_pos(stock_first_card_pos)
    animated_card_draw.set_vel(ANIMATION2_VEL)
    if len(computer_hand.get_deadwood()) > 0:
        temp_card = computer_hand.discard(-1)
    else:    
        deadwood_value = 110
        for card in computer_hand.get_cards():
            computer_hand_trial = Hand()
            computer_hand.replicate(computer_hand_trial)
            computer_hand_trial.discard(computer_hand_trial.find_index(card))
            computer_hand_trial.sort()
            deadwood_value_trial = computer_hand_trial.calc_deadwood_value()
            if deadwood_value_trial < deadwood_value:
                temp_card = card
                deadwood_value = deadwood_value_trial
        computer_hand.discard(computer_hand.find_index(temp_card))
    animated_card_discard = Card(temp_card.get_suit(), temp_card.get_rank())
    animated_card_discard.set_pos(COMPUTER_HAND_CENTER)
    animated_card_discard.set_vel(ANIMATION3_VEL)
    computer_hand.sort()
    deadwood_value = computer_hand.calc_deadwood_value()
        
    # initiate the animation
    animation_draw_from_stock = True
            
def deal():
    global player_hand, computer_hand, deck, discard_pile, message1, message2, round_num
    global player_draw, player_discard, computer_draw, knock_pile, message3, in_play, message4, message5
    global card_popped, decline_round, knock_message_display, lay_off_message_display, short_of_card
    global score_display_initiator, score_display, computer_knock, player_knock, drawing_from_discard
    
    # initialization
    card_popped = False
    decline_round = True
    knock_message_display = False
    lay_off_message_display = False
    score_display_initiator = False
    score_display = False
    computer_knock = False
    player_knock = False
    drawing_from_discard = False
    short_of_card = False
    
    round_num += 1
    if round_num == 2:
        message4 = ''
        message5 = ''
    
    player_hand = Hand()
    computer_hand = Hand()
    
    deck = Deck()
    # fill the deck with all 52 cards
    for suit in SUITS:
        for rank in RANKS:
            deck.add_card(Card(suit, rank))
    deck.shuffle()
    
    for i in range(10):
        player_hand.add_card(deck.deal_card())
        computer_hand.add_card(deck.deal_card())
    player_hand.sort()
    computer_hand.sort()
    
    discard_pile = Deck()
    knock_pile = Deck()
    discard_pile.add_card(deck.deal_card())
    
    message1 = "Decline or take"
    message2 = "the face-up card?"
    message3 = ''
    
    in_play = True
    player_draw = True
    player_discard = False
    computer_draw = False

def draw_and_discard(pos):
    global message1, message2, message3, player_hand, player_draw, player_discard, discard_pile, deck, card_popped, player_knock
    global card_popped_num, decline_round, computer_draw, knock_message_display, knock_pile, drawn_card_from_discard, drawing_from_discard
    global in_play, short_of_card
    
    # start a new round when there are only two cards left in the stock pile
    if short_of_card:
        short_of_card = False
        deal()
        return
    
    if in_play:
        # pop the card out if the mouse clicks on a card and there is no card currently popped out
        if not card_popped:
            card_popped_num = player_hand.check_clicked_card_index(pos)
            if card_popped_num != 'No Match Found':
                if player_discard:
                    player_hand_trial = Hand()
                    player_hand.replicate(player_hand_trial)
                    player_hand_trial.discard(card_popped_num)
                    player_hand_trial.sort()
                    player_deadwood_val_trial = player_hand_trial.calc_deadwood_value()
                    if player_deadwood_val_trial <= 10:
                        knock_message_display = True
                player_hand.change_pop_status(card_popped_num)
                card_popped = True
                return

        # reorganize the card if a card is already popped out and the mouse clicks on another card
        if card_popped:
            card_insert_num = player_hand.check_clicked_card_index(pos)
            if card_insert_num != 'No Match Found':
                knock_message_display = False
                player_hand.change_pop_status(card_popped_num)
                card_popped = False
                player_hand.reorganize_card(card_insert_num, card_popped_num)
                if player_draw:
                    message1 = 'Please click either'
                    message2 = 'pile to draw a card!'
                    message3 = ''
                elif player_discard:
                    message1 = 'Please click on'
                    message2 = 'a card from your'
                    message3 = 'hand to discard!'
                else:
                    message1 = 'Waiting for the'
                    message2 = 'the other player...'
                    message3 = ''
                return

        # the player draws if the mouse clicks on the discard or the stock pile
        if player_draw:
            # discard pile
            if click_on_card(pos, DISCARD_PILE_POS, CARD_SIZE):
                if card_popped:
                    message1 = 'Please click the'
                    message2 = 'card again to put'
                    message3 = 'it down!'
                else:
                    drawing_from_discard = True
                    drawn_card_from_discard = discard_pile.deal_card()
                    player_hand.add_card(drawn_card_from_discard)
                    message1 = 'Please click on'
                    message2 = 'a card from your'
                    message3 = 'hand to discard!'
                    player_draw = False
                    player_discard = True
                    if decline_round:
                        decline_round = False
                return

            if decline_round and not card_popped: # the player can only draw from the stock pile
                                                  # after declining / drawing the first face-up card
                message1 = "Decline or take"
                message2 = "the face-up card?"
                message3 = ''
            elif click_on_card(pos, stock_first_card_pos, CARD_SIZE): # stock pile
                if card_popped:
                    message1 = 'Please click the'
                    message2 = 'card again to put'
                    message3 = 'it down!'
                else:
                    if deck.get_card_num() == 2:
                        in_play = False
                        short_of_card = True
                        message1 = 'No More Cards'
                        message2 = 'Click to start'
                        message3 = 'a new round'
                    else:
                        drawing_from_discard = False
                        player_hand.add_card(deck.deal_card())
                        message1 = 'Please click on'
                        message2 = 'a card from your'
                        message3 = 'hand to discard!'
                        player_draw = False
                        player_discard = True
                return

        # the player discards if he clicks on it and it is his turn to discard a card
        if player_discard:
            if card_popped:
                if knock_message_display:
                    if click_on_card(pos, KNOCK_CARD_POS, CARD_SIZE):
                        knock_pile.add_card(player_hand.discard(card_popped_num))
                        player_knock = True
                        knock()
                        return

                if click_on_card(pos, DISCARD_PILE_POS, CARD_SIZE):
                    if drawing_from_discard:
                        if player_hand.get_card(card_popped_num) == drawn_card_from_discard:
                            message1 = 'Card from discard'
                            message2 = "pile can't be dis-"
                            message3 = 'carded right away!'
                            return
                    knock_message_display = False
                    discard_pile.add_card(player_hand.discard(card_popped_num))
                    card_popped = False
                    message1 = 'Waiting for the'
                    message2 = 'other player...'
                    message3 = ''
                    player_discard = False
                    computer_draw = True

                    # computer's turn
                    computer_draw_from_discard()
                    if computer_draw:
                        if deck.get_card_num() == 2:
                            in_play = False
                            short_of_card = True
                            message1 = 'No More Cards'
                            message2 = 'Click to start'
                            message3 = 'a new round'
                        else:   
                            computer_draw_from_stock()
                else:
                    message1 = 'Please click on the dicard'
                    message2 = 'pile to discard!'
                    message3 = ''
            else:
                message1 = 'Please click on'
                message2 = 'a card from your'
                message3 = 'hand to discard!'

# when the player hits "decline", it is the computer's turn to decide whether or not
# to take the face-up card
def decline():
    global player_draw, decline_round
    
    if decline_round:
        computer_draw_from_discard()
        decline_round = False
        player_draw = True
        
def knock(): 
    global message1, message2, message3, player_deadwood_val, computer_deadwood_val, val_diff
    global in_play, score_display, score_display_initiator, player_score, computer_score
    
    in_play = False
    
    player_hand.sort()
    player_deadwood_val = player_hand.calc_deadwood_value()
    computer_deadwood_val = computer_hand.calc_deadwood_value()
    
    if player_knock and player_deadwood_val > 0: # no lay-off if the player goes gin
        player_hand.check_if_laid_off(computer_hand)
    elif computer_knock and computer_deadwood_val > 0: # no lay_off if the computer goes gin
        computer_hand.check_if_laid_off(player_hand)
        
    if lay_off_message_display:
        if computer_knock:
            message1 = "Computer knocked"
            message2 = 'PRESS SPACE'
            message3 = 'TO LAY OFF'
        else:
            message1 = 'PRESS SPACE'
            message2 = 'TO LAY OFF'
            message3 = ''
    else:
        if computer_knock:
            val_diff = player_deadwood_val - computer_deadwood_val
            message1 = 'Computer knocked'
            message2 = 'Press S to view'
            message3 = 'the scores'
            # update scores
            score = score_update(computer_score, player_score, computer_deadwood_val, player_deadwood_val, val_diff)
            computer_score = score[0]
            player_score = score [1]
        else:
            val_diff = computer_deadwood_val - player_deadwood_val
            message1 = 'Press S to view'
            message2 = 'the scores'
            message3 = ''
            # update scores
            score = score_update(player_score, computer_score, player_deadwood_val, computer_deadwood_val, val_diff)
            player_score = score[0]
            computer_score = score[1]
        score_display_initiator = True

# Space - lay off
# S - View Scores
# C - Continue to next round or game over page
def key_handler(key):
    global lay_off_message_display, message1, message2, message3, score_display, score_display_initiator
    global player_deadwood_val, computer_deadwood_val, val_diff, player_score, computer_score, in_play, game_over
    
    if key == simplegui.KEY_MAP['space']: # lay off cards
        if lay_off_message_display:
            lay_off_message_display = False
            if computer_knock:
                player_hand.lay_off(computer_hand)
                player_deadwood_val = player_hand.calc_deadwood_value()
                val_diff = player_deadwood_val - computer_deadwood_val
                # update scores
                score = score_update(computer_score, player_score, computer_deadwood_val, player_deadwood_val, val_diff)
                computer_score = score[0]
                player_score = score [1]
            else:
                computer_hand.lay_off(player_hand)
                computer_deadwood_val = computer_hand.calc_deadwood_value()                
                val_diff = computer_deadwood_val - player_deadwood_val
                # update scores
                score = score_update(player_score, computer_score, player_deadwood_val, computer_deadwood_val, val_diff)
                player_score = score[0]
                computer_score = score[1]
                
            message1 = 'Press S to view'
            message2 = 'the scores'
            message3 = ''
            score_display_initiator = True  
            return
    
    if key == simplegui.KEY_MAP['S']: # view scores
        if score_display_initiator:
            message1 = ''
            message2 = ''
            message3 = ''
            score_display = True
            return
    
    if key == simplegui.KEY_MAP['C']: # continue... next round or game over
        if score_display:
            if player_score >= 100 or computer_score >= 100:
                score_display = False
                game_over = True
            else:
                deal()
    
def sort():
    global player_hand
    
    # player's hand gets sorted when the Sort button is hit
    player_hand.sort()

def draw_handler(canvas):
    global animation_draw_from_discard, animation_draw_from_stock, animation_discard		
    global player_draw, discard_pile, message1, message2, message3, knock_pile, computer_knock
    
    # player's and computer's hands    
    canvas.draw_text("You (" + str(player_score) + ")", [80, 430], 24, "white")
    player_hand.draw(canvas, PLAYER_HAND_POS)
    
    canvas.draw_text("Computer (" + str(computer_score) + ")", [80, 50], 24, "white")
    if not in_play: # only show the computer hand when the round is over
        computer_hand.draw(canvas, COMPUTER_HAND_POS)
    
    # messages
    canvas.draw_text(message1, [20, 290], 20, "white")
    canvas.draw_text(message2, [20, 320], 20, "white")
    canvas.draw_text(message3, [20, 350], 20, "white")
    canvas.draw_text(message4, [225, 50], 16, "white")
    canvas.draw_text(message5, [225, 70], 16, 'white')
    
    deck.draw_stock_pile(canvas, STOCK_PILE_POS)
    discard_pile.draw_discard_or_knock_pile(canvas, DISCARD_PILE_POS)
    
    canvas.draw_text('Round ' + str(round_num), [500, 30], 24, 'white')
    
    # Draw the knock text and grey rectangle
    if knock_message_display:
        canvas.draw_text('KNOCK?', [450, 240], 20, 'white')
        canvas.draw_polygon([KNOCK_CARD_POS, 
                             [KNOCK_CARD_POS[0], KNOCK_CARD_POS[1] + CARD_SIZE[1]],
                             [KNOCK_CARD_POS[0] + CARD_SIZE[0],
                              KNOCK_CARD_POS[1] + CARD_SIZE[1]],
                             [KNOCK_CARD_POS[0] + CARD_SIZE[0], KNOCK_CARD_POS[1]]],
                            1, 'grey', 'grey')
        
    knock_pile.draw_discard_or_knock_pile(canvas, KNOCK_CARD_POS)
    
    # Display the score board for each round
    if score_display:
        canvas.draw_polygon([[50, 220], [50, 400], [550, 400], [550, 220]],
                            1, '#663300', '#663300')
        canvas.draw_text('Your Deadwood Value = ' + str(player_deadwood_val), [60, 240], 20, 'white')
        canvas.draw_text("Computer's Deadwood Value = " + str(computer_deadwood_val), [60, 270], 20, 'white')
        
        if computer_knock:
            if computer_deadwood_val == 0:
                canvas.draw_text("Computer knocked and it went GIN (deadwood = 0)", [60, 300], 20, 'white')
                if player_deadwood_val == 0:
                    canvas.draw_text("But you undercut (deadwood also = 0)", [60, 330], 20, 'white')
                    canvas.draw_text('Your Score = 0(10) = 10', [60, 360], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 390], 20, 'white')
                else:
                    canvas.draw_text("Computer's Score = " + str(val_diff) + '(20) = ' + str(val_diff + 20),
                                     [60, 330], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 360], 20, 'white')
            else:
                canvas.draw_text("Computer knocked", [60, 300], 20, 'white')
                if val_diff > 0:
                    canvas.draw_text("Computer's Score = " + str(val_diff), [60, 330], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 360], 20, 'white')
                elif player_deadwood_val != 0:
                    canvas.draw_text('But the player undercut!', [60, 330], 20, 'white')
                    canvas.draw_text('Your Score = ' + str(-val_diff) + '(10) = ' + str(-val_diff + 10),
                                     [60, 360], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 390], 20, 'white')
                else:
                    canvas.draw_text('But the player undercut and went GIN!', [60, 330], 20, 'white')
                    canvas.draw_text('Your Score = ' + str(-val_diff) + '(20)(10) = ' + str(-val_diff + 30),
                                     [60, 360], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 390], 20, 'white')
        else:
            if player_deadwood_val == 0:
                canvas.draw_text('You knocked and you went GIN (deadwood = 0)', [60, 300], 20, 'white')
                if computer_deadwood_val == 0:
                    canvas.draw_text('But the computer undercut (deadwood also = 0)', [60, 300], 20, 'white')
                    canvas.draw_text("Computer's Score  = 0(10) = 10", [60, 360], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 390], 20, 'white')
                else:
                    canvas.draw_text("Your Score = " + str(val_diff) + '(20) = ' + str(val_diff + 20),
                                     [60, 330], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 360], 20, 'white')
            else:
                canvas.draw_text("You knocked", [60, 300], 20, 'white')
                if val_diff > 0:
                    canvas.draw_text("Your Score = " + str(val_diff), [60, 330], 20, 'white')
                    canvas.draw_text("Press C to Continue", [60, 360], 20, 'white')
                elif computer_deadwood_val != 0:
                    canvas.draw_text('But the computer undercut!', [60, 330], 20, 'white')
                    canvas.draw_text("Computer's Score = " + str(-val_diff) + '(10) = ' + str(-val_diff + 10),
                                     [60, 360], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 390], 20, 'white')
                else:
                    canvas.draw_txt('But the computer undercut and went GIN!', [60, 330], 20, 'white')
                    canvas.draw_text("Computer's Score = " + str(-val_diff) + '(20)(10) = ' + str(-val_diff + 30),
                                     [60, 360], 20, 'white')
                    canvas.draw_text('Press C to Continue', [60, 390], 20, 'white')
    
    # Display the final scores
    if game_over:
        if player_score >= 100 or computer_score >= 100:
            canvas.draw_polygon([[50, 220], [50, 400], [550, 400], [550, 220]],
                                1, '#663300', '#663300')
            if player_score >= 100:
                canvas.draw_text('You won the game!', [60, 240], 20, 'white')
                if computer_score != 0:
                    canvas.draw_text("Your Final Score: " + str(player_score) + '(200) = ' + str(player_score + 200), 
                                     [60, 270], 20, 'white')
                    canvas.draw_text("Computer's Final Score: " + str(computer_score) + '(100) = ' + str(computer_score + 100),
                                     [60, 300], 20, 'white')
                    canvas.draw_text('Hit the New Game button to start a new game', [60, 330], 20, 'white')
                else:
                    canvas.draw_text("Your Final Score: " + str(player_score) + '(300) = ' + str(player_score + 300),
                                     [60, 270], 20, 'white')
                    canvas.draw_text("Computer's Final Score: " + str(computer_score), [60, 300], 20, 'white')
                    canvas.draw_text('Hit the New Game button to start a new game', [60, 330], 20, 'white')
            else:
                canvas.draw_text('Computer won the game!', [60, 240], 20, 'white')
                if player_score != 0:
                    canvas.draw_text("Computer's Final Score: " + str(computer_score) + '(200) = ' + str(computer_score + 200),
                                     [60, 270], 20, 'white')
                    canvas.draw_text("Your Final Score: " + str(player_score) + '(100) = ' + str(player_score + 100),
                                     [60, 300], 20, 'white')
                    canvas.draw_text('Hit the New Game button to start a new game', [60, 330], 20, 'white')
                else:
                    canvas.draw_text("Computer's Final Score: " + str(computer_score) + '(300) = ' + str(computer_score + 300),
                                     [60, 270], 20, 'white')
                    canvas.draw_text('Your Final Score: ' + str(player_score), [60, 300], 20, 'white')
                    canvas.draw_text('Hit the New Game button to start a new game', [60, 330], 20, 'white')
    
    
    # animation for card drawn from discard pile to the computer hand
    if animation_draw_from_discard:
        if animated_card_draw.get_pos()[1] > COMPUTER_HAND_CENTER[1]:
            animated_card_draw.draw(canvas, animated_card_draw.get_pos())
            animated_card_draw.update()
        else:
            animation_draw_from_discard = False
            animation_discard = True
    
    # animation for card drawn from stock pile to the computer hand
    if animation_draw_from_stock:
        if animated_card_draw.get_pos()[1] > COMPUTER_HAND_CENTER[1]:
            canvas.draw_image(card_back, CARD_BACK_CENTER_ORIGINAL,
                              CARD_BACK_SIZE_ORIGINAL, 
                              [animated_card_draw.get_pos()[0] + CARD_CENTER[0],
                               animated_card_draw.get_pos()[1] + CARD_CENTER[1]],
                              CARD_SIZE)
            animated_card_draw.update()
        else:
            animation_draw_from_stock = False
            animation_discard = True
    
    # animation for card discarded from computer hand to the discard pile
    if animation_discard:
        if animated_card_discard.get_pos()[1] < DISCARD_PILE_POS[1]:
            animated_card_discard.draw(canvas, animated_card_discard.get_pos())
            animated_card_discard.update()
        else:
            animation_discard = False
            if deadwood_value <= 10:
                message1 = 'Computer knocks!'
                message2 = ''
                message3 = ''
                knock_pile.add_card(animated_card_discard)
                computer_knock = True
                knock()
            else:
                discard_pile.add_card(animated_card_discard)
                message1 = 'Please click to'
                message2 = 'draw a card!'
                message3 = ''
                player_draw = True        

# initialize frame
frame = simplegui.create_frame("Gin Rummy", 600, 600)
frame.set_canvas_background("#019930")

# create buttons and callbacks
frame.add_button("New Game", new_game, 200)
frame.add_button("Decline",  decline, 200)
frame.add_button("Sort", sort, 200)
frame.add_label("Rules: http://www.pagat.com", 200)
frame.add_label("/rummy/ginrummy.html", 200)
frame.add_label("How to Start:", 200)
frame.add_label("If you don't want the faced-up card on the left, hit the Decline button", 200)
frame.add_label("Otherwise, click on the card on the left and discard a card from your pile", 200)
frame.add_label("Draw a card: single click on either the stock (right) or discard (left) pile", 200)
frame.add_label("Discard a card: single click on the card and then click on the discard pile", 200)
frame.add_label("Reorganize cards: single click on a card and then click another card - the first will be placed before the second card", 200)
frame.add_label("Knock: discard the card inside the grey rectangle when 'KNOCK?' appears", 200)
frame.add_label("The Game Ends Once a Player Has More Than 100 Points", 200)
frame.set_mouseclick_handler(draw_and_discard)
frame.set_keydown_handler(key_handler)
frame.set_draw_handler(draw_handler)

# get things rolling
player_hand = Hand()
computer_hand = Hand()
new_game()
frame.start()