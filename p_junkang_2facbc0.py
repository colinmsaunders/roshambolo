# robot.py -- sample liar's dice robot

# See README.md for instructions on how to 
# write a robot, or look at computer.py for
# an example.

from scipy.misc import comb
from numpy import round
from math import pow
SIXTH = 1.0 / 6.0
FIVE_SIXTH = 5.0 / 6.0


def get_prob(q, n):
    """Get probability that there'll be q<= dices given there's n of them. In percent
    """
    p = 0
    for x in range(q, n+1):
        curr = float(comb(n, x, exact=True)) * pow(SIXTH, x) * pow(FIVE_SIXTH, (n-x))
        p += curr
    return p * 100

def _parse_hands(hands):
    ret_dict = {}
    keyval_str_list = hands.split(',')
    for keyval in keyval_str_list:
        key, val = keyval.split(':') 
        ret_dict[key] = val
    return ret_dict

def _parse_hand(hand):
    # Assumes max hand of 5
    hand_list = list(hand)
    hand_dict = {}
    for c in hand_list:
        hand_dict[c] = hand_dict.get(c, 0) + 1
    return hand_dict

def _latest_play(history):
    """Return tuple (quantity, face val)
    """
    if not history:
        return (0, 1)

    last_play = history.split(',')[-1]
    val = last_play.split(':')[1]
    face_val = val[-1]
    if int(face_val) == 0:
        # Calls liars
        # XXX: In reality, liars isn't a latest play bc the game stops
        return (1, 0)
    try:
        quant_last_len = len(val) - 1
        quant = int(val[:quant_last_len])
    except Exception, ex:
        raise
    return (quant, face_val)

def tot_other_player_dices(me, hands_dict):
    """Returns tuple (tot_dice_w_me, tot_dice_wo_me)
    """
    sum = 0
    for player, hands in hands_dict.items():
        if player == me:
            me_sum = len(hands) 
        else:
            sum += len(hands)
    return (sum + me_sum, sum)

   
def score_fn(m, o):
    return pow(m,2) * pow(100 - o, 2)

SAFE_THRESHOLD = 55
def find_next_play_thats_safe(hand, tot_w_me, tot_wo_me, curr_quant, curr_face_val):
    # Priority
    # 1. Make next bet I know I can make with threshold certainty
    # 2. Make next bet I know I can make with threshold certainty, (min prob) that would make others feel uncomfortable
    #
    # Bet can be same quant, next higher face val, or higher quant same face val.
    # Priority:
    # 1. High quant, same face val
    # 2. Same quant, next same face val

    # 1. higher quant, my highest face val. Must find higher quant
    new_quant = curr_quant
    new_face_val = curr_face_val
    quant_face_val_in_my_hand = hand.get(curr_face_val, 0)
    prob_next_quant_in_pool_knowing_what_i_know = 0
    prob_next_quant_in_pool_for_other = 0
    first_run = True
    # Can be no diff in num
    for delta in range(0, tot_wo_me + 1):
        tmp_quant = delta + curr_quant
        tmp_prob_next_quant_in_pool_knowing_what_i_know = get_prob(max((tmp_quant - quant_face_val_in_my_hand), 0), tot_wo_me) # Chances of me reaching this quant
        tmp_prob_next_quant_in_pool_for_other = get_prob(tmp_quant, tot_w_me)
        # 1. Know I can make this play! Or else why...
        if tmp_prob_next_quant_in_pool_knowing_what_i_know >= SAFE_THRESHOLD or first_run:
            # I can make it!
            new_quant = tmp_quant
            prob_next_quant_in_pool_knowing_what_i_know = tmp_prob_next_quant_in_pool_knowing_what_i_know
            prob_next_quant_in_pool_for_other = tmp_prob_next_quant_in_pool_for_other
            first_run = False
            #print "Chose new delta %s, my prob is %s other is %s" % (delta, prob_next_quant_in_pool_knowing_what_i_know, prob_next_quant_in_pool_for_other)
        else:
            # Early exit bc everything else is too risky
            #print "Stop chosing new delta %s, prob is %s " % (delta, tmp_prob_next_quant_in_pool_knowing_what_i_know)
            break
    #print "Q:%s K:%s me:%s other:%s" % (new_quant, curr_face_val, prob_next_quant_in_pool_knowing_what_i_know, prob_next_quant_in_pool_for_other)
    return new_quant, prob_next_quant_in_pool_knowing_what_i_know, prob_next_quant_in_pool_for_other

