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

def check_roll(dice, position, bar_nr, direction):
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
