#!/usr/bin/python

# roshambozo.py -- console harness

HELP = '''\
usage:

    To play a race to 10 between p_rock and p_random:

        $ python roshambozo.py game 10 p_rock p_random

    To play a round robin tourney of best of 100 races to 10000
    between p_rock and p_robot and p_random:

        $ python roshambozo.py tourney 100 10000 p_rock p_robot p_random
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


def get_play(playername, f_get_play, opponent_id, state, catch_exceptions):
    play = 0
    try:
        play = int(f_get_play(opponent_id, state & 3, (state >> 2) & 3, (state >> 6) & 1))
    except KeyboardInterrupt:
        raise
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" calling %s \'s get_play() function'
                     % (sys.exc_info()[1], str(f_get_play)))
    if play < 1 or play > 3:
        play = random.randint(1, 3)
    logging.debug('PLAY\t%d\t%d\t%d\t%d\t\t%s plays %s' % (state & 3, (state >> 2) & 3, (state >> 6) & 1, play, playername, VERBOSE_PLAYS[play]))
    return play


def play_game(race_to, a_playername, b_playername, f_get_play_a, f_get_play_b, a_id, b_id, catch_exceptions):
    wins = [0, 0]
    plays = [[-1, 0, 0, 0], [-1, 0, 0, 0]]
    last_a = last_b = 0
    while 1:
        a_play = get_play(a_playername, f_get_play_a, b_id, last_a, catch_exceptions)
        b_play = get_play(b_playername, f_get_play_b, a_id, last_b, catch_exceptions)
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
        last_a = a_play | (b_play << 2) | (ties << 4) | (a_won << 6)
        last_b = b_play | (a_play << 2) | (ties << 4) | ((1 - a_won) << 6)
        if a_won:
            wins[0] += 1
        else:
            wins[1] += 1
        logging.debug('GAME\t%d\t%d\t%d\t%d\t%d\t%s beat %s'
                      % (wins[0], wins[1], a_play, b_play, a_won, 
                      [a_playername, b_playername][a_won], 
                      [b_playername, a_playername][1 - a_won]))
        if wins[0] == race_to:
            return 0
        if wins[1] == race_to:
            return 1


def split_playername(playername):
    parts = playername.split(':')
    if 1 == len(parts):
        return (parts[0], None, parts[0], 'get_play')
    if 2 == len(parts):
        return ('%s_%s' % (parts[0], parts[1]), None, parts[0], parts[1])
    if 3 == len(parts):
        return ('%s_%s' % (parts[0], parts[1]), parts[2], parts[3])
    raise Exception('i don\'t know how to parse "%s"' % playername)


def make_player(playername, catch_exceptions):
    name, path, modulename, attr = split_playername(playername)
    fp = pathname = description = m = None
    try:
        if None == path:
            fp, pathname, description = imp.find_module(modulename)
        else:
            fp, pathname, description = imp.find_module(modulename, [path, ])
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" finding module %s' 
                     % (sys.exc_info()[1], modulename))
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
    f = getattr(m, attr)
    return f


def play_tourney(t, n, playernames):
    scores = {}
    players = []
    for i in playernames:
        f = make_player(i, True)
        scores[len(players)] = 0
        players.append(f)
    for r in range(t):
        for i in range(len(players)):
            for j in range(len(players)):
                if i >= j:
                    continue
                x = play_game(n, playernames[i], playernames[j], players[i], players[j], i, j, True)
                if 0 == x:
                    scores[i] += 1
                else:
                    scores[j] += 1
                logging.info('SCORE\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s' % (
                             r, t, i, j, scores[i], scores[j], 
                             playernames[i], playernames[j]))
        logging.info('STATUS\t%.2f\t\t%s' % (r / float(t), ','.join(
                     ['%s:%s' % (playernames[i], scores[i]) for i in range(len(players))])))
    logging.info('STATUS\t%.2f\t\t%s' % (100.0, ','.join(['%s:%s' 
                 % (playernames[i], scores[i]) for i in range(len(players))])))


def main(argv):
    if 1 == len(argv):
        print(HELP)
        sys.exit()

    c = argv[1]

    if 0:
        pass

    elif 'help' == c:
        print(HELP)
        sys.exit()

    elif 'game' == c:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s', stream=sys.stdout)
        n = int(sys.argv[2])
        a_player = make_player(argv[3], False)
        b_player = make_player(argv[4], False)
        x = play_game(n, argv[3], argv[4], a_player, b_player, 0, 1, False)
        return x

    elif 'tourney' == c:
        logging.basicConfig(level=logging.INFO, 
                format='%(asctime)s %(levelname)-7s %(message)s', stream=sys.stdout)
        t = int(sys.argv[2])
        n = int(sys.argv[3])
        playernames = sys.argv[4:]
        play_tourney(t, n, playernames)
        return
    
    else:
        logging.error('i don\'t know how to "%s". look at the source' % c)
        print(HELP)
        sys.exit()


if __name__ == '__main__':
    main(sys.argv)
