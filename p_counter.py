# p_counter.py

# Dumb bot with memory. Keeps a single counter, increments
# everytime he sees rock, decrements everytime he sees paper.
# Plays scissors if positive, paper if negative, rock if zero.

ROCK = 1
PAPER = 2
SCISSORS = 3

# the count
#
counter = 0


def play(game_id, my_id, opponent_id):
    global counter
    if counter < 0:
        play = SCISSORS
    elif counter > 0:
        play = PAPER
    else:
        play = ROCK
    return play


def observe(game_id, a_id, b_id, a_play, b_play, result):
    global counter
    if ROCK == a_play:
        counter += 1
    if PAPER == a_play:
        counter -= 1
    if ROCK == b_play:
        counter += 1
    if PAPER == b_play:
        counter -= 1

