# player.py -- sample player

def get_play(me, hands, history):
    ''' play lowest call i can amongst faces i have '''
    hands = hands.split(',')
    my_hand = {}
    my_max_face = 0
    for i in hands:
        player, dice = i.split(':')
        if me == player:
            for j in dice:
                j = int(j)
                if j > my_max_face:
                    my_max_face = j
                my_hand[j] = my_hand.get(j, 0) + 1
            break

    if 0 == len(history):
        last_call = 0
        last_face = 0
        last_quantity = 0
    else:
        last_play = history.split(',')[-1]
        last_player, last_call = last_play.split(':')
        last_call = int(last_call)
        if 0 == last_call:
            return 0
        last_face = last_call % 10
        last_quantity = last_call // 10

    if 0 == len(history):
        quantity = 1
    else:
        quantity = last_quantity
    while 1:
        for face in range(1, my_max_face + 1):
            if 0 == my_hand.get(face, 0):
                continue
            if quantity > last_quantity or face > last_face:
                return (quantity * 10) + face
        quantity += 1

