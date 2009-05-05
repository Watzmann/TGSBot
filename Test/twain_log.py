#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Zerlegt ein Twain-Log in übersichtliche Abschnitte"""

import sys
from optparse import OptionParser

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

class TwainCommand:
    
    def __init__(self):
        self.reset()
        self.direction = '-->'            
        self.source = ''
        self.target = ''
        return

    def info_parse(self, info):
##        print '++++', info
        info = ' - '.join(info)
        typ = None
        ret = ''
        if info.startswith(TW_TRACE):
            typ = 'trace'
            if self.line == 1:
                ret = info[:-1].split('--')[1].split(' to ')
                self.partners(ret)
                self.line = 2
            elif self.line == 2:
                self.tw_command = info.split('--')[1]
                self.line = 3
            else:
                print '!! wie komm ich hierher??',self.line
        elif info.startswith(TW_DSM):
            typ = 'dsm'
            ret = info.split('--')
            if len(ret) > 1 and ret[1].startswith(TW_DIAGEXIT):
                self.dsm = ret[1][len(TW_DIAGEXIT)+1:]
            else:
                self.dsm = info
            self.flag_complete = True
        else:
            self.dsm = info
            self.flag_complete = True
        return typ

    def partners(self, pair):
##        print 'Partners:',pair
        if self.source:
            if self.source in pair:
                if self.source == pair[1]:
                    self.turn_direction()
                    self.source, self.target = self.target, self.source
                pair.remove(self.source)
                if self.target != pair[0]:
                    print 'Wechsel im Target!', pair[0]
                    self.target = pair[0]
            else:
                print 'Source - Target unklar!',pair
                print 'Source:',self.source
        else:
            self.source = pair[0]
            self.target = pair[1]
            print 'Partner:', self.source,'-->',self.target
        return

    def turn_direction(self,):
        if self.direction == '-->':
            self.direction = '<--'
        else:
            self.direction = '-->'            

    def append(self, line):
        a = line.split(' - ')
##        for i in a:
##            print i
        if len(a) < 3 or a[1] != TW_MESSAGE:
            self.lines.append(line)
            self.flag_complete = True
        else:
            self.info_parse(a[2:])
        return
    
    def reveal(self):
##        print '#######################'
        for i in self.lines:
            print '##',i
        print self.direction, self.tw_command, self.dsm

    def reset(self):
        self.lines = []
        self.flag_complete = False
        self.dsm = ''
        self.tw_command = ''
        self.line = 1
        return

    def complete(self):
        return self.flag_complete

TW_32DLL = 'TWAIN_32.DLL'
TW_MESSAGE = 'MESSAGE'
TW_TRACE = 'CTWTRACE'
TW_DSM = 'DSM'
TW_DIAGEXIT = 'DsmEntryDiagExit'

def parseTwainLog(fname):
    f = file(fname)
    all_lines = [l.rstrip('\n') for l in f.readlines()]
    all_lines = [l for l in all_lines if l]
    command = TwainCommand()
    for l in all_lines:
        if l.startswith(TW_32DLL):
            line = command.append(l)
            if command.complete():
                command.reveal()
                command.reset()
        else:
            print l
    return
    
if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    fname = args[0]
    parseTwainLog(fname)
