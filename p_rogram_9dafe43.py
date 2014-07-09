#import numpy as np
import logging
from random import randint
import scipy.stats as stats
#from sklearn.cluster import DBSCAN
#from sklearn import metrics
#from sklearn.preprocessing import StandardScaler
from collections import namedtuple
# http://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html#example-cluster-plot-dbscan-py

def get_play(me,hands,h_str) :
    self = get_play
    logging.debug("/\\/\\/\\/\\/\\/\\/\\/\\/\\STOOGE/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\")
    if not hasattr(self, "players"):
        self.players = {}
        self.game = None
        self.bid = namedtuple('bid',['quant','face'])
        self.player_bid = namedtuple('player_bid',['player','bid'])
        self.liar = self.bid(0,0)
    logging.debug(hands)
    #parse history for this game h_srt => history_list[] - find round number
    history_list = []
    round_num = 1 #first round
    if len(h_str) > 0: #if not the openning bid
        for player_quant_face in h_str.split(','):
            player, quant_face = player_quant_face.split(':')
            quant, face =  int(quant_face) // 10, int(quant_face) % 10
            history_list.append(self.player_bid(player, self.bid(quant,face)))
            if player == me:
                round_num += 1 
    logging.debug("Round number: %i" % round_num)
    total_dice = 0
    my_hand = None
    for hand in hands.split(','): 
        player, dice = hand.split(':')
        total_dice += len(dice)
        if player == me :
            my_hand = dice
    if round_num == 1:
        self.game = game(self.bid)
        self.game.prev_turn = 0
    self.game.round_num = round_num
    self.game.my_hand = my_hand
    self.game.total_dice= total_dice
    self.game.history_list = history_list
    self.game.add_round(history_list[self.game.prev_turn:-1])
    if history_list:
        opposing_bid = history_list[-1].bid
        if opposing_bid.quant == 0:
            logging.debug("showdown!")
            return 0 #showdown
    else: #openning bid
        logging.debug("openning bid!") #bid 1 of a random face in hand
        return(10 + int(my_hand[randint(0,len(my_hand)-1)]))
    logging.debug("Opposing bid: %i %i" % (opposing_bid.quant,opposing_bid.face))
           
    sticky_bid = self.bid(opposing_bid.quant + 1, opposing_bid.face)
    risks = {}
    logging.debug("getting risk for liar")
    risks[self.liar] = 1 - self.game.hand_risk(opposing_bid)
    logging.debug("getting risk for sticky bid %i %i" % (sticky_bid.quant,sticky_bid.face))
    risks[sticky_bid] = self.game.hand_risk(sticky_bid)
    logging.debug("getting risks for increased faces")
    for face in range(1,opposing_bid.face+1):
        logging.debug("Face %i" % face)
        proposed_bid = self.bid(opposing_bid.quant + 1, face)
        risks[proposed_bid] = self.game.hand_risk(proposed_bid)   
    logging.debug("getting risks for increased quantities")
    if opposing_bid.face < 6:
        for face in range(opposing_bid.face + 1, 7):
            logging.debug("Face %i" % face)
            proposed_bid = self.bid(opposing_bid.quant, face)
            risks[proposed_bid] = self.game.hand_risk(proposed_bid) 
    logging.debug(risks)

    best_bid = min(risks, key=risks.get)
    
    logging.debug("best bid: %i %i" % (best_bid.quant,best_bid.face))
   
    # if sticking with the face is similar in risk to the best bid, just stay 
    # with the same face, but only if the naive risk < .5 for the sticky bid
    if self.game.naive_risk(sticky_bid) < .5:
        logging.debug("considering sticky bid")
        if risks[best_bid] < (risks[sticky_bid] + .02):
            logging.debug ("Chose sticky bid! %i %i" % (sticky_bid.quant,sticky_bid.face))
            best_bid = sticky_bid

    # if we're aobut to call liar, but the risk of doing so is likely to
    # lose, we should bluff instead of calling liar            
    if best_bid is self.liar and (risks[self.liar] < .5 or opposing_bid.quant == 1):
        logging.debug("reconsidering liar")
        del risks[self.liar]
        proposed_bid = min(risks, key=risks.get)
        logging.debug("Considering %i %i instead of Liar" % proposed_bid)
        if risks[proposed_bid] < .5:
            best_bid = proposed_bid
            logging.debug("chose a new low risk bid %i %i" % (best_bid.quant,best_bid.face))
    
    return(best_bid.quant * 10 + best_bid.face)

def at_least_risk(dice,quant):
    if quant < 1:
        return 0.0
    if quant > dice:
        return 1.0
    p = 1.0/6.0
    risk = stats.binom.cdf(quant - 1, dice, p)
    logging.debug("Quant: %i Dice: %i Risk: %.3f p: %.3f" % (quant,dice,risk,p) )
    return risk
        
class player():
    """the player - persists through tournament"""
    pass
    #this is where I will learn about a player

class game():
    """the game"""
    
    def __init__(self,bid_object):
        #instance attributes
        self.bid = bid_object
        self.my_hand = None
        self.prev_turn = 0
        self.round_num = 0
        self.total_dice = 0
        self.history_list=[]
        
    def add_round(self, round_history_list):
        pass
    
    def naive_risk(self, bid):
        return(at_least_risk(self.total_dice,bid.quant))

    def hand_risk(self, bid):
        hand_dice = self.total_dice - len(self.my_hand)
        hand_quant = bid.quant - self.my_hand.count(str(bid.face))
        return(at_least_risk(hand_dice,hand_quant))
        
    def next_risk(self, bid):
        return self.hand_risk(bid)
    
    def pool_risk(self, bid):
        return self.hand_risk(bid)
    
    def quant_risk(self, quant):
        return(at_least_risk(self.total_dice,quant))  