def meta_find_next_play_thats_safe(my_hand, tot_w_me, tot_wo_me, curr_quant, user_face_val):
    # Perm through all hands
    max_my_prob = 0
    max_score = 0
    opt_quant = 0
    opt_keyval = 0
    for curr_face_val in ['1', '2', '3', '4', '5', '6']:
        new_quant, my_prob, other_prob = find_next_play_thats_safe(my_hand, tot_w_me, tot_wo_me, curr_quant + (0 if int(user_face_val) < int(curr_face_val) else 1), curr_face_val)
        # Maximize discomfort while staying safe
        score = score_fn(my_prob, other_prob)
        #print "Eval q:%s f:%s my_prob:%s, other_prob:%s, score:%s" % (new_quant, curr_face_val, my_prob, other_prob, score)
        if score > max_score:
            max_score = score
            opt_quant = new_quant
            opt_keyval = curr_face_val
            max_my_prob = my_prob
    #print "Picking Q:%s K:%s Score:%s" % (opt_quant, opt_keyval, max_score)
    return (opt_quant, opt_keyval, max_my_prob, max_score)


def get_play(me, hands, history):
    try:
        hands_dict = _parse_hands(hands)

        my_hands = hands_dict[me]
        my_hand = _parse_hand(my_hands)
        tot_w_me, tot_wo_me = tot_other_player_dices(me, hands_dict)
        
        (quant, face_val) =  _latest_play(history)
        quant_face_val_in_my_hand = my_hand.get(face_val, 0)
        latest_play_prob = get_prob(quant, tot_w_me)
        latest_play_prob_knowing_what_i_know = get_prob(max(0, quant - quant_face_val_in_my_hand), tot_wo_me)
        prob_bs_is_correct = 100 - latest_play_prob_knowing_what_i_know

        # DECISION
        # 1. Make next safe play and hope someone else messes up
        # 2. Call BS now, bc calling BS risks are lower than taking the next val
        # 3. If early in the game, raise the stakes!! Make call aftea threshold
        (opt_quant, opt_keyval, my_prob, max_score) = meta_find_next_play_thats_safe(my_hand, tot_w_me, tot_wo_me, quant, face_val)

        # Take a chance If i'm better off than calling BS
        score_of_bs = pow(prob_bs_is_correct, 4)
        if max_score > score_of_bs:
            #print "Picking mine %s,%s vs bs %s,%s" % (max_score, my_prob, score_of_bs, prob_bs_is_correct)
            return int("%s%s" % (opt_quant, opt_keyval))
        else:
            #print "Callig BS mine %s,%s vs bs %s,%s" % (max_score, my_prob, score_of_bs, prob_bs_is_correct)
            return 0
    except Exception, ex:
        import traceback
        #print traceback.format_exc()
        return 0


    #new_quant, prob_next_quant_in_pool_knowing_what_i_know, prob_next_quant_in_pool_for_other = find_next_play_thats_safe(my_hand, tot_w_me, tot_wo_me, quant, face_val)
    ##print score_fn(prob_next_quant_in_pool_knowing_what_i_know, prob_next_quant_in_pool_for_other )

    # Results Logic
    #print 'Results'
    #print latest_play_prob
    #print prob_bs_is_correct
    

#print "final result %s" %  get_play('A', 'A:23135,B:xxxx,C:xx', 'A:22,B:23,A:33')
