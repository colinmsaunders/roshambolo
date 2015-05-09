# p_human.py -- human roshambozo robot

import random

ROCK = 1
PAPER = 2
SCISSORS = 3

VERBOSE_PLAYS = {
    1:  'ROCK',
    2:  'PAPER',
    3:  'SCISSORS'
}

def play(my_id, opponent_id):

    # first, get some information about the current state of the game
    #
    pass

    # tell the user what's going on
    #
    print("Your opponent is: %s" % opponent_id)
    if 0 != my_play:
        print("You played %s, your opponent played %s, you %s." % 
                (VERBOSE_PLAYS[my_play], VERBOSE_PLAYS[her_play], 
                 ['lost', 'won'][i_won]))

    # get the user's move
    #
    play = None
    try:
        print("What is your play? (1 for Rock, 2 for Paper, 3 for Scissors)")
        s = raw_input()
        play = int(play)
    except KeyboardInterrupt:
        raise
    except:
        pass

    # invalid input? just pick a random shape
    #
    if None == play:
        play = random.choice((ROCK, PAPER, SCISSORS))

    # echo it back to the user
    #
    print('You played %s.' % VERBOSE_PLAYS[play])
    
    # and return it to the referree
    #
    return play

