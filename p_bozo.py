# p_bozo.py 

# Dumb bot with memory. Remembers what everyone plays 
# and tries to beat their most commonly played shape.

import random


ROCK = 1
PAPER = 2
SCISSORS = 3

# this is a mapping between players and counts of
# their plays
#
memory = {}


def play(my_id, opponent_id):
    global memory
    
    # remember how often she plays each shape
    #
    if not opponent_id in memory:
        counts = {ROCK: 0, PAPER: 0, SCISSORS: 0}
    else:
        counts = memory.get(opponent_id)

    # is ROCK their most? play PAPER
    #
    if (counts[ROCK] > counts[PAPER]) and (counts[ROCK] > counts[SCISSORS]):
        return PAPER

    # PAPER? play SCISSORS
    #
    if (counts[PAPER] > counts[SCISSORS]) and (counts[PAPER] > counts[ROCK]):
        return SCISSORS

    # if they play SCISSORS most, play ROCK
    #
    if (counts[SCISSORS] > counts[PAPER]) and (counts[SCISSORS] > counts[ROCK]):
        return ROCK
    
    # if we get here, just play a random shape
    #
    return random.choice((ROCK, PAPER, SCISSORS))


def observe(my_id, his_id, her_id, his_play, her_play, result, his_score, her_score):
    global memory
    
    # if we've never seen either opponent before, 
    # put them in memory
    #
    if not memory.has_key(his_id):
        memory[his_id] = {ROCK:0, PAPER: 0, SCISSORS: 0}
    if not memory.has_key(her_id):
        memory[her_id] = {ROCK:0, PAPER: 0, SCISSORS: 0}

    # and incremement the counter of what they played
    #
    memory[his_id][his_play] += 1
    memory[her_id][her_play] += 1

