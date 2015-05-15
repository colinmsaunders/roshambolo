# p_human.py -- human roshambolo robot

import random

ROCK = 1
PAPER = 2
SCISSORS = 3

VERBOSE_PLAYS = {
    1:  'ROCK',
    2:  'PAPER',
    3:  'SCISSORS'
}

score = [0, 0]
last_game_id = None

def play(game_id, my_id, opponent_id):

    # tell the user what's going on
    #
    print("You are player #%s, your opponent is player %s." % 
          (my_id, opponent_id))

    # get the user's move
    #
    play = None
    try:
        print("What is your play? (1 for Rock, 2 for Paper, 3 for Scissors)")
        s = raw_input()
        play = int(s)
    except KeyboardInterrupt:
        raise
    except:
        pass

    # invalid input? just pick a random shape
    #
    if None == play:
        print("Invalid input. Picking a random shape.")
        play = random.choice((ROCK, PAPER, SCISSORS))

    # echo it back to the user
    #
    print('You played %s.' % VERBOSE_PLAYS[play])
    
    # and return it to the referree
    #
    return play


def observe(game_id, a_id, b_id, a_play, b_play, result):
    global score, last_game_id
    if game_id != last_game_id:
        score = [0, 0]
        last_game_id = game_id
    score[result] += 1
    print("Player #%s played %s, player #%s played %s, player #%s won the point." % (
              a_id, VERBOSE_PLAYS[a_play],
              b_id, VERBOSE_PLAYS[b_play],
              [a_id, b_id][result]))
    print("The score is %d to %d." % (score[0], score[1]))

