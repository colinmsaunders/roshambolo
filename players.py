# players.py -- some sample players

import random
import logging


def p_caller(me, hands, history):
    ''' always call '''
    return 0


def p_random_raiser(me, hands, history):
    ''' raise to some random, possible, hand. call if impossible '''
    if 0 == len(history):
        prev = 0, 0
    else:
        x = int(history.split(',')[-1].split(':')[1])
        prev = x / 10, x % 10
 
    num_dice = sum(map(lambda x: len(x.split(':')[1]), hands.split(',')))

    # impossible?
    #
    if prev[0] > num_dice:
        return 0

    # top call?
    #
    if prev[0] == num_dice and prev[1] == 6:
        return 0

    # loop till we find a bigger play
    #
    while 1:
        qty = random.randint(prev[0], num_dice)
        face = random.choice((1, 2, 3, 4, 5, 6))
        if (qty > prev[0]) or (qty == prev[0] and face > prev[1]):
            return (qty * 10) + face


def p_bumper(me, hands, history):
    ''' just bump previous call '''
    if 0 == len(history):
        return 11   # "one one"
    last_play = history.split(',')[-1]
    last_player, last_call = last_play.split(':')
    last_call = int(last_call)
    # ignore showdown
    if 0 == last_call:
        return 0
    last_face = last_call % 10
    last_quantity = last_call // 10
    if 6 == last_face:
        return ((last_quantity + 1) * 10) + 1
    return (last_quantity * 10) + (last_face + 1)


def p_simpleton(me, hands, history):
    ''' play lowest call i can amongst faces i have '''
    hands = hands.split(',')
    my_hand = {}
    my_max_face = 0
    for i in hands:
        player, dice = i.split(':')
        if me == player:
            for j in dice:
                j = int(j)
                if j > my_max_face:
                    my_max_face = j
                my_hand[j] = my_hand.get(j, 0) + 1
            break

    if 0 == len(history):
        last_call = 0
        last_face = 0
        last_quantity = 0
    else:
        last_play = history.split(',')[-1]
        last_player, last_call = last_play.split(':')
        last_call = int(last_call)
        if 0 == last_call:
            return 0
        last_face = last_call % 10
        last_quantity = last_call // 10

    if 0 == len(history):
        quantity = 1
    else:
        quantity = last_quantity
    while 1:
        for face in range(1, my_max_face + 1):
            if 0 == my_hand.get(face, 0):
                continue
            if quantity > last_quantity or face > last_face:
                return (quantity * 10) + face
        quantity += 1


def p_conservative(me, hands, history):
    ''' only play things i have, otherwise call '''
    hands = hands.split(',')
    my_hand = {}
    my_max_face = 0
    my_dice = 0

    for i in hands:
        player, dice = i.split(':')
        if me == player:
            for j in dice:
                my_dice += 1
                j = int(j)
                if j > my_max_face:
                    my_max_face = j

                my_hand[j] = my_hand.get(j, 0) + 1
            break

    if 0 == len(history):
        last_call = 0
        last_face = 0
        last_quantity = 0
    else:
        last_play = history.split(',')[-1]
        last_player, last_call = last_play.split(':')
        last_call = int(last_call)

        if 0 == last_call:
            return 0
        last_face = last_call % 10
        last_quantity = last_call // 10

    if 0 == len(history):
        quantity = 1
    else:
        quantity = last_quantity

    while 1:
        for face in range(1, my_max_face + 1):

            if quantity > my_hand.get(face, 0):
                continue

            if quantity > last_quantity or face > last_face:
                return (quantity * 10) + face

        quantity += 1

        if quantity > my_dice:
            return 0

