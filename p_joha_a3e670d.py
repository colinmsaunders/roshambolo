def get_play(me, hands, history):
    # 'A:16631,B:xxxxx'
    counts = {}
    opponent_max = 0
    max_die = 0
    max_count = 0
    highest_die = 0
    my_max = None
    hands = hands.split(',')

    for hand in hands:
        player, dice = hand.split(':')

        if player == me:
            for die in dice:
                die = int(die)

                if die in counts:
                    counts[die] += 1
                else:
                    counts[die] = 1

            my_max = len(dice)
        else:
            opponent_max = len(dice)

    for die, count in counts.iteritems():
        if die > highest_die:
            highest_die = die

        if count > max_count:
            max_count = count
            max_die = die

    if max_count < 2:
        max_die = highest_die
        if my_max == 1 and opponent_max == 1:
            max_count = 1
        else:
            max_count = 2
    # figure out the previous call
    #        
    if 0 == len(history):
        prev_quantity, prev_face = 0, 0
    else:
        x = int(history.split(',')[-1].split(':')[1])
        prev_quantity, prev_face = x // 10, x % 10
    # showdown? if so, just ignore
    #
    num_players = len(hands);

    # Joha's basic sauce (hot sauce did not work)
    if 0 == prev_quantity and len(history) > 0:
        return 0
    if len(history) > num_players*2:
        return 0        

    return '%s%s' % (max_count, max_die)
