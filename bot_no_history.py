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

    return '%s%s' % (max_count, max_die)
