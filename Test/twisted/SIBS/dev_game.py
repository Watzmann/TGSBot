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

class Spiel:
    def __init__(self, ml):
        self.match_length = ml
        self.p1 = 'white'
        self.p2 = 'black'
        self.white = getUser(user=self.p1, password='##', lou=lou)
        self.white.set_protocol(Simple(self.p1))
        self.black = getUser(user=self.p2, password='##', lou=lou)
        self.black.set_protocol(Simple(self.p2))
        self.white.invite(self.p2, ml)
        self.white.join(self.black, log)
        print log.active_games
        self.turns = {'p1':'p2', 'p2':'p1'}
        self.players = {'p1':self.white, 'p2':self.black}
        self.turn = None

    def hand_over(self,):
        self.turn = self.turns.get(self.turn)
        return self.players[self.turn].running_game

    def first_turn(self, player):
        self.turn = player

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
    turn = id1
    spiel.first_turn(p1)
    loops = 0
    while turn:
        game, player = log.get(turn)
        print game, player
        game.roll(player)
        turn = spiel.hand_over()
        loops += 1
        if loops > 3:
            break
##    game.roll(player)
##
##    game, player = self.list_of_games.get(me.running_game)
##    game.move(line[1:], player)
