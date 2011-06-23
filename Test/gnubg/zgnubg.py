#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""analysiert BG-Matches mit Aufruf von 'gnubg -tq'"""

import os
from subprocess import Popen, PIPE

OFF = True
_DEBUG = True
def DEBUG(msg, ON=True):
    if _DEBUG and ON:
        print '##', msg

class Gnubg:

##    load_cmd = """load match %s
##show score\n"""
    load_cmd = ">\n"
    analyse_cmd = """analyse match\n"""
    statistics_cmd = {'match':(61,"""show statistics match\n"""),
                      'game':(57,"""show statistics game\n"""),
                      }
    reset_cmd = """previous game %s\n"""
    next_cmd = """next game %s\n"""
    score_interpretation = ('nr_of_games','opponent','opp_score',
                            'player','pl_score','matchlength','xxx','crawford',)

    def __init__(self,):
        OFF = False
        arg = 'gnubg -tq -p /home/hausmann/tmp/gnubg/zgnubg.py'
        DEBUG('starting gnubg', OFF)
        self.gnubg = Popen(arg,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
        DEBUG('setting Pipes', OFF)
        self.stdin = self.gnubg.stdin
        self.stdout = self.gnubg.stdout
        self.stderr = self.gnubg.stderr
        DEBUG('reading', OFF)
        self.start_output = self.start()
        DEBUG("gnubg running with '%s'" % (arg,), OFF)
        for i in self.start_output:
            print i,
        self.alive = True
        self.loaded_match = False
        self.score = {}
##        err = self.err()
##        print 'error?', err

    def write(self, msg):
        self.stdin.write(msg)
 
    def load(self, match):
        OFF = True
        DEBUG('loading %s' % match, OFF)
        self.warnings = []
        cmd = self.load_cmd # % match
        DEBUG('command: %s' % cmd, OFF)
        self.write(cmd)
        #ret = self.read(17)
        self.loaded_match = True
        DEBUG('done loading', OFF)
        DEBUG('info: %s' % ret[-1], OFF)
        self.score = self.scores(ret[-1])
        DEBUG('score: %s' % self.score, OFF)
        self.analysed_match = False
        self.reset()
        return ret

    def read(self,n=0,stop="Keine Partie"):
        OFF = False
        ret = []
        last_line_empty = False
        last_lines = 0
        i = n
        while i > 0:
            DEBUG('%d reading' % i, OFF)
            i -= 1
            r = self.stdout.readline()
            while r.startswith('WARNUNG: ') or \
                  r.startswith('Nicht erkannter Zug '):
                w = r.rstrip('\n')
                self.warnings.append(w)
                DEBUG('!! %s' % w, OFF)
                r = self.stdout.readline()
            if r.startswith('Bist Du sicher'):
                self.write('y\n')
                self.write('show score\n')
                self.stdout.readline()
                self.stdout.readline()
                self.stdout.readline()
                r = self.stdout.readline()
            if r.startswith(' +13-14-15-16-17-18'):
                if r.rstrip('\n').endswith('You'):
                    i = 2
            ret.append(r)
            DEBUG('## (%d) %s##' % (last_lines,r), OFF)
            if len(r) == 1:
                if last_line_empty:
                    if last_lines == 2:
                        self.warnings.append('SELBSTSTÄNDIG LESEVORGANG ABGEBROCHEN')
                        return ret
                    last_lines += 1
                else:
                    last_line_empty = True
                    last_lines = 1
            else:
                last_line_empty = False
                last_lines = 0
        return ret

    def start(self, stop="um Details"):
        OFF = False
        ret = []
        while True:
            r = self.stdout.readline()
            ret.append(r)
            DEBUG('##%s##' % (r,), OFF)
            if r.startswith(stop):
                break
        return ret

print __name__
if __name__ == '__main__':
    root = '/home/hausmann/tmp/gnubg'
    my_match = 'gnuBG-Andreas_7p_2010-02-21_1715.sgf'
    match = os.path.join(root,my_match)

    print match
    gnu = Gnubg()
    gnu.load(match)
    
