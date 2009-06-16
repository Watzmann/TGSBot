#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""Stellt Statistiken zu Gegnern auf."""

import sys
import os
from optparse import OptionParser
from StringIO import StringIO
from listen import Liste
from el_listen import Line
##from mgnubg import DEBUG, OFF
from my_matches import JavaMatches, JavaMatch, get_matches, print_opponents
from my_matches import JavaRatings, JavaRating

class Opponents(JavaMatches):

    pass

class OpponentDescription(JavaMatch):

    def __init__(self, line, **kw):
        self.delimiter = ' '
        self.interpretation = ['opponent', 'nr_matches',
                               'total_rating','average_win',]
        self.key = 'total_rating'
        Line.__init__(self, line)

    def process(self,):
        il = self.interpreted_line
        il['nr_matches'] = int(il['nr_matches'])
        il['total_rating'] = float(il['total_rating'])
        il['average_win'] = float(il['average_win'])
        
    def __repr__(self,):
        il = self.interpreted_line
        return '%(total_rating)7.2f %(nr_matches)3d %(average_win)5.2f %(opponent)s' % il
    
def get_o_matches(matches, opponent):
    kw = {'opponent':opponent}
    _matches = JavaMatches(matches.liste, **kw)
    _matches.interpret(JavaMatch)
    _matches.list2hash()
    return _matches

def list_opponents(o_liste, **kw):
    opponents = Opponents(o_liste, **kw)
    opponents.interpret(OpponentDescription)
    opponents.process()
    opponents.list2hash()
    return opponents

def print_rating_gain_loss(matches, ratings, threshold=10):
    """Berechnet für jeden Opponent die gesamte Änderung im rating"""
    o_liste = StringIO()
    for k in matches.dliste.keys():
        d = matches.dliste[k]
        if len(d) > threshold:
            om = get_o_matches(matches,k)
            print >> o_liste, k,len(d),om.total_rating_delta(ratings), \
                                     om.average(om.pliste,'win')
    o_liste.seek(0)
    ol = list_opponents(o_liste.read().splitlines())
    o_liste.close()

    # opponents list (ol) could/should be returned here;
    # instead it is simply printed to stdout
    k = ol.dliste.keys()
    k.sort()                        # list of gains and losses
    for r in k:
        for o in ol.dliste[r]:      # account for multiple entries for any value
            print o

def statistics_rating(matches, ratings):
    sufficient_experience = 135     # ab da ist exp > 400
##    sufficient_experience = -20     # für Testzwecke
    for k in matches.pliste[sufficient_experience:]:
        delta = k.get_rating(ratings)[1]
        opp = k.get_opponents_rating(ratings)
        group = int(opp/50)*50
        ret = '%5.2f %7.2f' % (delta, opp)
        print '%-45s %s %6d' % (k.print_formatted(), ret.replace('.',','), group)

def usage(progname):
    usg = """usage: %prog [<opponent>]
  %prog """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-e", "--experience",
                  action="store_true", dest="experience", default=False,
                  help="print experience of matches")
    parser.add_option("-g", "--gain-loss",
                  action="store_true", dest="gain_loss", default=False,
                  help="print sorted list of gains and losses vs. opponents")
    parser.add_option("-s", "--statistics",
                  action="store_true", dest="statistics", default=False,
                  help="print statistics")
    default_threshold = 10
    parser.add_option("-t", "--threshold",
                  action="store", dest="threshold", type='int',
                  default=default_threshold,
                  help="use threshold [%d]; opponents with less matches are \
discarded." % default_threshold)
    parser.add_option("-r", "--root",
                  action="store", dest="file_root",
                  default='/opt/JavaFIBS2001/user/sorrytigger',
                  help="root path to matches and ratings")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()

    file_root = options.file_root
    if not os.path.isdir(file_root):
        file_root = '/opt/JavaFIBS2001/user/sorrytigger'
        if options.verbose:
            print 'default root wird verwendet:', file_root

    matches,ratings = get_matches(file_root,)
    matches.process()

    if options.verbose:
        print matches
        print ratings
        print_opponents(matches, threshold=options.threshold)

    if options.experience:
        print matches.experience()

    if options.gain_loss:
        print_rating_gain_loss(matches, ratings, threshold=options.threshold)

    if options.statistics:
        statistics_rating(matches, ratings)

