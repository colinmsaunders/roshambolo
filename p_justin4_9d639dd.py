# justin.py -- my liar's dice robot

import random,logging,math

round_counter = 0.0
game_counter = 0
round_average_list = []
round_average = 0.0
player_dict = {}
truthDict = {}
flag = 'false'
last_bid = ''
prev_dice_count = 5
prev_bid = ''
prev_reason = 0
liar_count = 0
correctLiar = 0
incorrectLiar = 0
LiarCalledOnMe_count = 0
correctCalled = 0
CalledOnIncorrectBid = 0
avoidedCall_count = 0
shouldHaveCalledLiar = 0
bidding_losing_log = [0,0,0,0,0,0,0]
bidding_winning_log = [0,0,0,0,0,0,0]

def get_play(me,hands,history) :
    
    # figure out the previous call
    #
    if 0 == len(history) :
        prev_quantity,prev_face = 0,0
        
    else :
        x = int(history.split(',')[-1].split(':')[1])
        prev_quantity,prev_face = x // 10,x % 10
        #logging.info('%s is the prev_quantity on justin' % prev_quantity)
    
    if me not in history:
        global round_counter
        round_counter = 0.0
        
    else:
        global round_counter
        round_counter = round_counter + 1.0
        
    if ((prev_quantity == 0) and (len(history) != 0)):
        global flag
        flag = 'true'
        
        average_round_length(round_counter)
        all_hands = {}
        list_of_players = []
        list_of_bids = []
        total_dice = 0
        total_dice_real = ''
        for i in hands.split(',') :
            who,dice = i.split(':')
            all_hands[who] = dice
            list_of_players.append(who)
            total_dice = total_dice + len(dice)
            total_dice_real = total_dice_real + dice
            if who == me:
                global prev_dice_count
                prev_dice_count = len(dice)
        
        
        first_bid_flag = 0
        the_round = 0
        first_bid_player = ''
        list_count = 0
        history_list = []
        for i in history.split(',') :
            who,theBid = i.split(':')
            if int(theBid) != 0:
                if first_bid_player == who:
                    the_round = the_round + 1
                if first_bid_flag == 0:
                    first_bid_player = who
                    the_round = the_round + 1
                first_bid_flag = 1
                
                new_bid = bid(who, the_round, theBid, all_hands[who], total_dice)
                
                list_of_bids.append(new_bid)
            history_formatted = the_history(who,theBid,list_count,prev_reason,total_dice_real)
            list_count = list_count + 1
            history_list.append(history_formatted)
        #logging.info('length of list ' + str(len(list_of_bids)))
        
        icalledLiar = ''
        wascorrect = ''
        LiarCalledOnMe = ''
        avoidedcall = ''
        
        if history_list[list_count-1].name == me:
            icalledLiar = 'true'
            global liar_count
            liar_count = liar_count + 1
            if history_list[list_count-2].truth == 0:
                wascorrect = 'true'
                global correctLiar 
                correctLiar = correctLiar + 1
                global bidding_winning_log
                bidding_winning_log[prev_reason] = bidding_winning_log[prev_reason] + 1
            else:
                wascorrect = 'false'
                global incorrectLiar
                incorrectLiar = incorrectLiar + 1
                global bidding_losing_log
                bidding_losing_log[prev_reason] = bidding_losing_log[prev_reason] + 1
            logging.info('i called liar and I was ' + wascorrect)
        elif history_list[list_count-2].name == me:
            LiarCalledOnMe = 'true'
            global LiarCalledOnMe_count
            LiarCalledOnMe_count = LiarCalledOnMe_count + 1
            if history_list[list_count-2].truth == 1:
                wascorrect = 'true'
                global correctCalled
                correctCalled = correctCalled + 1
                global bidding_winning_log
                bidding_winning_log[prev_reason] = bidding_winning_log[prev_reason] + 1
            else:
                wascorrect = 'false'
                global CalledOnIncorrectBid
                CalledOnIncorrectBid = CalledOnIncorrectBid + 1
                global bidding_losing_log
                bidding_losing_log[prev_reason] = bidding_losing_log[prev_reason] + 1
                if history_list[list_count-3].truth == 0:
                    global shouldHaveCalledLiar
                    shouldHaveCalledLiar = shouldHaveCalledLiar + 1
            logging.info('liar was called on me and I was ' + wascorrect)
        else:
            avoidedcall = 'true'
            global avoidedCall_count
            avoidedCall_count = avoidedCall_count + 1
            global bidding_winning_log
            bidding_winning_log[prev_reason] = bidding_winning_log[prev_reason] + 1
            #logging.info('liar wasnt called on me and I didnt call it either')
                
        global game_counter
        game_counter = game_counter + 1
        
        #logging.info('SCORE I have called liar ' + str(liar_count) + ' many times and was correct ' + str(correctLiar) + ' many times and incorrect ' + str(incorrectLiar) + ' many times')
        #logging.info('SCORE I have been called a liar ' + str(LiarCalledOnMe_count) + ' many times and was correct ' + str(correctCalled) + ' many times and incorrect ' + str(CalledOnIncorrectBid) + ' many times')
        #logging.info('SCORE I wasnt called ' + str(avoidedCall_count) + ' many times and total games are at ' + str(game_counter))
        #logging.info('SCORE I was called a liar ' + str(LiarCalledOnMe_count) +  ' times and i should have called liar on ' + str(shouldHaveCalledLiar) + ' of those')
        g = 0
        while g < 7:
            #logging.info('SCORE strategy ' + str(g) + ' was responsible for ' + str(bidding_winning_log[g]) + ' wins and ' + str(bidding_losing_log[g]) + ' losses')
            g = g + 1
        
        global player_dict
        for thisBid in list_of_bids:
            if thisBid.name in player_dict:
                player_dict[thisBid.name].list_of_bids.append(thisBid)
            else:
                aPlayer = player(thisBid.name)
                aPlayer.list_of_bids = [thisBid]
                player_dict[thisBid.name] = aPlayer
                
            global truthDict
            if thisBid.name in truthDict:
                if thisBid.bid_truth == 1.0:
                    truthDict[thisBid.name].true_count = truthDict[thisBid.name].true_count + 1.0
                truthDict[thisBid.name].total_count = truthDict[thisBid.name].total_count + 1.0
            else:
                truthDict[thisBid.name] = truthCount(thisBid.name, thisBid.bid_truth, 1.0)
        
        for onePlayer in truthDict:
            truthDict[onePlayer].true_percent = truthDict[onePlayer].true_count/truthDict[onePlayer].total_count
            #logging.info('the truth percent for player ' + truthDict[onePlayer].name + ' is: ' + str(truthDict[onePlayer].true_percent))
        
    # count the total number of dice
    #
    num_dice = sum(map(lambda x : len(x.split(':')[1]),hands.split(',')))
 
    # find my hand
    #
    my_hand = None
    other_dice = 0
    for i in hands.split(',') :
        who,dice = i.split(':')
        if who == me :
            my_hand = dice
        else:
            other_dice = other_dice + len(dice)
    
    #define function to calculate binomial coeffecients C(n,r)
    def nCr(n,r):
        f = math.factorial
        return f(n) / f(r) / f(n-r)
    
    #function to find the probability of at least r dice of a give face given n unknown dice    
    def probAtLeast(n,r):
        sum = 0
        n = float(n)
        r = float(r)
        while r <= n:
            sum = sum + nCr(n,r)*pow((1.0/6.0),r)*pow((5.0/6.0),(n-r))
            r = r + 1
        return sum
    
    #given my hand, what are the probabilities of all next bids
    def probOfBids (prev_quantity,prev_face,my_hand,other_dice):
        i = 0
        dict_of_bid_probs = {}
        new_quantity = prev_quantity
        new_face = prev_face
        each_die_count = [0,my_hand.count('1'),my_hand.count('2'),my_hand.count('3'),my_hand.count('4'),my_hand.count('5'),my_hand.count('6')]
        while i < 6 :
            if new_face < 6 :
                new_face = new_face + 1
            else:
                new_face = 1
                new_quantity = new_quantity + 1
            new_quantity_string = str(new_quantity)
            new_face_string = str(new_face)
            quantity_face_asString = new_quantity_string + new_face_string
            if (new_quantity-each_die_count[new_face]) < 0:
                dict_of_bid_probs[quantity_face_asString] = 1.0
            else:
                dict_of_bid_probs[quantity_face_asString] = probAtLeast(other_dice,(new_quantity-each_die_count[new_face]))
                #logging.info('%d is the dict' % dict_of_bid_probs[quantity_face_asString])
                
            i = i + 1
        return dict_of_bid_probs
        
    def probOfBidsAssumingWeKnowMore (prev_quantity,prev_face,my_hand,other_dice):
        i = 0
        dict_of_bid_probs = {}
        new_quantity = prev_quantity
        new_face = prev_face
        each_die_count = [0,my_hand.count('1'),my_hand.count('2'),my_hand.count('3'),my_hand.count('4'),my_hand.count('5'),my_hand.count('6')]
        while i < 6 :
            if new_face < 6 :
                new_face = new_face + 1
            else:
                new_face = 1
                new_quantity = new_quantity + 1
            new_quantity_string = str(new_quantity)
            new_face_string = str(new_face)
            quantity_face_asString = new_quantity_string + new_face_string
            if (new_quantity - (each_die_count[new_face] + 1 )) < 0:
                dict_of_bid_probs[quantity_face_asString] = 1.0
            else:
                dict_of_bid_probs[quantity_face_asString] = probAtLeast((other_dice - 1),(new_quantity-(each_die_count[new_face]+1)))
                #logging.info('%d is the dict' % dict_of_bid_probs[quantity_face_asString])
                
            i = i + 1
        return dict_of_bid_probs
    
    #logging.info(type(float(prev_quantity)-float(my_hand.count(prev_face))))
    global prev_bid
    global prev_reason
    
    if prev_quantity == 0:
        newterm = random.randint(1,6)
        logging.info('random int is: ' + str(newterm))
        newterm_s = str(newterm)
        thisdumnbid = '1' + newterm_s
        logging.info('random bid is: ' + str(thisdumnbid))
        prev_bid = 'thisdumnbid'
        prev_reason = 0
        return '11'
    
    #determining what the next bid is
    if prev_face == 6:
        next_bid_face = '1'
        next_bid_quantity = str(prev_quantity + 1);
        next_bid = next_bid_quantity + next_bid_face
    else:
        next_bid_face = str(prev_face + 1)
        next_bid_quantity = str(prev_quantity)
        next_bid = next_bid_quantity + next_bid_face
    
    #find the probability of the last bid being true
    if (prev_quantity-my_hand.count(str(prev_face))) < 0:
        prob_of_last_bid = 1.0
    else:
        prob_of_last_bid = probAtLeast(other_dice, (prev_quantity-my_hand.count(str(prev_face))))
    
    #find the probability of the next 6 bid options
    dict_of_bid_probs_pre = probOfBids(prev_quantity,prev_face,my_hand,other_dice)
    
    if flag == 'true':
        #find the probability of the next 6 bids if we knew one more die*
        dict_of_bid_probs_if = probOfBidsAssumingWeKnowMore(prev_quantity,prev_face,my_hand,other_dice)
        
        dict_of_diff = {}
        for oneBid in dict_of_bid_probs_if:
            dict_of_diff[oneBid] = dict_of_bid_probs_if[oneBid]-dict_of_bid_probs_pre[oneBid]
            #logging.info('the difference of one more ' + str(oneBid) + ' makes this much diff ' + str(dict_of_diff[oneBid]))
            #logging.info('the difference of knowing more ' + str(oneBid) + ' makes this much diff ' + str(dict_of_bid_probs_if[oneBid]))
            #logging.info('without knowing ' + str(oneBid) + ' makes this much diff ' + str(dict_of_bid_probs_pre[oneBid]))
        
        list_of_guess = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        for i in history.split(',') :
            who,theBid = i.split(':')
            if who != me:
                x = int(theBid)
                the_quantity,the_face = x // 10,x % 10
                list_of_guess[the_face] = list_of_guess[the_face] + truthDict[who].true_percent
        
        dict_of_bid_probs_REAL = {}
        
        for biddie in dict_of_diff:
            x = int(biddie)
            the_quantity,the_face = x // 10,x % 10
            increased_chances_bid = (list_of_guess[the_face]*dict_of_diff[biddie]) #potenitally modify this to me a smaller value
            dict_of_bid_probs_REAL[biddie] = dict_of_bid_probs_pre[biddie] + increased_chances_bid
            #logging.info('for bid: ' + str(biddie) + ' the increase due to others is: ' + str(increased_chances_bid) + ' giving us total of: ' + str(dict_of_bid_probs_REAL[biddie]))
    else:
        dict_of_bid_probs_REAL = dict_of_bid_probs_pre
    
    current_option_value = 0.0
    for a_bid in dict_of_bid_probs_REAL:
        new_option_value = dict_of_bid_probs_REAL[a_bid]
        #logging.info('the bid: ' + a_bid + ' has a ' + str(new_option_value) + '% chance of being true')
        if (new_option_value > current_option_value):
            current_option_value = new_option_value
            current_option = a_bid
            
    #find the probability of the next bid being true
    prob_of_next_bid = dict_of_bid_probs_REAL[next_bid]
    
    #logging.info('the odds of my next bid are ' + str(prob_of_next_bid))
    #logging.info('the odds of my best bid are ' + str(current_option_value))
    #logging.info('the odds of their bid are ' + str(prob_of_last_bid))
    #logging.info('my bid is more likely than their bid ' + str(current_option_value >= prob_of_last_bid))
    #logging.info('their bid is not very unlikely ' + str((prob_of_last_bid > float('0.05'))))

    if ((current_option_value == 0.0) or (prob_of_last_bid == 0.0)):
        #logging.info('option 1')
        prev_bid = '0'
        prev_reason = 1
        return 0 
    if (prob_of_last_bid < 0.05):
        #logging.info('Their bid is true less than 5% of the time')
        prev_bid = '0'
        prev_reason = 2
        return 0
    #if prob_of_next_bid > 0.50:
        #prev_bid = next_bid
        #prev_reason = 3
        #return next_bid
    if (prob_of_last_bid > 0.15) and (current_option_value > 0.10):
        myBid = int(current_option)
        #logging.info('made bid because theres is more than 15% and mine is above 5%')
        prev_bid = myBid
        prev_reason = 4
        return myBid
    #if (current_option_value >= prob_of_last_bid) :
        #myBid = int(current_option)
        #logging.info('made bid because the probability of my hand is greater than theres')
        #prev_bid = myBid
        #prev_reason = 5
        #return myBid
    else:
        #logging.info('option 3')
        prev_bid = '0'
        prev_reason = 6
        return 0

