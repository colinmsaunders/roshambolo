Roshambozo
==========

Roshambozo is roshambo (or Rock-Paper-Scissors) with no ties.

Rock beats scissors, scissors beats paper, paper beats rock.

However, if there are is a tie, the player who has played that shape
more often wins. If each player has played that shape the same number 
of times, then the player who has played the shape that beats it more
wins. If still tied, then a coin is tossed.

For example, if both players play "Rock", then the player who
has played "Rock" more often wins. If both players have played 
"Rock" the same amount of times, she who played "Paper" more wins.

You can write a robot by implementing the `play()` function in 
`p_robot.py`:

    def play(my_id, opponent_id):
        pass

`my_id` is a unique identifier for your player, 
`opponent_id` identifies your opponent. Return 1 for ROCK, 
2 for PAPER, or 3 for SCISSORS.

You will also be called to observe all results, even for games you
aren't playing in:

    def observe(my_id, his_id, her_id, his_play, her_play, 
                result, his_score, her_score)
        pass

`result` is 0 if "he" won the last game, 1 if "she" won.

To play first to 100 rock against random:

    $ git clone https://github.com/colinmsaunders/roshambozo.git
    $ cd roshambozo
    $ python roshambozo.py play 100 p_rock p_random

Next, edit `p_robot.py`, implement `play()` and optionally `observe()`, 
then play your robot against random:

    $ python roshambozo.py play 100 p_robot p_random

To play a round robin tournament of 100 games each to 1000:
    
    $ python roshambozo.py tourney 100 1000 p_robot p_random p_rock 

To time your robot (to make sure it's not too slow, compared to p\_rock):

    $ python roshambozo.py time p_robot

Have fun!

