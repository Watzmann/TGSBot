#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Game-related utilities."""

REV = '$Revision$'

import logging
from version import Version

v = Version()
v.register(__name__, REV)

TRACE = 15
logging.addLevelName(TRACE, 'TRACE')
logging.basicConfig(level=logging.DEBUG,
                format='%(name)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('utilities')
#logger.setLevel(logging.DEBUG)

def check_roll_old(dice, position, nr_bar, direction):
    """Checks for possible moves depending on 'dice'."""
    exhausted = False
    list_of_moves = []  # TODO: lieber dict?
    pos = position      # TODO: vielleicht bei position bleiben
    d1, d2 = dice
    my_dice = list(dice[:])
    nr_of_moves = {True:4, False:2}[d1 == d2]
    # -------------------------------------------enter from the bar
    bar_moves = min(nr_of_moves, bar_nr)
    bar = direction['bar']
    if bar_moves:
        logger.info('der spieler hat %d moves von der bar (%d)' % \
                    (bar_moves, bar))
        for d in dice:
            if bar == 25:
                p = bar - d
                if pos[p] > -2:
                    if nr_of_moves == 2:
                        list_of_moves.append('bar-%d' % p)
                        my_dice.remove(d)
                        bar_moves -=1
                    else:
                        list_of_moves = ['bar-%d' % p,]*bar_moves
                        my_dice = [my_dice[0],]*(4-bar_moves)
                        bar_moves = 0
                        logger.info('pasch getested: bar %d  wurf %d   point %d   ' \
                             'checker %d  (%s) (%s) (%d)' % \
                             (bar,d,p,pos[p],list_of_moves,my_dice,bar_moves))
                        break
            elif bar == 0:
                p = bar + d
                if pos[p] < 2:
                    if nr_of_moves == 2:
                        list_of_moves.append('bar-%d' % p)
                        my_dice.remove(d)
                        bar_moves -=1
                    else:
                        list_of_moves = ['bar-%d' % p,]*bar_moves
                        my_dice = [my_dice[0],]*(4-bar_moves)
                        bar_moves = 0
                        logger.info('pasch getested: bar %d  wurf %d   point %d   ' \
                             'checker %d  (%s) (%s) (%d)' % \
                             (bar,d,p,pos[p],list_of_moves,my_dice,bar_moves))
                        break
            logger.info('hab getested: bar %d  wurf %d   point %d   ' \
                 'checker %d  (%s)' % (bar,d,p,pos[p],list_of_moves))
    if bar_moves > 0:
        nr_of_moves = len(list_of_moves)
        exhausted = True
    if exhausted:
        logger.info('der spieler kann nur %d zuege ziehen' % nr_of_moves)
    return {'nr_pieces': nr_of_moves, 'list_of_moves': list_of_moves,}

class OX:
    def __init__(self, bar, home_cnt):
        self.home = home_cnt
        if bar == 25:
            self.his_checkers = self.his_checkers_O
            self.possible_move = self.possible_move_O
            self.move_schema = self.move_schema_O
            self.leave = self.leave_O
            self.reach = self.reach_O
            self.greedy_moves = self.greedy_moves_O_old
            self.homeboard = (0,6)
            self.sum_home = lambda x,y: x + max(0, y)
        elif bar == 0:
            self.his_checkers = self.his_checkers_X
            self.possible_move = self.possible_move_X
            self.move_schema = self.move_schema_X
            self.leave = self.leave_X
            self.reach = self.reach_X
            self.greedy_moves = self.greedy_moves_X
            self.homeboard = (18,24)
            self.sum_home = lambda x,y: x + min(0, y)
        else:
            logger.error("Wrong use of the 'bar'-field (%d)!" % bar)

    def his_checkers_O(self, p):
        return p > 0

    def his_checkers_X(self, p):
        return p < 0

    def possible_move_O(self, e, d, position):
##        print 'e+1 d-1  %d,%d  pos[:] %s  # %d' % (e+1,6,position[e+1:6],reduce(self.sum_home, position[e+1:6], 0))
        return ((e >= d) and (position[e-d] > -2)) or \
            (self.bear_off(position) and (e == d-1)) or \
            (self.bear_off(position) and (e < d-1) and \
             not reduce(self.sum_home, position[e+1:6], 0))

    def possible_move_X(self, e, d, position):
        return ((e+d < 24) and (position[e+d] < 2)) or \
            (self.bear_off(position) and (e+d == 24)) or \
            (self.bear_off(position) and (e+d > 24) and \
             not reduce(self.sum_home, position[18:e-1], 0))

    def move_schema_O(self, e, d):
        t = e+1-d
        if t > 0:
            return '%d-%d' % (e+1, t)
        else:
            return '%d-off' % (e+1,)

    def move_schema_X(self, e, d):
        t = e+1+d
        if t < 25:
            return '%d-%d' % (e+1, t)
        else:
            return '%d-off' % (e+1,)

    def leave_O(self, position, p):
        position[p] -= 1

    def leave_X(self, position, p):
        position[p] += 1

    def reach_O(self, position, e, d):
        np = e - d
        if np >= 0:
            if position[np] == -1:
                position[np] = 1
            elif position[np] > -1:
                position[np] += 1
        else:
            self.home += 1
        return np

    def reach_X(self, position, e, d):
        np = e + d
        if np < 24:
            if position[np] == 1:
                position[np] = -1
            elif position[np] < 1:
                position[np] -= 1
        else:
            self.home += 1
        return np

    def bear_off(self, position,):
        a,b = self.homeboard
        nr_home = abs(reduce(self.sum_home, position[a:b], 0)) + self.home
        logger.debug('OX.bear_off: %d,%d   %d    %s   %d' % \
                (a, b, nr_home, position[a:b], self.home))
        return nr_home == 15

    def greedy_roll(self, dice, position):
        d = list(dice)
        d.sort(reverse=True)
        a,b = self.homeboard
        nr_home = abs(reduce(self.sum_home, position[a:b], 0))
        # TODO is it possible, nr_home is used only for debug?
        logger.debug('OX.greedy_roll: nr_home %d' % nr_home)
        d1,d2 = d
        self.is_pasch = False
        if d2 > d1:
            d = [d2, d1]
        elif d1 == d2:
            d = [d1,]*4
            self.is_pasch = True
        logger.log(TRACE, 'greedy roll: %s' % (d,))
        return d

    def greedy_moves_O_old(self, dice, position):
        """O is positiv and runs towards the 0."""
        moves = []
        dd = self.greedy_roll(dice, position)
        for d in dd:
            logger.debug('in greedy_moves_O   die %d' % d)
            if position[d-1] > 0:            # point is available
                moves.append('%d-0' % d)
                position[d-1] -= 1
            elif not reduce(self.sum_home, position[d:6], 0):
                r = d
                while r > 0:
                    r -= 1
                    logger.debug('checking  die %d on r %d' % (d,r))
                    if position[r] > 0:            # point is available
                        moves.append('%d-0' % (r+1,))
                        position[r] -= 1
                        break
            # TODO: fehlt der Fall mit "ich setze EINEN höheren" (bei >1
            #                                   Möglichkeiten darf ich nicht)
##        if (len(moves) < 2) and (len(dd) == 2) and \
##           (sum(dd) < 7) and (pos[sum(dd)-1] > 0):    # long move is available
##            moves = ['%d-%d' % (d1+d2,d1), '%d-0' % d1]   ????
                # TODO: denk an Contact!
                # TODO: gibt es beim long move waste????
        return moves
        
    def greedy_moves_O(self, dice, position):
        """O is positiv and runs towards the 0."""
        # Die Regeln fuer greedy:
        #                   (no forced moves!!)
        #   not pasch:
        #     bearoff 2
        #     - both dice can be born off by value (2==)
        #     (forced) - one dice can be born off by value,
        #     (forced)   scnd checker because pips are greater than highest field
        #     (forced) - both checker because pips are greater than highest field
        #     bearoff 1, one checker is exactly the sum of pips
        #     - long move where d1+d2 is a checker
        #
        dd = self.greedy_roll(dice, position)
        if self.pasch:
            return self.greedy_pasch_moves_O(dd[0])
        logger.debug('in greedy_moves_O  no pasch  dice %s' % dd)
        d1,d2 = dd
        if position[d1-1] > 0 and position[d2-1] > 0:   # points are available
            moves = ['%d-0' % d1, '%d-0' % d2]
            logger.debug('greedy_moves_O:  2==  %s' % moves)
            return moves
        if position[d1-1] < 1 and position[d2-1] < 1:   # points not available
            if position[d1+d2-1] > 0:                   # long move possible
                if not position[d2-1] < 0:
                    moves = ['%d-%d' % (d1+d2,d2), '%d-0' % d2]
                    logger.debug('greedy_moves_O:  0==  %s' % moves)
                elif not position[d1-1] < 0:
                    moves = ['%d-%d' % (d1+d2,d1), '%d-0' % d1]
                    logger.debug('greedy_moves_O:  0==  %s' % moves)
                else:
                    moves = []
                    logger.debug('greedy_moves_O:  0==  blocked')
                return moves

    def greedy_pasch_moves_O(self, pips):
        """O is positiv and runs towards the 0."""
        # Die Regeln fuer greedy:
        #                   (no forced moves!!)
        #   pasch:
        #     bearoff 4
        #     - 4 dice can be born off by value (4==)
        #     bearoff 3
        #     - 3 dice can be born off by value (2==), 1 checker is 2*pips
        #     bearoff 2
        #     - (0==), 2 checkers are 2*pips
        #
        logger.debug('in greedy_pasch_moves_O  pasch  dice %s' % pips)
        if position[pips-1] > 3:                                # 4==
            moves = ['%d-0' % pips,] * 4
            logger.debug('greedy_pasch_moves_O:  4==  %s' % moves)
            return moves
        if position[pips-1] > 1 and position[2*pips-1] > 0:     # 2== + 2*
            moves = ['%d-0' % pips,] * 2
            moves.append(['%d-%d' % (2*pips,pips), '%d-0' % pips])
            logger.debug('greedy_pasch_moves_O:  2== + 2* %s' % moves)
            return moves
        if position[2*pips-1] > 1:                              # 2* 2*
            moves = ['%d-%d' % (2*pips,pips), '%d-0' % pips] * 2
            logger.debug('greedy_pasch_moves_O:  2* 2* %s' % moves)
            return moves

    def greedy_moves_X(self, dice, position):
        """X is negativ and runs towards the 25."""
        moves = []
        dd = self.greedy_roll(dice, position)
        for d in dd:
            logger.debug('in greedy_moves_O   die %d' % d)
            if position[24-d] < 0:            # point is available
                moves.append('%d-off' % (25-d))
                position[24-d] += 1
            elif not reduce(self.sum_home, position[18:23-d], 0):
                r = 24 - d
                while r < 23:
                    r += 1
                    logger.debug('checking  die %d on r %d' % (d,r))
                    if position[r] < 0:            # point is available
                        moves.append('%d-off' % (r+1,))
                        position[r] += 1
                        break

#-------- TODO: siehe oben
##        elif (d1+d2 < 7) and (pos[24-(d1+d2)] > 0): # long move is available
##                                                    # TODO: denk an Contact!
##            moves = ['%d-%d' % (24-(d1+d2),24-d1), '%d-off' % (24-d1,)]
#--------------------------
        return moves
        
def check_roll(dice, position, bar_nr, direction, ox):
    """Checks for possible moves depending on 'dice'."""
    d1, d2 = dice
    logger.debug('enters check_roll with: dice %s position %s   bar_nr %d' \
                 ' direction %s' % (str(dice), position, bar_nr, direction))
    pasch = d1 == d2
    if pasch:
        nr_of_moves = 4
        my_dice = [d1,] * 4
    else:
        nr_of_moves = 2        
        my_dice = list(dice[:])
    list_of_moves = []
    nr_moved_pieces = 0
    forced_move = True
    checks_neccessary = True
    # ------------------------------------------- enter from the bar
    bar_moves = min(nr_of_moves, bar_nr)
    my_pos = position[:]
    bar_nr_moved_pieces = 0
    #print my_pos
    if bar_moves:
        ret = check_bar_moves(dice, my_pos, bar_moves, direction['bar'])
        my_dice = ret['my_dice']
        list_of_moves = ret['list_of_moves']
        forced_move = ret['forced_move']
        checks_neccessary = ret['checks_neccessary']
        bar_nr_moved_pieces = ret['nr_moved_pieces']
        nr_moved_pieces = bar_nr_moved_pieces
        nr_of_moves = ret['remaining_moves']
        print '..... ret', ret
    # ------------------------------------------- moves in the board
    #print my_pos
    if checks_neccessary:
        print '+++++++++++++', nr_of_moves
        board_o = my_pos[1:-1]
        board = board_o[:]
        ret = check_board_moves(tuple(my_dice), board, nr_of_moves, ox)
        print '1#### ret', ret
        # TODO  not (if len(dice) > 2 elif (len(dice) == 2) if dice[0] == dice[1])
        #       and if forced move oder vielleicht nicht alle gesetzt
        #       dann noch mal mit vertauschten dice durch check_board_moves
        nr_moved_pieces = ret['nr_moved_pieces']
        board_list_of_moves = ret['list_of_moves']
        print (not pasch),(nr_moved_pieces < nr_of_moves),(nr_of_moves > 1)
        if (not pasch) and (nr_moved_pieces < nr_of_moves) and (nr_of_moves > 1):
            board = board_o[:]
            my_dice.reverse()
            ret = check_board_moves(tuple(my_dice), board, nr_of_moves, ox)
            print '2#### ret', ret
            nr_moved_pieces = ret['nr_moved_pieces']
            board_list_of_moves.update(ret['list_of_moves'])
            print board_list_of_moves
        print (not pasch), (nr_moved_pieces == 1), (nr_of_moves == 2)
        if (not pasch) and (nr_moved_pieces == 1) and (nr_of_moves == 2):
            # now looking for a long move moving both dice with a single checker
            board = board_o[:]
            ret = check_single_moves(tuple(my_dice), board, ox)
            print '3#### ret', ret
            if ret['nr_moved_pieces'] == 2:
                board_list_of_moves = ret['list_of_moves']
        #print board
        for l in board_list_of_moves.values():
            list_of_moves += l
        nr_moved_pieces = min(len(list_of_moves), nr_of_moves+bar_nr_moved_pieces)
                # TODO: stimmt nicht, wenn man einen von der bar hat
        forced_move = nr_moved_pieces <= nr_of_moves
        if nr_moved_pieces == nr_of_moves:
            # looking for alternate moves
            
            # TODO: kann sein, dass das nicht immer stimmt, mit dem original
            #       board; siehe den Testfall mit den (6,5)
            #       wenn man die 5 von der 8 zieht, wo ist dann die 6?
##-------------------- dice (6, 5)
##utilities DEBUG enters check_roll with: dice (6, 5) position [0, 0, 0, 0, 1, 4, 1, 0, 3, 0, -4, -2, 0, 0, 0, 0, 2, 0, 0, -7, -5, -3, 0, 0, 0, 0]   bar_nr 0 direction {'home': 0, 'bar': 25}
##+++++++++++++ 2
##utilities TRACE check_board_moves in loop with die 6
##utilities DEBUG found: wurf 6   point 7,3  move 8-2   # 1
##utilities TRACE check_board_moves in loop with die 5
##utilities DEBUG found: wurf 5   point 5,1  move 6-1   # 0
##1#### ret {'nr_moved_pieces': 2, 'list_of_moves': {5: ['6-1'], 6: ['8-2']}}
##True False True
##True False True
##utilities TRACE check_board_moves in loop with die 6
##utilities TRACE check_board_moves in loop with die 5
##utilities DEBUG found: wurf 5   point 7,2  move 8-3   # 1
##4#### ret {'nr_moved_pieces': 1, 'list_of_moves': {5: ['8-3']}}
##utilities DEBUG check_roll results: nr_moved_pieces 2  list_of_moves ['6-1', '8-2']  forced False
##{'list_of_moves': ['6-1', '8-2'], 'forced_move': False, 'nr_pieces': 2}
            
            if pasch:
                alt_dice = (my_dice[0],)
            else:
                alt_dice = tuple(my_dice)
            ret = check_board_moves(alt_dice, board, nr_of_moves, ox,
                                    no_moves = list_of_moves)
            print '4#### ret', ret
            forced_move = ret['nr_moved_pieces'] < 1
    logger.debug('check_roll results: nr_moved_pieces %d  list_of_moves %s' \
                 '  forced %s' % (nr_moved_pieces, list_of_moves, forced_move))
    if forced_move:
        logger.info('der spieler kann nur %d zuege ziehen' % nr_moved_pieces)
    return {'nr_pieces': nr_moved_pieces, 'list_of_moves': list_of_moves,
            'forced_move': forced_move}

def check_board_moves(dice, position, nr_of_moves, ox, no_moves=[]):
    list_of_moves = dict(zip(range(1,7),([],[],[],[],[],[])))
    original_position = position[:]
    remaining_moves = nr_of_moves
    if len(dice) == 0:
        logger.error('what happens here: in check_board_moves with ' \
                     'unappropriate dice (%s)' % str(dice))
        return {'list_of_moves': [], 'nr_moved_pieces': 0,}
    for d in dice:
        logger.log(TRACE, 'check_board_moves in loop with die %d' % d)
        for e,p in enumerate(position):
            if ox.his_checkers(p):
                if ox.possible_move(e, d, position):
                    move = ox.move_schema(e, d)
                    if move in no_moves:
                        continue
                    list_of_moves[d].append(move)
                    ox.leave(position, e)
                    ox.reach(position, e, d)
                    remaining_moves -= 1
                    logger.debug('found: wurf %d   point %d,%d  move ' \
                                 '%s   # %d' \
                             % (d, e, p, move, remaining_moves))
                    break
        if remaining_moves < 0:
            break
    nr_moved_pieces = min(nr_of_moves, nr_of_moves - remaining_moves)
    for l in range(1,7):
        if not len(list_of_moves[l]):
            del list_of_moves[l]
    return {'list_of_moves': list_of_moves,
            'nr_moved_pieces': nr_moved_pieces,}
    
def check_single_moves(dice, position, ox):
    list_of_moves = dict(zip(range(1,7),([],[],[],[],[],[])))
    original_position = position[:]
    remaining_moves = 2
    if len(dice) != 2:
        logger.error('what happens here: in check_single_moves with ' \
                     'unappropriate dice (%s)' % str(dice))
        return {'list_of_moves': [], 'nr_moved_pieces': 0,}
    sum_dice = dice[0] + dice[1]
    logger.log(TRACE, 'check_single_moves before loop with dice %s' % str(dice))
    nr_moved_pieces = 0
    for e,p in enumerate(position):
        if ox.his_checkers(p):
            if ox.possible_move(e, sum_dice, position):
                d1, d2 = dice
                if ox.possible_move(e, d1, position):
                    move = ox.move_schema(e, d1)
                    list_of_moves[d1].append(move)
                    ox.leave(position, e)
                    e1 = ox.reach(position, e, d1)
                    remaining_moves -= 1
                    logger.debug('found: wurf %d   point %d,%d  move ' \
                                 '%s   # %d' \
                             % (d1, e, p, move, remaining_moves))
                    if ox.possible_move(e1, d2, position):
                        move = ox.move_schema(e1, d2)
                        list_of_moves[d2].append(move)
                        ox.leave(position, e1)
                        ox.reach(position, e1, d2)
                        remaining_moves -= 1
                        logger.debug('found: wurf %d   point %d  move ' \
                                     '%s   # %d' \
                                 % (d2, e1, move, remaining_moves))
                        nr_moved_pieces = 2
                break
        if remaining_moves < 0:
            break
    for l in range(1,7):
        if not len(list_of_moves[l]):
            del list_of_moves[l]
    return {'list_of_moves': list_of_moves,
            'nr_moved_pieces': nr_moved_pieces,}
    
def check_bar_moves(dice, position, nr_bar_moves, bar):
    list_of_moves = []
    d1, d2 = dice
    my_dice = list(dice[:])
    forced_move = False
    if d1 == d2:        # it's a double
        if bar == 25:
            p = bar - d1
            move_possible = position[p] > -2
        elif bar == 0:
            p = bar + d1
            move_possible = position[p] < 2
        else:
            logger.error("Falsche Belegung vom 'Bar'-Feld (%d)!" % bar)
        if move_possible:
            nr_moved_pieces = min(nr_bar_moves, 4)
            remaining_moves = 4 - nr_moved_pieces
            if bar == 25:
                position[p] = nr_moved_pieces
            elif bar == 0:
                position[p] = -nr_moved_pieces
            #print position
            forced_move = remaining_moves == 0
            checks_neccessary = remaining_moves > 0
            list_of_moves = ['bar-%d' % p,] * nr_moved_pieces
            my_dice = [d1,] * remaining_moves
        else:
            nr_moved_pieces = 0
            remaining_moves = 0
            forced_move = True 
            checks_neccessary = False
            my_dice = []
        logger.debug('pasch getested: bar %d  wurf %d   point %d   ' \
             'checker %d  (%s) (%s) (%d) # %d Forced move: %s  check %s' % \
             (bar, d1, p, position[p], list_of_moves, my_dice,
              remaining_moves, nr_moved_pieces, forced_move, checks_neccessary))
    else:               # normal roll
        remaining_moves = 2
        if bar == 25:
            for d in dice:
                p = bar - d
                if position[p] > -2:
                    list_of_moves.append('bar-%d' % p)
                    my_dice.remove(d)
                    remaining_moves -= 1
                    position[p] = 1
                logger.debug('normal testing: bar %d  wurf %d   point %d   ' \
                     'checker %d  (%s) (%s) (%d)  Forced move: %s' % \
                     (bar, d, p, position[p], list_of_moves, my_dice,
                      remaining_moves, forced_move))
        elif bar == 0:
            for d in dice:
                p = bar + d
                if position[p] < 2:
                    list_of_moves.append('bar-%d' % p)
                    my_dice.remove(d)
                    remaining_moves -= 1
                    position[p] = -1
                logger.debug('normal testing: bar %d  wurf %d   point %d   ' \
                     'checker %d  (%s) (%s) (%d)  Forced move: %s' % \
                     (bar, d, p, position[p], list_of_moves, my_dice,
                      remaining_moves, forced_move))
        else:
            logger.error("Falsche Belegung vom 'Bar'-Feld (%d)!" % bar)
        if (nr_bar_moves > 1) or (len(list_of_moves) == 0):
            forced_move = True 
            checks_neccessary = False
            remaining_moves = 0
            nr_moved_pieces = len(list_of_moves)
            my_dice = []
        else:
            forced_move = True 
            checks_neccessary = True
            remaining_moves = 1
            nr_moved_pieces = 1
            if my_dice == []:
                my_dice = list(dice[:])
                forced_move = False 
        logger.debug('normal getested: bar %d  wurf %d   point %d   ' \
             'checker %d  (%s) (%s) (%d) # %d Forced move: %s  check %s' % \
             (bar, d, p, position[p], list_of_moves, my_dice,
              remaining_moves, nr_moved_pieces, forced_move, checks_neccessary))        
    ret = {'my_dice': my_dice, 'list_of_moves': list_of_moves,
           'nr_moved_pieces': nr_moved_pieces, 'remaining_moves': remaining_moves,
           'forced_move': forced_move, 'checks_neccessary': checks_neccessary}
    return ret

##def bear_off(position, homeboard, home):
##    a,b = homeboard
##    nr_home = abs(sum(position[a:b])) + home # TODO abs(sum())
##    logger.debug('bear_off: %d,%d   %d    %s   %d' % \
##            (a, b, nr_home, position[a:b], home))
##    return nr_home == 15
    
def greedy(dice, position, ox):
    logger.debug('GREEDY: %s   %s' % (dice, position))
    moves = ox.greedy_moves(dice, position[1:-1])
    res = {'greedy_possible': len(moves) > 0, 'moves': moves}
    logger.debug('GREEDY: %s   ' % res)
    return res

##def greedy(dice, position,):
##    d1, d2 = dice           # TODO: mit waste auch noch machen
##    logger.debug('GREEDY: %d,%d   %s' % (d1, d2, position))
##    if d1 == d2:
##        return {'greedy_possible': False,}  # TODO: pasch geht nicht
##    pos = position
##    moves = []
##    if nick == 'p1':                # TODO: weg mit p1 und konsorten
##        if (pos[d1] > 0) and (pos[d2] > 0):
##            moves = ['%d-0' % d1, '%d-0' % d2]
##        elif (d1+d2 < 7) and (pos[d1+d2] > 0):
##            moves = ['%d-%d' % (d1+d2,d1), '%d-0' % d1]
##    elif nick == 'p2':              # TODO: weg mit p1 und konsorten
##        p1 = 25 - d1
##        p2 = 25 - d2
##        pp = 25 - d1 + d2
##        if (pos[p1] < 0) and (pos[p2] < 0):
##            moves = ['%d-25' % p1, '%d-25' % p2]
##        elif (d1+d2 < 7) and (pos[pp] > 0):
##            moves = ['%d-%d' % (pp,p1), '%d-25' % p1]
##    res = {'greedy_possible': len(moves) > 0, 'moves': moves}
##    logger.debug('GREEDY: %s   ' % res)
##    return res
##
if __name__ == '__main__':
    data = [{'dice':[(6,6), (5,5), (3,3), (6,5), (6,2), (2,1),],
             'pos': [0, 0,0,0,1,4,1, 0,3,0,-4,-2,0,
                        0,0,0,2,0,0, -7,-5,-3,0,0,0, 0],
             'dir': {'home':0, 'bar':25}, 'bar': [0,]},
            {'dice':[(5,1), (1,5)],
             'pos': [0, 2,0,-1,2,2,2, 0,2,0,0,0,0,
                        0,0,1,1,1,0, 1,0,0,-7,1,-7, 0],
             'dir': {'home':25, 'bar':0}, 'bar': [0,]},
            {'dice':[(6,3),],
             'pos': [0, 2,0,0,2,2,2, 0,2,0,0,0,0,
                        0,0,1,1,1,0, 1,0,0,-7,1,-7, 0],
             'dir': {'home':25, 'bar':0}, 'bar': [1,]},
            # TODO: sollte der hier nicht forced sein?
            {'dice':[(6,2),],
             'pos': [0, 0,0,3,3,0,0, -2,0,0,0,0,0,
                        2,0,0,0,0,0, 0,0,0,-7,-1,-7, 0],
             'dir': {'home':0, 'bar':25}, 'bar': [0,]},
            {'dice':[(4,3),],
             'pos': [0, 3,3,0,0,0,0, -2,0,0,0,2,0,
                        0,0,0,0,0,0, 0,0,0,-7,-1,-7, 0],
             'dir': {'home':0, 'bar':25}, 'bar': [0,]},
            # TODO: der hier muss forced sein! die 4-1 steht nicht als
            #       alternative zur verfügung
            {'dice':[(6,5),],
             'pos': [0, 3,3,2,0,0,0, -2,0,0,0,0,0,
                        0,0,0,0,0,0, 0,0,0,-7,-1,-7, 0],
             # TODO: auch hier muss forced sein! wenn man von der ursprünglichen
             #       pos ausgeht, sieht man das
             # TODO: das Konzept forced muss anders sein. die Aufgabe ist:
             #       finde im Original pos eine ausreichende Kombination mit einem
             #       anderen Endzustand
             'dir': {'home':0, 'bar':25}, 'bar': [0,], 'home': 7},
            {'dice':[(2,5),],
             'pos': [0, -2,6,2,2,0,2, -2,0,0,0,0,0,
                        0,0,0,0,0,0, 0,0,0,-7,-1,-7, 0],
             # TODO: auch hier muss forced sein! wenn man von der ursprünglichen
             #       pos ausgeht, sieht man das
             # TODO: das Konzept forced muss anders sein. die Aufgabe ist:
             #       finde im Original pos eine ausreichende Kombination mit einem
             #       anderen Endzustand
             'dir': {'home':0, 'bar':25}, 'bar': [0,], 'home': 3},
        ]
    for d in data:
        pos = d['pos']
        direction = d['dir']
        home_count = d.get('home', 0)
        ox = OX(direction['bar'], home_count)
        print 'Testing position', pos, '  ->', direction, '='*10
        for b in d['bar']:
            print '-'*40, 'bar', b
            for die in d['dice']:
                print '-'*20, 'dice', die
                print check_roll(die, pos, b, direction, ox)
                print
    print '#'*50
    ret = check_board_moves((5,1), data[1]['pos'][1:-1], 2, OX(0,0))
    print ret

