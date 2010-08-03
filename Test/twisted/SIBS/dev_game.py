#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Entwicklungs-Skript für die Entwicklung von game.py.
Damit soll die mühsame Verbindung von 2 Spielern über telnet überflüssig
werden.
"""

import sys
from sibs_user import getUser, UsersList
from game import GamesList
from clip import Simple

lou = UsersList()
log = GamesList()

ML = 1

sequence = (
((2, 3), ['24-21','13-11']),
((4, 6), ['17-23','19-23']),
((1, 4), ['24-20','21-20']),
((5, 6), ['1-7','7-12']),
((2, 4), ['','']),
((5, 3), ['','']),
((5, 3), ['','']),
((5, 3), ['','']),
((2, 1), ['','']),
((6, 6), ['','']),
((2, 2), ['','','','']),
((1, 2), ['','']),
((4, 2), ['','']),
((3, 6), ['','']),
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
        self.p1 = 'white'
        self.p2 = 'black'
        self.white = getUser(user=self.p1, password='##', lou=lou)
        self.white.set_protocol(Simple(self.p1))
        self.white.dice = 'sequence'
        self.black = getUser(user=self.p2, password='##', lou=lou)
        self.black.set_protocol(Simple(self.p2))
        self.white.invite(self.p2, ml)
        self.white.join(self.black, log)
        print log.active_games
        self.turns = {'p1':'p2', 'p2':'p1'}
        self.players = {'p1':self.white, 'p2':self.black}
        self.turn = None

    def dice_and_moves(self, sequence, gid):
        dice = []
        moves = []
        for i in sequence:
            d,m = i
            dice.append(d)
            moves.append(m)
        print dice
        print moves
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
    spiel = Spiel(ML)
    games = log.active_games
    if len(games) > 2:
        print 'zuviele Einträge für diese simple Technik'
        sys.exit(1)

    id1,p1 = get_game('p1')
    print 'white:', id1, p1
    id2,p2 = get_game('p2')
    print 'black:', id2, p2

    print '-'*60
    print 'das Spiel beginnt'
    print '-'*60
    spiel.dice_and_moves(sequence, id1)
    turn = spiel.whos_turn()
    loops = 0
    while turn:
        game, player = log.get(turn)
        print game, player
        game.roll(player)
        game.move(spiel.get_move(), player)
        turn = spiel.hand_over()
        loops += 1
        if loops > 3:
            break
