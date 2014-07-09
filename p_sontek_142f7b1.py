# sontek_smart.py -- sample liar's dice robot
import math
import random

h_data = { 'first': {}, 'one_on_one': {} }


def comb(n, r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)

def get_lowest(hand):
    lowest_dice = lowest_count = 6

    for dice, count in hand.iteritems():
        if count < lowest_count:
            lowest_dice = dice
            lowest_count = count

    return (lowest_count, lowest_dice)


def get_best(hand):
    best_dice = best_count = 0

    for dice, count in hand.iteritems():
        if count >= best_count:
            if dice > best_dice:
                best_dice = dice
                best_count = count

    return (best_count, best_dice)


def is_raise_possible(last_face, last_count, total_deese):
    if last_count < total_deese:
        return True
    elif last_count == total_deese and last_face < 6:
        return True
    else:
        return False


def get_known_raise(hand, last_dice, last_quantity):
    # Do we have anything in our hand that can beat the
    # last call?
    high_counts = {}

    for dice, count in hand.iteritems():
        # we need to be larger than the quantity
        if count < last_quantity:
            continue

        if count == last_quantity and dice > last_dice:
            high_counts[dice] = count
        elif count > last_quantity:
            high_counts[dice] = count

    best_count = 0
    best_dice = 0

    for dice, count in high_counts.iteritems():
        if count == best_count:
            if dice > best_dice:
                best_count = count
                best_dice = dice

        if count > best_count:
            best_count = count
            best_dice = dice

    if best_count == 0:
        return None
    else:
        return (best_count, best_dice)


def get_probability(combinations, unknown):
    count = 0.0

    q = combinations
    n = unknown

    for x in range(q, n):
        count += comb(n, x) * (1 / 6.0) ** x * (5/6.0) ** (n - x)

    return count


def process_history(hist):
    player, call = hist.split(':')
    call = int(call)

    dice = call % 10
    quantity = call // 10

    return (player, quantity, dice)


def get_game_state(me, hands, history):
    plays = hands.split(',')

    my_hand = {}
    total_dice = 0
    total_players = 0

    hand_counts = {}
    last_player = None
    last_dice = None
    last_quantity = None
    hist_plays = []

    for hand in plays:
        player, dice = hand.split(':')
        if player == me:
            for die in dice:
                die = int(die)
                my_hand[die] = my_hand.get(die, 0) + 1

        dice_count = len(dice)

        if dice_count > 0:
            hand_counts[player] = dice_count
            total_dice += len(dice)
            total_players += 1

    if len(history) > 0:
        hist_plays = [process_history(x) for x in history.split(',')]

        # A game is afoot!
        last_player, last_quantity, last_dice = hist_plays[-1]

    return {
        'plays': plays,
        'my_hand': my_hand,
        'total_dice': total_dice,
        'total_players': total_players,
        'hand_counts': hand_counts,
        'last_player': last_player,
        'last_quantity': last_quantity,
        'last_dice': last_dice,
        'hist_plays': hist_plays
    }


def truthy_play(state):
    my_hand = state['my_hand']
    last_dice = state['last_dice']
    last_quantity = state['last_quantity']
    last_player = state['last_player']

    total_dice = state['total_dice']

    can_raise = is_raise_possible(last_dice, last_quantity, total_dice)

    if can_raise:
        known_raise = get_known_raise(
            my_hand,
            last_dice,
            last_quantity
        )

        if known_raise is None:
            print("LOGIC 1")
            return

        known_count = known_raise[0]
        known_dice = known_raise[1]

        first_p, first_quantity, first_dice = state['hist_plays'][0]

        use_first_dice = False

        if first_p in h_data['first'] and known_dice == first_dice:
            p_data = h_data['first'][first_p]
            perc = p_data['truth_percentage']

            if perc >= .70 and p_data['total'] >= 100:
                use_first_dice = True

        if use_first_dice:
            known_count += 1

            if first_p != last_player:
                known_count += 1

        print("LOGIC 2")
        return '%s%s' % (known_count, known_dice)
    else:
        print("LOGIC 3")
        return 0


def large_game_play(state):
    my_hand = state['my_hand']
    last_dice = state['last_dice']
    last_quantity = state['last_quantity']
    last_player = state['last_player']
    total_dice = state['total_dice']

    my_quantity = my_hand.get(last_dice, 0)

    first_p, first_quantity, first_dice = state['hist_plays'][0]

    use_first_dice = False

    if first_p in h_data['first'] and last_dice == first_dice:
        p_data = h_data['first'][first_p]
        perc = p_data['truth_percentage']

        if (perc >= .70 and
            p_data['total'] >= 100 and
            first_dice in my_hand
        ):
            use_first_dice = True

    if last_quantity > my_quantity:
        qty = (last_quantity - my_quantity) - 1

        if use_first_dice and qty > 0:
            qty = qty -1

    else:
        # If we have more of the dice type than they
        # are guessing, we should just autoraise
        print("LOGIC 4")
        return '%s%s' % (last_quantity+1, last_dice)

    unknowns = total_dice - len(my_hand)

    prob_truth = get_probability(qty, unknowns)
    prob_raise = get_probability(qty+1, unknowns)
    probability_difference = prob_truth - prob_raise

    print ("-----------------------------------------")
    print("guessed: %s" % last_quantity)
    print("qty: %s, unknowns %s" % (qty, unknowns))
    print("probability: %s" % prob_truth)
    print("probability+1: %s" % prob_raise)
    print("probability diff: %s" % probability_difference)
    print ("-----------------------------------------")

    best_count, best_dice = get_best(my_hand)
    # There is a 50% chance they are lieing!
    if prob_truth <= .55:
        if best_count >= 2 and total_dice / last_quantity > 3:
            if best_dice > last_dice:
                print("LOGIC 5")
                return '%s%s' % (last_quantity, best_dice)

        print("LOGIC 6")
        return 0

    # At this point they are probably telling the truth
    acceptable_bluff = (len(my_hand) + state['total_players']) - 3

    if acceptable_bluff > last_quantity and best_count > 2:
        if best_dice > last_dice:
            print("LOGIC 8")
            return '%s%s' % (last_quantity, best_dice)
        else:
            print("LOGIC 9")
            return '%s%s' % (last_quantity+1, best_dice)

    if best_dice > last_dice:
        print("LOGIC 10")
        return '%s%s' % (last_quantity, best_dice)
    elif prob_raise >= .45:
        print("LOGIC 7")
        return '%s%s' % (last_quantity+1, last_dice)
    elif last_dice != 6:
        print("LOGIC 11")
        return '%s%s' % (last_quantity, last_dice+1)
    elif qty <= 2:
        print("LOGIC 12")
        return '%s%s' % (last_quantity+1, best_dice)

    print("LOGIC 13")
    return 0


