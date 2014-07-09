# ben_player3.py 
#from sklearn.naive_bayes import MultinomialNB as Model
from sklearn.linear_model import LogisticRegression as Model

import itertools, random, logging, operator as op
import numpy as np
###############################################################################
## Helper Functions
###############################################################################

def find_last_bid(history):
    if 0 == len(history) :
        return 10
    else :
        return int(history.split(',')[-1].split(':')[1])

def nCr(n,r):
    """ nCr """
    r = min(r, n-r)
    if r == 0: return 1.0
    try:
        numer = reduce(op.mul, xrange(n, n-r, -1))
        denom = reduce(op.mul, xrange(1, r+1))
    except:
        numer, denom = 1, 1
    return float(numer//denom)

def exact_odds(n,q):
    """for a given number of unknown dice n, the probability that
    exactly a certain quantity q of any face value are showing"""
    return float(nCr(n,q) * (1.0/6)**q * (5.0/6)**(n-q))

def odds(n,x):
    "the odds of an x face roll give n unknown dice"
    return sum([exact_odds(n,x) for x in range(x,n+1)])

def naive_odds(uk_dice, my_faces, bid):
    "odds given a unknown dice, the # of faces known, and the bid"
    if bid <= my_faces:
        return 1.0
    else:
        return odds(uk_dice, bid - my_faces)

def parse_hand(raw_hand):
    "parse hand into a dict of faces and counts"
    hand = {n:0 for n in range(1,6+1)}
    for face in raw_hand:
        hand[int(face)] += 1
    return hand

def find_candidates(last_bid):
    "finds the next 6 possible bids given a bid"
    candidates = []
    for x in range(1,6+1):
        if last_bid % 10 < 6:
            last_bid += 1
            candidates.append(last_bid)
        else:
            last_bid = (last_bid // 10) * 10 + 11
            candidates.append(last_bid)
    return candidates

def combine_probs(prob):
    """Takes a list of dicts--
    the keys in each dict should be the possible values
    the values in each dict should be the probablility of its key
    returns a dict of the combined values and probabilities"""
    result_set = [x.keys() for x in prob]
    prob_set = [x.values() for x in prob]
    combinations = [sum(x) for x in list(itertools.product(*result_set))]
    probabilities = [reduce(op.mul,x) for x in list(itertools.product(*prob_set))]
    comb_prob = zip(combinations, probabilities)
    values = range(0,max(combinations)+1)
    return dict([(y, sum([x[1] for x in comb_prob if x[0] == y])) for y in values])

def iter_combine(prob):
    """speed up combination of large number of dice"""
    combined_prob = prob[0]
    for n in range(1, len(prob)):
        combined_prob = combine_probs([combined_prob, prob[n]])
    return combined_prob  

def get_face_probs(model, data, player_dice, from_face):
    cat_data = []
    X_data = []
    faces = [data[from_face]]
    other_faces = [data[x] for x in data.keys() if x != from_face]
    faces.extend(sorted(other_faces, reverse=True))
    faces.append(player_dice)
    pre = model.predict_proba([faces])
    pre = {x:pre[0][x] for x in range(0, len(pre[0]))}
    sum_possible = sum([pre[x] for x in pre if x in range(player_dice+1)])
    new_pre = {}
    for x in pre:
        if x in range(player_dice+1):
            new_pre[x] = pre[x]/sum_possible
        else:
            new_pre[x] = 0
    return new_pre

def combined_odds(models, player_bids, from_face, players_dice, my_hand, bid_size):
    player_odds = []
    for player in players_dice:
        if player in player_bids and player in models:
            player_odds.append(get_face_probs(models[player],
                                                 player_bids[player],
                                                 players_dice[player],
                                                 from_face))
        else:
            player_odds.append({face: exact_odds(players_dice[player], face) for face in range(0,6+1)})
    my_faces = my_hand[from_face]
    hand = {h:0.0 for h in range(0,6+1)}
    hand[my_faces] = 1.0
    player_odds.append(hand)
    combined_exact = iter_combine(player_odds)
    return sum([combined_exact[x] for x in combined_exact if x >= bid_size])

def determine_next_bid(last_bid, my_hand, uk_dice, r, player_dice):
    hand = parse_hand(my_hand)
    candidates = find_candidates(last_bid)
    if uk_dice <= 18:
        can_probs = {x: combined_odds(r.models, r.player_bid, x%10, player_dice, hand, x//10) for x in candidates}
    else:
        can_probs = {x: naive_odds(uk_dice, hand[x%10], x//10) for x in candidates}
    if last_bid >= 11:
        for bid in can_probs:
            if bid%10 == last_bid%10:
                can_probs[bid] = can_probs[bid] * 1
        can_probs[0] = (1.0 - combined_odds(r.models, r.player_bid, last_bid%10, player_dice, hand, last_bid//10))
    max_prob = max(can_probs.iteritems(), key=op.itemgetter(1))
    equal_choices = [c for c in can_probs.keys() if can_probs[c] == max_prob[1]]
    max_side = max(hand.iteritems(), key=op.itemgetter(1))
    min_prob = min(can_probs.iteritems(), key=op.itemgetter(1))
    if min(equal_choices) == 0 and r.last_player != '':
        if player_dice[r.last_player] > player_dice[r.next_player] and r.last_player != r.next_player:
            out_put = max_side[1]*10 + max_side[0] + (uk_dice//6)*10
        else:
            out_put = 0
    elif r.last_player != '' \
        and len(player_dice) > 5 \
        and max_prob[1] == 1.0 \
        and uk_dice*1.0 / (len(player_dice)-1) < 5.0 \
        and player_dice[r.next_player]*1.0 // uk_dice < 0.5:
            out_put = max_side[1]*10 + max_side[0] + (uk_dice//6)*10
    else:
            out_put = min(equal_choices)
    return out_put

def determine_next_bid_naive(last_bid, my_hand, uk_dice):
    hand = parse_hand(my_hand)
    candidates = find_candidates(last_bid)
    can_probs = {x: naive_odds(uk_dice, hand[x%10], x//10) for x in candidates}
    if last_bid >= 11:
        for bid in can_probs:
            if bid%10 == last_bid%10:
                can_probs[bid] = can_probs[bid] * 1.5
        can_probs[0] = 1.0 - naive_odds(uk_dice, hand[last_bid%10], last_bid//10)
    my_prob = max(can_probs.iteritems(), key=op.itemgetter(1))
    equal_choices = [c for c in can_probs.keys() if can_probs[c] == my_prob[1]]
    max_side = max(hand.iteritems(), key=op.itemgetter(1))
    if 0 == max(equal_choices):
        out_put = max_side[1] + max_side[0] + (uk_dice//7)*10
    else:
        out_put = min(equal_choices)
    return out_put

def parse_data_to_players(data):
    players = data[0].keys()
    data_dict = {}
    cat_data = {}
    X_data = {} 
    for player in players:
        data_dict[player] = []
        for bid in data[1]:
            if bid[0] == player:
                if player in data[0].keys():
                    data_dict[player].append([data[0][player], bid[1]])
        cat_data[player] = []
        X_data[player] = []
        for from_face in range(1,6+1):
            for d in data_dict[player]:
                num_face = d[0][from_face]
                player_dice = sum(d[0].values())
                faces = [d[1][from_face]]
                other_faces = [d[1][x] for x in d[1].keys() if x != from_face]
                faces.extend(sorted(other_faces, reverse=True))
                faces.append(player_dice)
                cat_data[player].append(num_face)
                X_data[player].append(faces)
    return  X_data, cat_data, players

class Record(object):
    def __init__(self, players, me):
        self.players = players
        self.me = me
        self.dataset = []
        self.ld = 0
        self.games = 0
        self.X = {x:[] for x in players}
        self.y = {x:[] for x in players}
        self.models = {}
        self.player_bid = {}
        self.last_train = 0
        self.order = []
        self.next_player = ''
        self.last_player = ''

    def record_last_player_bid(self, history, d):
        phistory = []
        for bid in history.split(','):
            phistory.append(bid.split(':'))

        history = [[bid[0],
            int(bid[1])%10,
            1-odds(d,int(bid[1])//10)] for bid in phistory if int(bid[1]) != 0]

        highest_bid = {h:{int(x):0 for x in '123456'} for h in self.players}

        data = []
        for h in history:
            highest_bid[h[0]][h[1]] = h[2]
            self.player_bid[h[0]] = highest_bid[h[0]].copy()

    def record_play(self, me, hands, history):
        # split and parse hands for each player
        self.order = [h[0] for h in [hand.split(':') for hand in hands.split(',')]]
        try:
            my_index = self.order.index(me)
            try:
                self.next_player = self.order[my_index+1]
            except:
                self.next_player = self.order[0]
            try:
                self.last_player = self.order[my_index-1]
            except:
                self.last_player = self.order[-1]
        except:
            self.next_player = ''
            self.last_player = ''
        hands = {h[0]:parse_hand(h[1]) \
                        for h in [hand.split(':') \
                           for hand in hands.split(',')]}
        # total dice in play                   
        d = sum([sum(hands[hand].itervalues()) for hand in hands])

        # split the player, the face, and the naive odds of a bid
        phistory = []
        for bid in history.split(','):
            phistory.append(bid.split(':'))

        history = [[bid[0],
            int(bid[1])%10,
            1-odds(d,int(bid[1])//10)] for bid in phistory if int(bid[1]) != 0]

        highest_bid = {h:{int(x):0 for x in '123456'} for h in hands.keys()}

        data = []
        for h in history:
            highest_bid[h[0]][h[1]] = h[2]
            data.append([h[0], highest_bid[h[0]].copy()])

        # self.record.append([hands, history])
        X, y, players = parse_data_to_players([hands, data])

        for player in hands.keys():
            self.X[player].extend(X[player])
            self.y[player].extend(y[player])

    def train_players(self):
        if self.games == self.last_train:
            return None
        for player in self.players:
            if player != self.me:
                if player not in self.models:
                    try:
                        self.models[player] = Model(probability=True)
                    except:
                        self.models[player] = Model()
                self.models[player].fit(self.X[player],self.y[player])
        self.last_train = self.games

def get_play(me,hands,history) :
    
    if not hasattr(get_play, "r"):
        players = [x.split(':')[0] for x in hands.split(',')]
        get_play.r = Record(players, me)

    last_bid = find_last_bid(history)
    if 0 == last_bid :
        get_play.r.record_play(me, hands, history)
        return 0
    num_dice = sum(map(lambda x : len(x.split(':')[1]),hands.split(',')))

    if len(history) > 0:
        get_play.r.record_last_player_bid(history, num_dice)

    my_hand = None
    players_dice = {}
    for i in hands.split(',') :
        who,dice = i.split(':')
        players_dice[who] = len(dice)
        if who == me :
            my_hand = dice

    firstgame = False
    if get_play.r.ld < num_dice:
        get_play.r.games += 1
        firstgame = True
    get_play.r.ld = num_dice

    if get_play.r.games > 500 and get_play.r.games%100 == 0 and firstgame == True:
        get_play.r.train_players()

    elif get_play.r.games > 25 and get_play.r.games%10 == 0 and firstgame == True:
        get_play.r.train_players()

    elif get_play.r.games > 3 and get_play.r.games <= 25 and firstgame == True:
        get_play.r.train_players()

    if not hasattr(get_play.r, 'player_bid'):
        return determine_next_bid_naive(last_bid,
                                        my_hand,
                                        num_dice - len(my_hand),
                                        )
    else:
        return determine_next_bid(
                                  last_bid,
                                  my_hand,
                                  num_dice - len(my_hand),
                                  get_play.r,
                                  players_dice
                                  )


def main():
    print odds(0,1)

if __name__ == '__main__':
    main()