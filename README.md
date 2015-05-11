Roshambozo
==========

Roshambozo is roshambo (or Rock-Paper-Scissors) with no ties.

Rock beats scissors, scissors beats paper, paper beats rock.

However, if there are is a tie, the player who has played that shape
more often in the game, wins. If each player has played that shape the
same number of times, then the player who has played the shape that
beats it more wins. If still tied, then a coin is tossed.

For example, if both players play "Rock", then the player who
has played "Rock" more often wins. If both players have played
"Rock" the same amount of times, she who played "Paper" more wins.

You write a robot by implementing the `play()` function in
`p_robot.py`:

    def play(my_id, opponent_id):
        pass

`my_id` is a unique identifier for your player,
`opponent_id` identifies your opponent. Return 1 for rock,
2 for paper, or 3 for scissors.

You will also be called to observe all results, even for games you
aren't playing in:

    def observe(my_id, a_id, b_id, a_play, b_play,
                result, a_score, b_score)
        pass

`result` is 0 if "a" won the last game, 1 if "b" won.

To get a copy of the game:

    $ git clone https://github.com/colinmsaunders/roshambozo.git
    $ cd roshambozo

To play a race to 3, human against computer:

    $ python roshambozo.py humam 3 p_random

To play first to 100 rock against random:

    $ python roshambozo.py game 100 p_rock p_random

Next, copy `p_random.py` to `p_mybot.py`, implement `play()` and
optionally `observe()`, then play your bot against random:

    $ python roshambozo.py game 100 p_mybot p_random

To play a round robin tournament of 100 games each to 1000:

    $ python roshambozo.py tourney 100 1000 p_mybot p_random p_rock

The winner of the tournament is the player who wins the most games,
in total. Note that `player_id` is consistent across games, but shape
counts are reset between each game.

To time your robot (to make sure it's not too slow, compared to `p_rock`):

    $ python roshambozo.py time p_mybot

Have fun!

