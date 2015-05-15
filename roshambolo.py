#!/usr/bin/python

# roshambolo.py -- console harness

HELP = '''\
usage:

    To play a race to 10 game between p_rock and p_random:

        $ python roshambolo.py game 10 p_rock p_random

    To play a round robin tourney of best of 100 races to 10000
    between p_rock and p_robot and p_random:

        $ python roshambolo.py tourney 100 10000 p_rock p_robot p_random

    To time your bot to make sure it's not too slow:

        $ python roshambolo.py time p_robot
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


def get_play(game_id, player, opponent, catch_exceptions):
    play = 0
    start = time.clock()
    try:
        play = int(player[1](game_id, player[0], opponent[0]))
    except KeyboardInterrupt:
        raise
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" calling %s \'s play() function'
                     % (sys.exc_info()[1], player[2]))
    elapsed = time.clock() - start
    player[4] += 1
    player[5] += elapsed
    if play < 1 or play > 3:
        play = random.randint(1, 3)
#    logging.debug('PLAY\t%d\t%d\t%d\t%s plays %s' %
#                  (player[0], opponent[0], play, player[3],
#                  VERBOSE_PLAYS[play]))
    return play


def observe_play(player, game_id, his_id, her_id, his_play, her_play,
                 result, catch_exceptions):
    try:
        player[2](game_id, his_id, her_id, his_play, her_play, result)
    except KeyboardInterrupt:
        raise
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" calling %s \'s observe() function'
                     % (sys.exc_info()[1], player[3]))
    return


def play_game(game_id, race_to, player1, player2, observers, catch_exceptions):
    wins = [0, 0]
    plays = [[-1, 0, 0, 0], [-1, 0, 0, 0]]
    while 1:
        a_play = get_play(game_id, player1, player2, catch_exceptions)
        b_play = get_play(game_id, player2, player1, catch_exceptions)
        ties = 0
        if a_play == b_play:
            ties += 1
            x = plays[0][a_play] - plays[1][b_play]
            if 0 == x:
                ties += 1
                x = plays[0][BEAT_BY[a_play]] - plays[1][BEAT_BY[b_play]]
                if 0 == x:
                    ties += 1
                    winner = random.randint(0, 1)
                elif 0 < x:
                    winner = 0
                else:
                    winner = 1
            elif 0 < x:
                winner = 0
            else:
                winner = 1
        else:
            winner = 0
            if BEATS[b_play] == a_play:
                winner = 1
        plays[0][a_play] += 1
        plays[1][b_play] += 1
        if 0 == winner:
            wins[0] += 1
        else:
            wins[1] += 1
#        logging.debug('GAME\t%d\t%d\t%d\t%d\t%d\t%s\t%s'
#                      % (wins[0], wins[1],
#                         a_play, b_play, winner,
#                         [player1[3], player2[3]][winner],
#                         [player1[3], player2[3]][1 - winner]))
        for i in observers:
            if None == i[2]:
                continue
            observe_play(i, game_id, player1[0], player2[0],
                         a_play, b_play, winner, catch_exceptions)
        if wins[0] == race_to:
            logging.debug('G_RESULT\t%s beat %s' % (player1[3], player2[3]))
            return 0
        if wins[1] == race_to:
            logging.debug('G_RESULT\t%s beat %s' % (player2[3], player1[3]))
            return 1


def play_tourney(t, n, players):
    scores = {}
    for i in players:
        scores[i[0]] = [i, 0]
    game_id = 0
    for r in range(t):
        random.shuffle(players)
        for i in range(len(players)):
            for j in range(len(players)):
                if i >= j:
                    continue
                game_id += 1
                x = play_game(game_id, n, players[i], players[j], players, True)
                if 0 == x:
                    scores[players[i][0]][1] += 1
                else:
                    scores[players[j][0]][1] += 1
                logging.info('TOURNEY\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s' % (
                             game_id, t, i, j, scores[players[i][0]][1],
                             scores[players[j][0]][1],
                             players[i][3], players[j][3]))
        k = scores.keys()
        k.sort(key=lambda x: scores[x][1], reverse=True)
        logging.info('SCORE\t%d' % r)
        for i in k:
            logging.info('SCORE\t%d\t%d\t%s' %
                         (r, scores[i][1], scores[i][0][3]))
    logging.info('T_RESULT\t%s wins the tournament' % scores[k[0]][0][3])


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
    return [player_id, f_play, f_observe, playername, 0, 0.0]


if __name__ == '__main__':

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
        logging.basicConfig(level=logging.DEBUG, format='%(message)s',
                            stream=sys.stdout)
        n = int(sys.argv[2])
        playernames = sys.argv[3:5]
        random.shuffle(playernames)
        player1 = make_player(1, playernames[0], False)
        player2 = make_player(2, playernames[1], False)
        x = play_game(0, n, player1, player2, (player1, player2), False)
        sys.exit()

    elif 'human' == c:
        n = int(sys.argv[2])
        player1 = make_player(1, 'p_human', False)
        player2 = make_player(2, sys.argv[3], False)
        x = play_game(0, n, player1, player2, (player1, player2), False)
        sys.exit()

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
        sys.exit()

    elif 'time' == c:
        p1 = make_player(1, 'p_random', False)
        p2 = make_player(2, 'p_random', False)
        p3 = make_player(3, 'p_rock', False)
        p4 = make_player(4, sys.argv[2], False)
        print('playing 100 games to 1000 between random and rock and random ...')
        play_tourney(100, 1000, [p1, p3, p2])
        print('playing 100 games to 1000 between random and rock and %s ...' % p4[3])
        play_tourney(100, 1000, [p1, p3, p4])
        print('p_random clock time: %f, %s clock time: %f' % (p2[5], p4[3], p4[5]))
        print('%s is %.1fx slower than p_random' % (p4[3], p4[5] / p2[5]))
        sys.exit()

    else:
        logging.error('i don\'t know how to "%s". look at the source' % c)
        print(HELP)
        sys.exit()
