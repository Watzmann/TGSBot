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

if __name__ == "__main__":
    p1 = 'white'
    p2 = 'black'
    white = getUser(user=p1, password='##', lou=lou)
    white.set_protocol(Simple(p1))
    black = getUser(user=p2, password='##', lou=lou)
    black.set_protocol(Simple(p2))
    white.invite(p2, ML)
    white.join(black, log)
    print log.active_games
