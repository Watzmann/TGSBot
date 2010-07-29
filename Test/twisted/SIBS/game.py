#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von Game-related Routinen."""

class GamesList:        # TODO: als Singleton ausführen
    def __init__(self,):
        self.list_of_ongoing_games = {}

class Dice:
"""Dice provides a pair of dice."""
    def roll(self,):
        return (5,3)

class Board:
"""The Board holds all information about position etc.. Special methods check
for valid moves etc.."""
    pass

class GameControl:
"""GameControl controls the process of playing a single game of BG."""
    def __init__(self, player1, player2):
        pass

class Game:
    # players watchers
    def __init__(self, ML):
        self.id = '908239874918'    # funny id, is that neccessary?
        self.board = Board()
        print 'New game with id %s' % (self.id,)
        
def getGame(**kw):
    game = Game(kw['ML'])
    kw['list_of_games'].add(game)
    return game
