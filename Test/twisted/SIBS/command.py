#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Erste Implementierung des SIBS-Protokolls.
Siehe fibs_interface.html.
"""
 
class Command():
    def __init__(self,):
        self.commands = {
        'show': self.c_show,
        }
        
    def c_show(self, line):
        return 'shown'

    def c_unknown(self, line):
        return 'unknown command %s' % line[0]

    def command(self, cmd):
        return self.commands.get(cmd, self.c_unknown)
