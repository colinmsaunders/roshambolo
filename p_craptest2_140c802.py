# conserv1.py
# Be conservative but be willing to go one past what we have.
# First bump face, then bump num

import pprint
from random import randint

def get_num_dice(hands):
    num = 0
    for player in hands.split(','):
        num += len(player.split(':')[1])
    return num

def get_prev_plays(history):
    prev_plays = []
    if not history:
        return prev_plays

    for prev_play in history.split(','):
        player, play = prev_play.split(':')
        play = int(play)
        num = play / 10
        face = play % 10
        play_dict = dict(player=player, num=num, face=face)
        prev_plays.append(play_dict)
    return prev_plays

def my_hand(me, hands):
    my_dice = {}
    for player_hand in hands.split(','):
        player, hand = player_hand.split(':')
        if player == me:
            for die in hand:
                die = int(die)
                if die in my_dice:
                    my_dice[die] += 1
                else:
                    my_dice[die] = 1

def get_play(me,hands,history) :
    num_dice = get_num_dice(hands)
    prev_plays = get_prev_plays(history)
    my_dice = my_hand(me, hands)
    #print "my_dice", my_dice
    num_other_dice = num_dice - sum(my_dice.values())
    bluff_qty = (num_other_dice - 3)/6 + 1

    if len(prev_plays) == 0:
        last_play=dict(num=1,face=0)
    else:
        last_play = prev_plays[-1]

    # See if we can safely play the lowest possible face with the same num
    last_face = last_play['face']
    for possible_face in range(last_face + 1, 7):
        #print 'examining', possible_face
        if my_dice.get(possible_face, 0) >= last_play['num']:
            return last_play['num']*10 + possible_face

    # See if we can less safely play the lowest possible face with the same num
    for possible_face in range(last_face + 1, 7):
        #print 're-examining', possible_face
        if (my_dice.get(possible_face, 0) + bluff_qty) >= last_play['num']:
            return last_play['num']*10 + possible_face

    # Let's bump the number if we can
    next_num = last_play['num'] + 1
    for possible_face in range(1, 7):
        #print 'examining', possible_face, "with", next_num
        if my_dice.get(possible_face,0) >= next_num:
            return next_num*10 + possible_face

    # See if we can less safely play the lowest possible face with the same num
    for possible_face in range(1, 7):
        #print 're-examining', possible_face, "with", next_num
        if (my_dice.get(possible_face, 0) + bluff_qty) >= next_num:
            return next_num*10 + possible_face


    # Nope. Call liar
    return 0

