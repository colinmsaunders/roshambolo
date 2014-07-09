# saunders.py -- my player 

import random,itertools,math,sys

RULES_DICE = 5
RULES_FACES = 6

def choose(n,k) :
    return reduce(lambda x,y : (x * y[0]) // y[1],itertools.izip(xrange(n - k + 1,n + 1),xrange(1,k + 1)),1)

def exactly_k_out_of_n(k,n,faces) :
    return choose(n,k) * math.pow(1.0 / faces,k) * math.pow((faces - 1.0) / faces,n - k)

AT_LEAST_K_OUT_OF_N = {}
def at_least_k_out_of_n(k,n,faces) :
    global AT_LEAST_K_OUT_OF_N
    key = (k,n,faces)
    if AT_LEAST_K_OUT_OF_N.has_key(key) :
        return AT_LEAST_K_OUT_OF_N[key]
    t = 0.0
    for i in range(k,n + 1) :
        t += exactly_k_out_of_n(i,n,faces)
    AT_LEAST_K_OUT_OF_N[key] = t
    return t

def prob_call(k,n) :
    x = at_least_k_out_of_n(k,n,RULES_FACES)
    return x

def get_play(me,hands_str,history_str) :
    
    # first, set up some variables
    #
    hands = hands_str.split(',')
    total_dice = 0
    dice_counts = {}
    my_hand = {}
    for i in hands :
        player,dice = i.split(':')
        dice_counts[player] = len(dice)
        total_dice += len(dice)
        if me == player :
            for j in dice :
                j = int(j)
                my_hand[j] = my_hand.get(j,0) + 1

    # parse the history
    #
    history = []
    if 0 != len(history_str) :
        for i in history_str.split(',') :
            player,call = i.split(':')
            history.append((player,int(call)))

    # showdown? ignore ...
    #
    if 0 != len(history) and 0 == history[-1][1] :
        return 0
    
    # figure out the last play
    #
    last_play = None
    last_player = None
    last_quantity = None
    last_face = None
    if 0 != len(history) :
        last_play = history[-1]
        last_player = last_play[0]
        last_quantity = last_play[1] // 10
        last_face = last_play[1] % 10

    # impossible play (bigger call than dice left)? if so, call bullshit
    #
    if None != last_play :
        if last_quantity > (my_hand.get(last_face,0) + (total_dice - dice_counts[me])) :
            return 0

    # find all legal plays in my hand
    #
    candidates = []
    for face,quantity in my_hand.items() :
        start = 1
        if None != last_quantity :
            start = last_quantity
        for i in range(start,quantity + 1) :
            if (None == last_play) or (i > last_quantity) or ((i == last_quantity) and (face > last_face)) :
                candidates.append((i,face))

    # any legal plays in my hand? if so, play a random one
    #
    if 0 != len(candidates) :
        x = random.choice(candidates)
        return (x[0] * 10) + x[1]

    # calculate the probability of the last call
    #
    p_call = 1.0
    if last_quantity > my_hand.get(last_face,0) :
        p_call = prob_call(last_quantity - my_hand.get(last_face,0),total_dice - dice_counts[me])
    
    # ok, time to bluff. find the most likely next highest hands.
    #
    candidates = [None,[]]
    for quantity in range(1,total_dice + 1) :
        for face in range(1,RULES_FACES + 1) :
            if (None == last_play) or (quantity > last_quantity) or ((quantity == last_quantity) and (face > last_face)) :
                
                # possible given my hand?
                #
                if (quantity - my_hand.get(face,0)) > (total_dice - dice_counts[me]) :
                    continue

                # what is the probability of this call being in the other dice
                #
                y = prob_call(quantity - my_hand.get(face,0),total_dice - dice_counts[me])

                # and the probability of the total call being in all dice
                #
                y2 = prob_call(quantity,total_dice)
                
                # remember the most likely onees
                #
                if (None == candidates[0]) or (candidates[0] < (y,y2)) :
                    candidates = [(y,y2),[(quantity,face),]]
                elif candidates[0] == (y,y2) :
                    candidates[1].append((quantity,face))
                else :
                    pass

    # no possible raise? call
    #
    if None == candidates[0] :
        return 0

    # ok, now we have the probability of the previous player's call,
    # and the probability of our raise that is most likely on the table.
    # 
    # we will call bullshit if the following three conditions are met:
    #
    #   A. a random float between 0 and 1 is greater than the probability of their call
    #   B. a random float between 0 and 1 is greater than the probability of our call
    #   C. we roll a 1 on a k-sided die, where k is the number of remaining players
    #
    # the intuition here is the more likely the previous call, the less
    # often we should call bullshit. similarly, the more likely our call
    # the less often we should call bullshit. lastly, the more players
    # that are left, the less often we should call bullshit.
    #
    if (random.random() > p_call) and (random.random() > candidates[0][0]) and (1 == random.randint(1,len(dice_counts))) :
        return 0

    # lastly, pick a random candidate
    #
    x = random.choice(candidates[1])
    return (x[0] * 10) + x[1]

