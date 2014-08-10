Roshambono
==========

Roshambono is roshambo (or Rock-Paper-Scissors) with no ties.

Rock beats scissors, scissors beats paper, paper beats rock.

However, if there are is a tie, the player who has played that shape
more often wins. If each player has played that shape the same number 
of times, then the player who has played the shape that beats it more
wins. If still tied, then the player who has played the shape that
it beats most wins. Finally, if still tied, a coin is tossed.

You can write a robot by implementing the get\_play() function in 
p\_robot/player.py:

    def get_play(state) 
    
        state is an 8 bit unsigned integer representing the
        result of the last hand. 

        if it is 0, it is the first game. 

        otherwise, bits 3 and 4 represent your move,
        bits 1 and 2 represent your opponent's move, and 
        the zero'th bit is set if you won, or 0 if you lost.

        return 1 for Rock, 2 for Paper, and 3 for Scissors.

For a quick start to play first to 100 rock against random:

    $ git clone https://github.com/botfights/roshambono.git
    $ cd liarsdice
    $ python main.py play 100 p_rock p_random

Next, edit p\_robot/player.py, implement get\_play(), then play your
robot against the random:

    $ python main.py play 100 p_robot p_random

Have fun!

