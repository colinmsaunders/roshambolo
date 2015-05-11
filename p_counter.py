# p_counter.py 

# Dumb bot with memory. Keeps a single counter, increments 
# everytime he sees rock, decrements everytime he sees paper.
# Plays scissors if positive, paper if negative, rock if zero.

import random


ROCK = 1
PAPER = 2
SCISSORS = 3

# the count
#
counter = 0


def play(my_id, opponent_id):
    global counter
    if counter < 0:
        return SCISSORS
    if counter > 0:
        return PAPER
    return ROCK


def observe(my_id, a_id, b_id, a_play, b_play, result, a_score, b_score):
    global counter

    if ROCK == a_play:
        counter += 1
    if PAPER == a_play:
        counter -= 1
    if ROCK == b_play:
        counter += 1
    if PAPER == b_play:
        counter -= 1

