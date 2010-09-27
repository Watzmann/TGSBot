#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Entwicklungs-Skript für die Entwicklung von game.py.
Damit soll die mühsame Verbindung von 2 Spielern über telnet überflüssig
werden.
"""

import sys
from sibs_user import getUser, UsersList
from game import GamesList, set_verbose
from clip import Simple

lou = UsersList()
log = GamesList()

ML = 1

global VERBOSE
VERBOSE = False
BOARDSTYLE = '4'

def talk(msg):
    if VERBOSE:
        print msg
        
sequence = (
((2, 3), ['24-21','13-11']),
((4, 6), ['17-23','19-23']),
((1, 4), ['24-20','21-20']),
((5, 6), ['1-7','7-12']),       # 4
#---------------------------------------------------
((2, 4), ['8-4','6-4']),
((5, 3), ['17-22','19-22']),
((5, 3), ['8-3','6-3']),
((5, 3), ['12-17','12-15']),
((2, 1), ['8-6','6-5']),
((6, 6), ['12-18','12-18','12-18','1-7']),
((2, 2), ['11-9','9-7','7-5','13-11']),     # wirft    11
#---------------------------------------------------
((1, 2), ['bar-1','12-14']),
((4, 2), ['20-16','16-14']),                # wirft    13
((3, 6), ['','']),               # white kann nicht    14
((1, 6), ['','']),
((1, 4), ['','']),
((2, 5), ['','']),
((5, 5), ['','','','']),
((5, 4), ['','']),
((4, 3), ['','']),
)

class Spiel:
    def __init__(self, ml):
        self.match_length = ml
        self.p1 = 'frieda'
        self.p2 = 'dortdann'
        self.white = getUser(user=self.p1, password='andreas', lou=lou)
        if self.white == 1:
            self.white = lou.get_active(self.p1)
        self.white.set_protocol(Simple(self.p1))
        self.white.settings.boardstyle([BOARDSTYLE,])
##        self.white.save_settings()
        self.white.dice = 'sequence'
        self.black = getUser(user=self.p2, password='hallo', lou=lou)
        if self.black == 1:
            self.black = lou.get_active(self.p2)
        self.black.set_protocol(Simple(self.p2))
        self.black.settings.boardstyle([BOARDSTYLE,])
##        self.black.save_settings()
        self.white.invite(self.p2, ml)
        self.white.join(self.black, log)
##        print log.active_games
        self.turns = {'p1':'p2', 'p2':'p1'}
        self.players = {'p1':self.white, 'p2':self.black}
        self.turn = None

    def set_talkative(self,):
        self.white.protocol.quiet = False
        self.black.protocol.quiet = False

    def dice_and_moves(self, sequence, gid):
        dice = []
        moves = []
        for i in sequence:
            d,m = i
            dice.append(d)
            moves.append(m)
        talk(str(dice))
        talk(str(moves))
        game, player = log.get(gid)
        game.control.dice.set_sequence(dice)
        self.moves = iter(moves)

    def get_move(self,):
        return self.moves.next()

    def hand_over(self,):
        self.turn = self.turns.get(self.turn)
        return self.players[self.turn].running_game

    def whos_turn(self,):
        game,player = log.get(self.white.running_game)
        onturn = game.control.whos_turn()
        gid = onturn.running_game
        game,self.turn = log.get(gid)
        return gid

def get_game(player):
    games = log.active_games
    for k in games.keys():
        sig = games[k]
        if sig[1] == player:
            return (k,sig[1])
    return (None, None)

if __name__ == "__main__":
    VERBOSE = True
    set_verbose()
    spiel = Spiel(ML)
    spiel.set_talkative()
    games = log.active_games
    if len(games) > 2:
        print 'zuviele Einträge für diese simple Technik'
        sys.exit(1)

    id1,p1 = get_game('p1')
##    print 'white:', id1, p1
    id2,p2 = get_game('p2')
##    print 'black:', id2, p2

    print '-'*60
    print 'das Spiel beginnt'
    print '-'*60
    spiel.dice_and_moves(sequence, id1)
    turn = spiel.whos_turn()
    loops = 0
    wait_mode = False
    
    game, player = log.get(turn)
    game.control.score = {'p1':1, 'p2':2}
    game.control.board.set_score((game.control.white.name, 1), (game.control.black.name, 2), 1)
    print 'roll','-'*60
    game.roll(player)
    while turn:
        print 'loop %d:     player %s ist dran' % (loops, player)
        game, player = log.get(turn)
##        print 'loop %d:     player %s ist dran' % (loops, player)
##        print 'roll','-'*60
##        game.roll(player)
        print 'move','-'*60
        if game.control.pieces:
            game.move(spiel.get_move(), player)
        else:
            spiel.get_move()
        turn = spiel.hand_over()
        loops += 1
        if loops > 14:
            break
        if wait_mode:
            a = raw_input('enter drücken (q,c) ')
            if a.lower() == 'q':
                break
            if a.lower() == 'c':
                wait_mode = False
        print '-'*120
