# robot.py -- sample liar's dice robot

# See README.md for instructions on how to
# write a robot, or look at computer.py for
# an example.


def get_play(me, hands, history):
    # 'A:16631,B:xxxxx'
    counts = {}
    opponent_max = 0
    max_card = 0
    max_count = 0
    highest_card = 0
    my_max = None
    players = hands.split(',')

    for player in players:
        pname, cards = player.split(':')

        if pname == me:
            for card in cards:
                card = int(card)

                if card in counts:
                    counts[card] += 1
                else:
                    counts[card] = 1

            my_max = len(cards)
        else:
            opponent_max = len(cards)

    for card, count in counts.iteritems():
        if card > highest_card:
            highest_card = card

        if count > max_count:
            max_count = count
            max_card = card

    if max_count < 2:
        max_card = highest_card
        if my_max == 1 and opponent_max == 1:
            max_count = 1
        else:
            max_count = 2

    return '%s%s' % (max_count, max_card)
