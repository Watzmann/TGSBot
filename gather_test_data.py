#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Gather test data for bots from bot logs."""

import sys
import os, os.path
import re

modules = '/var/develop/Python/modules'
if modules not in sys.path:
	sys.path.insert(0, modules)
import listen, el_listen

class Line(el_listen.Line):
    interpretation = ['date',
                      'time',
                      'source',
                      'load',
                      ]
    MOVE = re.compile('[0123456789]')

    def process(self,):
        self.parse_load = {'invite': self._invite,
                           'PLAY': self._play,
                           'TURN': self._turn,
                           'deleting': self._roll,
                           'got': self._move,
                           'double': self._double,
                           }
        self.data = {}
        line = self.interpreted_line['load']
        if line.startswith('>> '):
            line = line[3:]
        self.data['line'] = line
        l = line.split()
        self.data['action'] = self.parse_load[l[0]](l)

    def _invite(self, line):
        return {'type': 'invite', 'ML': line[2]}

    def _play(self, line):
        return {'type': 'play', 'player': line[7]}

    def _turn(self, line):
        return {'type': 'turn', 'action': ' '.join(line[3:])}

    def _roll(self, line):
        if line[4] == 'rolled':
            dice = (int(line[5][0]), int(line[8][0]))
        else:
            dice = (int(line[5][0]), int(line[7][0]))
        return {'type': line[4], 'dice': dice}

    def _move(self, line):
        move = ' '.join([l.strip('(), ') for l in line[2:]])
        return {'type': 'move', 'move': move}

    def _double(self, line):
        return {'type': 'double', }

NRLINES = 10

if __name__ == '__main__':
    if len(sys.argv) < 2:
         arg = '-'
    else:
         arg = sys.argv[1]
    print 'reading', arg
    l = listen.Liste(arg)
    l.print_lines(0,NRLINES)
    kw = {"discard_contiguos_blanks": True}
    p = l.interpret(Line, **kw)
    for i in p[:NRLINES]:
        print '##', i.interpreted_line['load']
    l.process()
    for i in l.pliste:
        for k in i.data:
            if k in ('line',):
                continue
            print i.data[k]
