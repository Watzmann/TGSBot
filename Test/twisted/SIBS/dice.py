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

def getDice(dice_typ='simple'):
    dice = {'simple':Dice, 'random':RandomDice,}
    return dice[dice_typ]()