def average_round_length(round_counter):
    global round_average_list
    round_average_list.append(round_counter)
    global round_average
    round_average = sum(round_average_list) / float(len(round_average_list))
    
class bid:
    
    def __init__(self, name, round_counter, the_bid, their_dice, total_dice):
        self.name = name
        self.bid_round = round_counter
        self.total_dice = total_dice
        self.their_dice = their_dice
        self.their_dice_number = len(their_dice)
        self.bid = the_bid
    
        def bid_true(the_bid, their_dice):
            x = int(the_bid)
            the_quantity,the_face = x // 10,x % 10
            if str(the_face) in their_dice:
                return 1.0                          #true
            else:
                return 0.0
                
        self.bid_truth = bid_true(the_bid, their_dice)
            
class player:
    
    def __init__(self, name):
        self.name = name
        self.list_of_bids = []
        
class truthCount:
    
    def __init__(self, name, true_count, total_count):
        self.name = name
        self.true_count = true_count
        self.total_count = total_count
        self.true_percent = true_count/total_count

class the_history:

    def __init__(self, who, theBid, list_count, prev_reason, total_dice_real):
        self.name = who
        self.theBid = theBid
        self.list_count = list_count
        self.prev_reason = prev_reason
        self.total_dice_real = total_dice_real
        
        def bid_truth(theBid, total_dice_real):
            x = int(theBid)
            the_quantity,the_face = x // 10,x % 10
            each_die_count = [0,total_dice_real.count('1'),total_dice_real.count('2'),total_dice_real.count('3'),total_dice_real.count('4'),total_dice_real.count('5'),total_dice_real.count('6')]
            if each_die_count[the_face] < the_quantity:
                truthis = 0
            else:
                truthis = 1
            return truthis
        
        self.truth = bid_truth(theBid, total_dice_real)