#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von verschiedenen Dice."""

from random import randint

class Dice:                # TODO: als Singleton ausführen
    """Dice provides a pair of dice."""
    def roll(self,):
        return self.double_roll()

    def single_roll(self,):
        return (2,)

    def double_roll(self,):
        return (5,3)

class RandomDice(Dice):
    def single_roll(self,):
        return (randint(1,6),)

    def double_roll(self,):
        return (randint(1,6),randint(1,6))

class SequenceDice(Dice):
    def single_roll(self,):
        return (self.double_roll()[0],)

    def double_roll(self,):
        try:
            d = self.sequence.next()
        except StopIteration:
            self.sequence = iter(self.given)
            d = self.sequence.next()
        except AttributeError:
            self.sequence = iter(((4,2),(1,6),(1,1),))
            d = self.sequence.next()
        return d
    
    def set_sequence(self, seq):
        self.given = seq
        self.sequence = iter(seq)

def getDice(dice_typ='simple'):
    dice = {'simple':Dice,
            'random':RandomDice,
            'sequence':SequenceDice}
    return dice[dice_typ]()
