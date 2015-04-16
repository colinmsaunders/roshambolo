# robot.py -- sample roshambono robot

# See README.md for full documentation on how to
# write a robot.

# Return 1 for Rock, 2 for Paper, and 3 for Scissors.

# last_hand is an 8 bit unsigned integer representing the
# result of the last hand.

# If it is 0, it is the first game.

# Otherwise, bits 0 and 1 represent your move,
# bits 2 and 3 represent your opponent's move,
# bits 4 and 5 represent the number of tiebreakers
# needed to resolve the game, and
# bit 6 is set if you won, or 0 if you lost.

# For example, if in the last game you played Rock,
# and your opponent played Scissors, state would be:
#
#      (1) | (3 << 2) | (0 << 4) | (1 << 6) = 77


def get_play(last_game):
    return 0
