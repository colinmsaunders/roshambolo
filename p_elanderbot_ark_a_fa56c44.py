# Pelanderbot.py -- exemplary liar's dice robot

import math
import sys
from random import randint
import operator

## debuging setup
#
debug_on, shout_on = False, False

def debug_print(x):
    if debug_on:
        print x

def shout(x):
    if shout_on:
        print x
        
# utility probability functions
#
def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)
    
# class to hold info about other players
#
class Player:
    def __init__(self, name, dice):
        self.name = name
        self.dice = list(dice)
        self.bid_face = 0
        if dice is None:
            self.hand_size = 0
        else:
            self.hand_size = len(dice)

def get_play(me,hands,history):

    ## initialize the persistent variables, if necessary
    #
    if not hasattr(get_play, "player_dict"):
        get_play.player_dict = {}
    
    if not hasattr(get_play, "game_count"):
        get_play.game_count = 0  # it doesn't exist yet, so initialize it
    get_play.game_count += 1
    
    if not hasattr(get_play, "bid_losses"):
        get_play.bid_losses = 0  # it doesn't exist yet, so initialize it
    
    if not hasattr(get_play, "call_losses"):
        get_play.call_losses = 0  # it doesn't exist yet, so initialize it
    
        
    if not hasattr(get_play, "ld_bid_losses"):
        get_play.ld_bid_losses = 0  # it doesn't exist yet, so initialize it
    
    if not hasattr(get_play, "ld_call_losses"):
        get_play.ld_call_losses = 0  # it doesn't exist yet, so initialize it
    
    
    if not hasattr(get_play, "bid_modifier"):
        get_play.bid_modifier = .10  # it doesn't exist yet, so initialize it
        
    if not hasattr(get_play, "just_called"):
        get_play.just_called = False  # it doesn't exist yet, so initialize it    
    if not hasattr(get_play, "last_hand_size"):
        get_play.last_hand_size = 0  # it doesn't exist yet, so initialize it    
    
    mod_high = .01
    mod_low = -.12
    
    # figure out the previous call
    #
    if 0 == len(history):
		prev_player,prev_quantity,prev_face = 0,0,0
		return 10 + randint(1,3)
    else:
        prev_player = history.split(',')[-1].split(':')[0]
        x = int(history.split(',')[-1].split(':')[1])
        prev_call,prev_quantity,prev_face = str(x),x // 10,x % 10

    # count the total number of dice
    #
    num_dice = sum(map(lambda x : len(x.split(':')[1]),hands.split(',')))
 
    # find my hand and build the other players out
    #
    num_players = 0
    my_hand = None
    for i in hands.split(','):
        who,dice = i.split(':')
        if dice:
            num_players += 1
        if who == me:
            my_hand = dice
        else:
            if who in get_play.player_dict:
                if get_play.player_dict[who].dice == list('o'):
                    get_play.player_dict[who].dice = list(dice)
            else:
                get_play.player_dict[who] = Player(who, dice)
                
    # modify bid
    #
    if num_players == 2:
        get_play.bid_modifier = mod_low
    else:
        get_play.bid_modifier = mod_high
                
    if my_hand is None:
        if get_play.just_called:
            get_play.call_losses += 1
        else:
            get_play.bid_losses += 1
    
        get_play.last_hand_size = 0
        return 0
        
    if len(my_hand) < get_play.last_hand_size:            
        if get_play.just_called:
            get_play.call_losses += 1
        else:
            get_play.bid_losses += 1
    
    get_play.last_hand_size = len(my_hand)
    
    
    ## showdown: reset
    #
    if 0 == prev_quantity:
        if prev_player == me:
            get_play.just_called = True
        for who in get_play.player_dict:
            get_play.player_dict[who].dice = list('o')
        return 0
    
    next_player_name = ''

    ## populate suspected hands
    #
    if 1 < len(history) and prev_player != me:
        for hist in reversed(history.split(',')):
            the_player = hist.split(':')[0]
            if the_player == me:
                break
            next_player_name = the_player
            the_face = list(hist.split(':')[1])[-1]
            counter = 0
            for die in get_play.player_dict[the_player].dice:
                if die == 'x':
                    get_play.player_dict[the_player].dice[counter] = the_face
                    break
                counter += 1
                
    # find known quantities
    #
    global known_dice_map
    known_dice_map = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, 'u': num_dice}
    for face in my_hand:
        known_dice_map[face] += 1
        known_dice_map['u'] -= 1
	
    ## showdown: reset
    #
    if 0 == prev_quantity:
        for who in get_play.player_dict:
            get_play.player_dict[who].dice = list('o')
        return 0
    
	
    # find suspected quantities
    #
    global sus_dice_map
    sus_dice_map = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, 'u': num_dice}
    for who in get_play.player_dict:
        if get_play.player_dict[who].dice != list('o'):
            for face in get_play.player_dict[who].dice:
                if face != 'x':
                    sus_dice_map[str(face)] += 1
                    sus_dice_map['u'] -= 1
    for face in my_hand:
        sus_dice_map[face] += 1
        sus_dice_map['u'] -= 1 
     
	# find the known probability of a given bid
	#
    debug_print("I have %d ones, %d twos, %d threes, %d fours, %d fives, %d sixes, %d unknown" % (known_dice_map['1'],known_dice_map['2'],known_dice_map['3'],known_dice_map['4'],known_dice_map['5'],known_dice_map['6'],known_dice_map['u']))
    def prob_call(bid):
        num, face = int(bid[:-1]), bid[-1]
        debug_print("Num is %d, face is %s" % (num, face))
        if num == 0:
            debug_print("Probability is %d. No actual call" % (1))
            return 1.0
		# establish boundaries
        if num <= known_dice_map[face]:
            debug_print("Probability is %d. I have at least as many dice of this face as this bid" % (1))
            return 1.0
        elif num > known_dice_map['u'] + known_dice_map[face]:
            debug_print("Probability is %d. Not enough dice on the board." % (0))
            return 0.0
		# calculate probability
        num_needed, num_unknown = num - known_dice_map[face], known_dice_map['u']
        probability = 0.0
        for i in xrange(num_needed, num_unknown + 1):
            probability += (nCr(num_unknown, i) * ((float(1)/6)**i) * ((float(5)/6)**(num_unknown - i)))
        debug_print("Probability is %f" % (probability))
        return probability	
	
      
	# find the suspected probability of a given bid
	#
    def sus_prob_call(bid):
        num, face = int(bid[:-1]), bid[-1]
        debug_print("Num is %d, face is %s" % (num, face))
        if num == 0:
            debug_print("Probability is %d. No actual call" % (1))
            return 1.0
		# establish boundaries
        if num <= sus_dice_map[face]:
            debug_print("Probability is %d. I have at least as many dice of this face as this bid" % (1))
            return 1.0
        elif num > sus_dice_map['u'] + sus_dice_map[face]:
            debug_print("Probability is %d. Not enough dice on the board." % (0))
            return 0.0
		# calculate probability
        num_needed, num_unknown = num - sus_dice_map[face], sus_dice_map['u']
        probability = 0.0
        for i in xrange(num_needed, num_unknown + 1):
            probability += (nCr(num_unknown, i) * ((float(1)/6)**i) * ((float(5)/6)**(num_unknown - i)))
        debug_print("Probability is %f" % (probability))
        return probability	
	
    

	## increment the bid
	#
    def inc_bid(bid):
		num, face = int(bid[:-1]), int(bid[-1])
		if face == 6:
			return str(num + 1) + '1'
		return str(num) + str(face + 1)
    
    def inc_bid_amount(bid, amount):
        bidReturn = bid
        for i in xrange (1, amount + 1):
            bidReturn = inc_bid(bidReturn)
        return bidReturn
    
    ## create dictionary of next possible bids
    #
    global bid_dict
    bid_dict = {}
    for i in xrange (1, 7):
        bid_dict[i] = inc_bid_amount(prev_call, i)
        debug_print("Bid %d is %s" % (i, bid_dict[i]))
    
    ## build a dictionary of bids to their probability
    #
    bid_prob_dict = {x: prob_call(bid_dict[x]) for x in bid_dict}
    
    ## find known bid with highest probability
    #
    test_bid = bid_dict[max(bid_prob_dict.iteritems(), key=operator.itemgetter(1))[0]]
        
    ## build a dictionary of suspected bids to their probability
    #
    sus_bid_prob_dict = {x: sus_prob_call(bid_dict[x]) for x in bid_dict}
    
    ## find suspected bid with highest probability
    #
    sus_test_bid = bid_dict[max(sus_bid_prob_dict.iteritems(), key=operator.itemgetter(1))[0]]
    
	## decision time
	#
    
    prev_prob,sus_prev_prob,test_prob,sus_test_prob = prob_call(prev_call),sus_prob_call(prev_call),prob_call(test_bid),sus_prob_call(sus_test_bid)
    ### easy decisions
    if prev_prob == 0:
		debug_print("No chance")
		return 0
    elif prev_prob == 1:
        debug_print("Obviously...")
        return int(test_bid)
    ### big decision
    if num_players != 2:
        if ((known_dice_map['u'] - len(get_play.player_dict[next_player_name].dice) + len(my_hand)) / 6) > prev_quantity:
            return int(inc_bid(prev_call))
    if sus_test_bid == test_bid:
        if test_prob >= (1 - sus_prev_prob - get_play.bid_modifier):
            return int(test_bid)
        return 0
    elif float(test_bid) > float(sus_test_bid) - .25:
        if test_prob >= (1 - sus_prev_prob - get_play.bid_modifier):
            debug_print("Best guess")
            return int(test_bid)
        return 0
    else:
        if  sus_test_prob >= (1 - sus_prev_prob - get_play.bid_modifier):
            return int(sus_test_bid)
        return 0

if __name__ == '__main__':
    get_play(sys.argv[1], sys.argv[2], sys.argv[3])