def one_on_one_play(state):
    # when we are in small game play, we need to be more honest.
    my_hand = state['my_hand']
    hand_counts = state['hand_counts']
    last_dice = state['last_dice']
    last_quantity = state['last_quantity']
    last_player = state['last_player']
    total_dice = state['total_dice']

    their_count = hand_counts[last_player]
    my_dice_count = my_hand.get(last_dice, 0)

    if last_quantity > their_count:
        if last_dice not in my_hand:
            print("LOGIC 20")
            return 0

        if their_count == 1:
            if my_dice_count + 1 == last_quantity:
                # They are telling the truth here. We need to bluff.
                return
            else:
                print("LOGIC 21")
                return 0


def get_play(me, hands, history):
    global h_data

    state = get_game_state(me, hands, history)

    # no plays have happened so far, just return smallest
    # dice to return the ball rolling
    if 0 == len(history):
        best_count, best_dice = get_best(state['my_hand'])

        # We are one on one, lets tell a lie!
        if state['total_players'] == 2 and len(state['my_hand']) > 0:
            if best_count > 1:
                print("LOGIC 14")
                return '%s%s' % (best_count, best_dice)

            random_dice = random.randint(1, 6)
            print("LOGIC 15")
            return '%s%s' % (1, random_dice)

        print("LOGIC 16")
        return '%s%s' % (best_count, best_dice)
    else:
        # We are in a liar call, lets track history
        if 0 == state['last_dice']:
            first_p, first_quantity, first_dice = state['hist_plays'][0]

            tmp_hdata = {}
            for hp, hq, hd in state['hist_plays']:
                if hp not in tmp_hdata:
                    tmp_hdata[hp] = {}

                if hd not in tmp_hdata[hp]: 
                    tmp_hdata[hp][hd] = []

                tmp_hdata[hp][hd].append(hq)

            historical_hands = history.split(',')

            h_data['all_time'] = {}

            for hand in historical_hands:
                player, dice = hand.split(':')

                if player not in h_data['all_time']:
                    h_data['all_time'][player] = {
                        'total': 0.0,
                        'truths': 0.0,
                        'lies': 0.0,
                    }

                h_data['all_time'][player]['total'] += 1.0

                if dice in tmp_hdata[player]:
                    h_data['all_time'][player]['truths'] += 1.0
                else:
                    h_data['all_time'][player]['lies'] += 1.0

                all_truths = h_data['all_time'][player]['truths']
                all_lies = h_data['all_time'][player]['lies']
                all_total = h_data['all_time'][player]['total']
                perc =  all_truths / all_total

                h_data['all_time'][player]['truth_percentage'] = perc
                    
                if player == first_p:
                    dice_count = dice.count(str(first_dice))
                    # Do they tell the truth on first play?
                    if first_p not in h_data['first']:
                        h_data['first'][first_p] = {
                            'total': 0.0,
                            'truths': 0.0,
                            'lies': 0.0,
                            'qty_truths': 0.0,
                            'qty_lies': 0.0,
                        }

                    h_data['first'][first_p]['total'] += 1.0

                    if dice_count > 0:
                        h_data['first'][first_p]['truths'] += 1.0
                        if first_quantity == dice_count:
                            h_data['first'][first_p]['qty_truths'] += 1.0
                        else:
                            h_data['first'][first_p]['qty_lies'] += 1.0

                    else:
                        h_data['first'][first_p]['lies'] += 1.0

                    truths = h_data['first'][first_p]['truths']
                    total = h_data['first'][first_p]['total']
                    perc = truths / total

                    h_data['first'][first_p]['truth_percentage'] = perc
            return 0

        # Are they being crazy and guessing they
        # know all the dice in play?
        if state['last_quantity'] >= state['total_dice']:
            print("LOGIC 17")
            return 0

        print ("=============================")
        print("TOTAL PLAYERS: %s" % state['total_players'])
        print("TOTAL_DICE: %s" % state['total_dice'])
        print("COUNTS: %s" % state['hand_counts'])
        print("H_DATA: %s" % h_data)
        print("=============================")
        truth_results = truthy_play(state)

        # If we can't tell the truth, lets start bluffing!!
        if truth_results is not None:
            return truth_results

        if state['total_players'] == 2 and len(state['my_hand']) > 0:
            one_results = one_on_one_play(state)

            if one_results is not None:
                return one_results

        return large_game_play(state)
