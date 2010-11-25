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

def check_roll(dice, position, bar_nr, direction):
    """Checks for possible moves depending on 'dice'."""
    d1, d2 = dice
    if d1 == d2:
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
    #print my_pos
    if bar_moves:
        ret = check_bar_moves(dice, my_pos, bar_moves, direction['bar'])
        my_dice = ret['my_dice']
        list_of_moves = ret['list_of_moves']
        forced_move = ret['forced_move']
        checks_neccessary = ret['checks_neccessary']
        nr_moved_pieces = ret['nr_moved_pieces']
        nr_of_moves = ret['remaining_moves']
        print '..... ret', ret
    # ------------------------------------------- moves in the board
    #print my_pos
    if checks_neccessary:
        print '+++++++++++++', nr_of_moves
        ret = check_board_moves(tuple(my_dice), my_pos[1:-1], nr_of_moves,
                                                        direction['bar'])
        print '##### ret', ret
        # TODO  not (if len(dice) > 2 elif (len(dice) == 2) if dice[0] == dice[1])
        #       and if forced move oder vielleicht nicht alle gesetzt
        #       dann noch mal mit vertauschten dice durch check_board_moves
        nr_moved_pieces += ret['nr_moved_pieces']
        list_of_moves += ret['list_of_moves']
        forced_move = forced_move and ret['forced_move']
    if nr_moved_pieces < nr_of_moves:
        nr_of_moves = len(list_of_moves)
        logger.info('der spieler kann nur %d zuege ziehen' % nr_of_moves)
    return {'nr_pieces': nr_moved_pieces, 'list_of_moves': list_of_moves,
            'forced_move': forced_move}

def check_board_moves(dice, position, nr_of_moves, bar):
    list_of_moves = []
    forced_move = True
    remaining_moves = nr_of_moves
    if len(dice) > 1:
        pasch = dice[0] == dice[1]
    for d in dice:
        found = 0
        logger.log(TRACE, 'check_board_moves in loop with die %d' % d)
        if bar == 25:
            for e,p in enumerate(position):
                if p > 0:
                    if (e >= d) and (position[e-d] > -2):
                        list_of_moves.append('%d-%d' % (e+1,e+1-d))
##                        if not found:
                        position[e] -= 1
                        position[e-d] += 1
                        remaining_moves -= 1
                        found += 1
                        logger.debug('found: wurf %d   point %d,%d  move %s   ' \
                                     '(%s) Forced move: %s' % \
                                     (d, e, p, list_of_moves[-1],
                                      list_of_moves, forced_move))
                if (found > 1) or ((found == 1) and forced_move):
                    forced_move = False
                    break
        elif bar == 0:
            for e,p in enumerate(position):
                if p < 0:
                    if (e+d < 24) and (position[e+d] < 2):
                        list_of_moves.append('%d-%d' % (e+1,e+1+d))
##                        if not found:
                        position[e] -= 1
                        position[e+d] += 1
                        remaining_moves -= 1
                        found += 1
                        logger.debug('found: wurf %d   point %d,%d  move %s   ' \
                                     '(%s) Forced move: %s' % \
                                     (d, e, p, list_of_moves[-1],
                                      list_of_moves, forced_move))
                if (found > 1) or ((found == 1) and forced_move):
                    forced_move = False
                    break
        else:
            logger.error("Falsche Belegung vom 'Bar'-Feld (%d)!" % bar)
    nr_moved_pieces = min(nr_of_moves, nr_of_moves - remaining_moves)
    if found == 0:
        forced_move = True
    return {'list_of_moves': list_of_moves,
            'nr_moved_pieces': nr_moved_pieces,
            'forced_move': forced_move,}
    
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

if __name__ == '__main__':
    data = [{'dice':[(6,6), (5,5), (3,3), (6,5), (6,2), (2,1),],  #(5,5), (3,3), ],
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
        ]
    for d in data:
        pos = d['pos']
        direction = d['dir']
        print 'Testing position', pos, '  ->', direction, '='*10
        for b in d['bar']:
            print '-'*40, 'bar', b
            for die in d['dice']:
                print '-'*20, 'dice', die
                print check_roll(die, pos, b, direction)
                print
        
