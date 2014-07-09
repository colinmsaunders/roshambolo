# peakedtoosoon.py -- Go big then go home
import random
import logging

def get_play(me, hands, history):
    current_hands = extract_hands_from_input(hands)
    if me not in current_hands:
        # Not even in the game any more, my bot sucks
        return 0

    play_history = extract_history_from_input(history)
    my_hand = get_my_dice_data(me, current_hands[me])
    game_state = get_game_state_from_hands(current_hands, my_hand)

    # Find the best call current hand can make
    max_key = None
    hist = my_hand['histogram']
    for a_key in hist:
        if max_key == None or (hist[a_key] > hist[max_key]) or (hist[a_key] == hist[max_key] and a_key > max_key):
            max_key = a_key

    logging.debug("Best individual hand is %d %d" % (hist[max_key], max_key))
    logging.debug("Best call available is %d %d" % (hist[max_key] + game_state['expected_face_count'], max_key))

    # Note 1: If this is worse than the current best call, game assumes we're calling liar.
    # Note 2: This algorithm makes the same call every time.  If a single game gets back to it,
    # the game will be at a higher count, which will essentially trigger a liar call from the second call.
    return "%d%d" % (hist[max_key] + game_state['expected_face_count'], max_key)


def extract_hands_from_input(hands):
    current_hands = {}
    for a_player in hands.split(','):
        (player_id, player_dice) = a_player.split(':')
        current_hands[player_id] = player_dice
    logging.debug("Current hands: %s" % current_hands)
    return current_hands


def extract_history_from_input(history):
    play_history = []
    if history:
        for a_play in history.split(','):
            (player_id, raw_play) = a_play.split(':')
            play_history.append({'id': player_id,
                                 'value': int(raw_play) % 10,
                                 'quantity': int(raw_play) // 10})
    logging.debug("Play history: %s" % play_history)
    return play_history


def get_my_dice_data(me, roll_list):
    hand_data = {'raw_roll_list': roll_list,
                 'id': me,
                 'values': [],
                 'histogram': {}}
    for a_roll in roll_list:
        roll_val = int(a_roll)
        hand_data['values'].append(roll_val)
        if roll_val not in hand_data['histogram']:
            hand_data['histogram'][roll_val] = 0
        hand_data['histogram'][roll_val] += 1
    logging.debug("Hand data: %s" % hand_data)
    return hand_data


def get_game_state_from_hands(all_hands, my_hand):
    game_state = {'total_dice': 0}
    for a_hand in all_hands:
        if a_hand == my_hand['id']:
            continue
        game_state['total_dice'] += len(all_hands[a_hand])
    game_state['expected_face_count'] = int(round(game_state['total_dice'] / 6))
    logging.debug("Game state: %s" % game_state)
    return game_state
