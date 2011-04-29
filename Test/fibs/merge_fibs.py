#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""Das Script führt 2 Dateien zusammen. Es funktioniert für Matches und Ratings."""

__TODO__ = """TODOs:
 - gibt's noch interessante Optionen?
 - Wenn el_listen.Line umgebaut wird (siehe Todo dort), dann hier Simple==Line
"""
import sys
import os
from listen import Liste
from el_listen import Line, Entry
from optparse import OptionParser

class Rating(Line):
    interpretation = ['ident',
                      'rating',
                      'zeit',
                      ]

    format = ('%%(%s)s ' *len(interpretation)).rstrip() % tuple(interpretation)

    def __repr__(self,):
        return self.format % self.interpreted_line

class Simple(Rating):
    interpretation = ['ident',
                      'rest',
                      ]

    format = ('%%(%s)s ' *len(interpretation)).rstrip() % tuple(interpretation)

class Matches(Rating):
    interpretation = ['nick',
                      'my_points',
                      'his_points',
                      'ML',
                      'ident',
                      'weissnicht',
                      ]

    format = ('%%(%s)s ' *len(interpretation)).rstrip() % tuple(interpretation)

class My_Liste(Liste):

    def __init__(self, liste, klasse, **kw):
        Liste.__init__(self, liste, **kw)
        self.klasse = klasse

    def single_out(self,):
        single = {}
        for i in self.interpret(self.klasse):
            ident = i.interpreted_line['ident']
            if single.has_key(ident):
                print 'ident doppelt vorhanden (%s)' % ident
            else:
                single[ident] = i
##            print 'single[ident]', single[ident]
        self.matches = single

    def merge(self, comparee):
        result = comparee.matches.copy()
        for i in self.matches:
            if not result.has_key(i):
                result[i] = self.matches[i]
        self.merged = result

    def flatten_merged(self, sort=False):
        sk = self.merged.keys()
        if sort:
            sk.sort()
        self.m_sorted = [self.merged[m] for m in sk]
        return self.m_sorted

    def diff(self, comparee):
##        result = {'hier':[], 'dort':[], }
        result = []
        for i in self.matches:
            if not comparee.matches.has_key(i):
                result.append('< %s' %i)
        for i in comparee.matches:
            if not self.matches.has_key(i):
                result.append('> %s' %i)
        return result

def usage(progname):
    keys = ("'%s'|" *len(available_types))[:-1] % tuple(available_types)
    usg = u"""usage: %s {%s} <datei-1> <datei-2> 
  %s
  matches      Die zu vergleichenden Dateien sind Matches.
  rating       Die zu vergleichenden Dateien sind Ratings.
  simple       Die zu vergleichenden Dateien sind friends oder villains.
  <datei-1>    Zu vergleichende Datei.
  <datei-2>    Zu vergleichende Datei.

  Das Ergebnis wird nach stdout ausgegeben. Es ist die neue funktionsfähige
  Datei.""" % (progname,keys,__doc__,)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-d", "--diff",
                  action="store_true", dest="difference", default=False,
                  help="print the difference between the files")
    return parser,usg

def merge_lists(match, args):
    a = match[args[1]]
    a.merge(match[args[2]])                        # 2 Listen mergen
    return Liste(a.flatten_merged(sort=list_sort)) # 'merged' wird neue Liste

def compare_lists(match, args):
    a = match[args[1]]
    diffs = a.diff(match[args[2]])                 # 2 Listen vergleichen
    return Liste(diffs)                            # diff wird neue Liste

def cmdline_error(msg):
    print usg.encode('utf-8')
    print
    print msg
    sys.exit(1)
        
available_types = {'matches':(Matches, True),
                   'rating':(Rating, True),
                   'simple':(Simple, False)}

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print __TODO__
        print options,args
    if len(args) < 3:
        cmdline_error("!! Es müssen ein Schlüsselwort und 2 Dateien angegeben werden.")
    if not args[0] in available_types.keys():
        cmdline_error("!! key muss einer von %s sein." % available_types.keys())

    match = {}
    for a in args[1:3]:                               # 2 Listen laden
        klasse,list_sort = available_types[args[0].lower()]
        l = My_Liste(a,klasse)
        l.single_out()
        if options.verbose:
            print 'Listenlänge', a, len(l.matches)
        match[a] = l
    if options.difference:
        result = compare_lists(match, args)           # Differenz
    else:
        result = merge_lists(match, args)             # Merge
    result.print_lines()                              # neue Liste ausgeben
