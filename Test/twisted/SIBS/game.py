#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von Game-related Routinen."""

class GamesList:        # TODO: als Singleton ausführen
                        # TODO: mit UsersList in eine Klasse überführen
    def __init__(self,):
        self.active_games = {}

    def add(self, game):
        for i in game.ids:
            self.active_games[i] = (game, game.player[i])

    def get(self, gid, default=None):
        print 'returning gid %s' % gid
        return self.active_games.get(gid, default)

class Dice:                # TODO: als Singleton ausführen
    """Dice provides a pair of dice."""
    def roll(self,):
        return (5,3)

    def single_roll(self,):
        return 2

class Board:
    """The Board holds all information about position etc.. Special methods check
for valid moves etc.."""

    def __init__(self,):
        self.position = [2,5,3,8]
        
    def move(self, player, move):
        pass
    
    def check(self, player, move):
        msg = "can't move to Berlin"
        return msg

    def __raw__(self,):
        """board:You:someplayer:3:0:0:
         0:-2:0:0:0:0:5:0:3:0:0:0:-5:5:0:0:0:-3:0:-5:0:0:0:0:2:0:
         1:6:2:0:0:1:
         1:1:0:1:-1:0:25:0:0:0:0:2:0:0:0"""
        return "board:You:someplayer:3:0:0:0:-2:0:0:0:0:5:0:3:0:0:0:-5:5:0:0:0:-3:0:-5:0:0:0:0:2:0:1:6:2:0:0:1:1:1:0:1:-1:0:25:0:0:0:0:2:0:0:0"

class GameControl:
    """GameControl controls the process of playing a single game of BG."""
    def __init__(self, game):
        self.game = game
        self.white = game.player1   # TODO: sehr wichtig, diese Zuordnungen
        self.black = game.player2   #       zu überarbeiten
        self.dice = Dice()
        self.turn = 0       # TODO oder was im board-status richtig ist

    def start(self,):
        a = b = 0
        while a == b:
            a,b = self.dice.roll()
            self.game.starting_rolls(a,b)
        self.turn = {True:1, False:2}[a>b]

    def whos_turn(self,):
        return {1:self.white, 2:self.black, 0:None}[self.turn]

    def roll(self, player):
        # TODO: kontrollieren, ob der dran ist
        d = self.dice.roll()    # TODO    turn und dice eintragen
        return d

    def hand_over(self,):
        self.turn = 3 - self.turn

class Game:
    # players watchers
    def __init__(self, p1, p2, ML, board=None):
        self.id = '908239874918'    # funny id, is that neccessary?
                                    # TODO: YES - die muss unique sein!!!!!
        if not board is None:
            self.board = board
        else:
            self.board = Board()
        self.player1 = p1
        self.player2 = p2
        self.ids = (self.id + '_p1', self.id + '_p2')
        self.player = dict(zip(self.ids,('p1','p2')))
        self.who = dict(zip(('p1','p2'),(p1,p2)))
        self.ML = ML
        self.opp = {p1.name:p2, p2.name:p1}
        print 'New game with id %s, %s vs %s' % (self.id, p1.name, p2.name)

    def start(self,):
        msg = 'Starting a new game with %s'
        self.player1.chat(msg % self.player2.name)
        self.player2.chat(msg % self.player1.name)
        self.control = GameControl(self)
        self.control.start()
        self.whos_turn()

    def starting_rolls(self, p1, p2):
        msg = 'You rolled %s, %s rolled %s'
        self.player1.chat(msg % (p1, self.player2.name, p2))
        self.player2.chat(msg % (p2, self.player1.name, p1))

    def whos_turn(self,):
        msg = 'It is your turn to move'
        self.control.whos_turn().chat(msg)
##        self.player2.chat(msg % (p2, self.player1.name, p1))
        
    def opponent(self, player):
        return self.opp[player.name]

def getGame(**kw):
    game = Game(kw['player1'], kw['player2'], kw['ML'], )
    kw['list_of_games'].add(game)
    game.start()
    return game.ids
