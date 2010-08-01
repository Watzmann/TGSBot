#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Entwicklungs-Skript für die Entwicklung von game.py.
Damit soll die mühsame Verbindung von 2 Spielern über telnet überflüssig
werden.
"""

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

if __name__ == "__main__":
    spiel = Spiel(ML)
