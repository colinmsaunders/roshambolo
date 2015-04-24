Roshambono
==========

Roshambono is roshambo (or Rock-Paper-Scissors) with no ties.

Rock beats scissors, scissors beats paper, paper beats rock.

However, if there are is a tie, the player who has played that shape
more often wins. If each player has played that shape the same number 
of times, then the player who has played the shape that beats it more
wins. If still tied, then a coin is tossed.

For example, if both players play "Rock", then the player who
has played "Rock" more often wins. If both players have played 
"Rock" the same amount of times, she who played "Paper" more wins.

You can write a robot by implementing the get\_play() function in 
p\_robot.py:

    def get_play(opponent_id, my_play, her_play, i_won) 
        
        return 1 for Rock, 2 for Paper, and 3 for Scissors.
    
        opponent_id is an identifier of your opponent

        my_play and her_play are your plays from last round,
        and i_won is 1 if you won, 0 if you lost

To play first to 100 rock against random:

    $ git clone https://github.com/colinmsaunders/roshambono.git
    $ cd roshambono
    $ python roshambono.py play 100 p_rock p_random

Next, edit p\_robot.py, implement get\_play(), then play your
robot against the random:

    $ python roshambono.py play 100 p_robot p_random

To play a round robin tournament of 100 games each to 1000:
    
    $ python roshambono.py tourney 100 1000 p_robot p_random p_rock 

Have fun!

