#!/usr/bin/python

# roshambozo.py -- console harness

HELP = '''\
usage:

    To play a race to 10 between p_rock and p_random:

        $ python roshambozo.py game 10 p_rock p_random

    To play a round robin tourney of best of 100 races to 10000
    between p_rock and p_robot and p_random:

        $ python roshambozo.py tourney 100 10000 p_rock p_robot p_random

    To time your bot to make sure it's not too slow:

        $ python roshambozo.py time p_robot
'''

import sys
import imp
import logging
import random
import time

# ignore SIG_PIPE
from signal import (signal, SIGPIPE, SIG_DFL)

signal(SIGPIPE, SIG_DFL)

ROCK = 1
PAPER = 2
SCISSORS = 3

BEATS = [None, SCISSORS, ROCK, PAPER]
BEAT_BY = [None, PAPER, SCISSORS, ROCK]

VERBOSE_PLAYS = {
    ROCK: 'ROCK',
    PAPER: 'PAPER',
    SCISSORS: 'SCISSORS'
}


def get_play(player, opponent, catch_exceptions):
    play = 0
    try:
        play = int(player[1](player[0], opponent[0]))
    except KeyboardInterrupt:
        raise
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" calling %s \'s play() function'
                     % (sys.exc_info()[1], player[2]))
    if play < 1 or play > 3:
        play = random.randint(1, 3)
    logging.debug('PLAY\t%d\t%d\t%d\t%s plays %s' % (player[0], opponent[0], play, player[3], VERBOSE_PLAYS[play]))
    return play


def observe_play(player, his_id, her_id, his_play, her_play, result, his_score, her_score, catch_exceptions) :
    try:
        player[2](player[0], his_id, her_id, his_play, her_play, result, his_score, her_score)
    except KeyboardInterrupt:
        raise
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" calling %s \'s observe() function'
                     % (sys.exc_info()[1], player[3]))
    return


def play_game(race_to, player1, player2, observers, catch_exceptions):
    wins = [0, 0]
    plays = [[-1, 0, 0, 0], [-1, 0, 0, 0]]
    while 1:
        a_play = get_play(player1, player2, catch_exceptions)
        b_play = get_play(player2, player1, catch_exceptions)
        ties = 0
        if a_play == b_play:
            ties += 1
            x = plays[0][a_play] - plays[1][b_play]
            if 0 == x:
                ties += 1
                x = plays[0][BEAT_BY[a_play]] - plays[1][BEAT_BY[b_play]]
                if 0 == x:
                    ties += 1
                    a_won = random.randint(0, 1)
                elif 0 > x:
                    a_won = 0
                else:
                    a_won = 1
            elif 0 > x:
                a_won = 0
            else:
                a_won = 1
        else:
            a_won = 1
            if BEATS[b_play] == a_play:
                a_won = 0
        plays[0][a_play] += 1
        plays[1][b_play] += 1
        if a_won:
            wins[0] += 1
        else:
            wins[1] += 1
        logging.debug('GAME\t%d\t%d\t%d\t%d\t%d\t%s\t%s'
                      % (wins[0], wins[1], 
                          a_play, b_play, a_won, 
                          [player1[3], player2[3]][1 - a_won], 
                          [player1[3], player2[3]][a_won]))
        for i in observers:
            if None == i[2]:
                continue
            observe_play(i, player1[0], player2[0], a_play, b_play, 
                         a_won, wins[0], wins[1], catch_exceptions)
        if wins[0] == race_to:
            return 0
        if wins[1] == race_to:
            return 1


def make_player(player_id, playername, catch_exceptions):
    fp = pathname = description = m = None
    try:
        fp, pathname, description = imp.find_module(playername)
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" finding module %s' 
                     % (sys.exc_info()[1], playername))
    try:
        if fp:
            m = imp.load_module(playername, fp, pathname, description)
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" importing %s' 
                     % (sys.exc_info()[1], playername))
    finally:
        if fp:
            fp.close()
    if None == m:
        return None
    f_play = None
    if hasattr(m, 'play'):
        f_play = getattr(m, 'play')
    f_observe = None
    if hasattr(m, 'observe'):
        f_observe = getattr(m, 'observe')
    return (player_id, f_play, f_observe, playername)


def play_tourney(t, n, players):
    scores = {}
    for i in players:
        scores[i[0]] = [i, 0]
    for r in range(t):
        for i in range(len(players)):
            for j in range(len(players)):
                if i >= j:
                    continue
                x = play_game(n, players[i], players[j], players, True)
                if 0 == x:
                    scores[players[i][0]][1] += 1
                else:
                    scores[players[j][0]][1] += 1
                logging.info('TOURNEY\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s' % (
                             r, t, i, j, scores[players[i][0]][1], scores[players[j][0]][1], 
                             players[i][3], players[j][3]))
        k = scores.keys()
        k.sort(key = lambda x : scores[x][1],reverse = True)
        for i in k:
            logging.info('SCORE\t%d\t%d\t%s' % (r, scores[i][1], scores[i][0][3]))


if __name__ == '__MAIN__':
    if 1 == len(sys.argv):
        print(HELP)
        sys.exit()

    c = sys.argv[1]

    if 0:
        pass

    elif 'help' == c:
        print(HELP)
        sys.exit()

    elif 'game' == c:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s', stream=sys.stdout)
        n = int(sys.argv[2])
        playernames = sys.argv[3:5]
        random.shuffle(playernames)
        player1 = make_player(1, playernames[0], False)
        player2 = make_player(2, playernames[1], False)
        x = play_game(n, player1, player2, (player1, player2), False)
        return x

    elif 'tourney' == c:
        logging.basicConfig(level=logging.INFO, 
                format='%(message)s', stream=sys.stdout)
        t = int(sys.argv[2])
        n = int(sys.argv[3])
        playernames = sys.argv[4:]
        random.shuffle(playernames)
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(player_id, playername, True))
        play_tourney(t, n, players)
        return

    elif 'time' == c:
        p_random = make_player(1, 'p_random', False)
        p_rock = make_player(2, 'p_rock', False)
        p_player = make_player(3, sys.argv[2], False)
        start = time.time()
        print('playing 100 games to 1000 between random and rock ...')
        for i in range(100):
            play_game(1000, p_rock, p_random, (p_rock, p_random), False)
        rock_time = time.time() - start
        print('p_rock elapsed: %f seconds' % rock_time)
        print('playing 100 games to 1000 between random and %s ...' % p_player[3])
        for i in range(100):
            play_game(1000, p_random, p_player, (p_random, p_player), False)
        player_time = time.time() - start
        print('%s elapsed: %f seconds' % (p_player[3], player_time))
        print('%s is %.1fx slower than p_rock' % (p_player[3], player_time / rock_time))

    
    else:
        logging.error('i don\'t know how to "%s". look at the source' % c)
        print(HELP)
        sys.exit()
