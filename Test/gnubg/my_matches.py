#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""Stellt Einträge in 'matches'-Datei zur Verfügung."""

import sys
import os
import time
from math import sqrt, log10
from optparse import OptionParser
from listen import Liste
from el_listen import Line
from mgnubg import DEBUG, OFF

TIMEFMT = '%d.%m.%y %H:%M'

## TODOs:
##    1) Option --statistics  gibt einige Statistiken aus, wie z.B.
##        - Zahl von Opponenten
##        - Häufigste Gegenspieler
##    2) Parameter <opponent> gibt die Statistik gegen den Opponenten aus
##       und die "-l" Zeilen gegen ihn (wenn -l gegeben)
##    x) Bei -l kann man neben den Spielen die Änderung im Rating ausgeben

class JavaMatches(Liste):

    def __init__(self, liste, **kw):
        Liste.__init__(self, liste, **kw)
        DEBUG('JavaMatches.__init__()++++++++++', OFF)
        DEBUG('kw: %s' % kw, OFF)
        DEBUG('%s' % liste, OFF)

    def my_filter(self, **kw):
        """
        Applies filter to list; launched in constructor;
        optional arguments can be supplied in dictionary self.filter_args;
        to be overridden by subclass;
        """
        liste = self._raw_liste
        opponent = kw.get('opponent')
        if not opponent is None:
            liste = [e for e in liste if e.split()[0] == opponent]
        return liste

    def list2hash(self,):
        DEBUG('JavaMatches.list2hash()++++++++++',OFF)
        self.dliste = {}
        for i in self.pliste:
            pk = i.primary_key()
            if self.dliste.has_key(pk):
                self.dliste[pk].append(i)
            else:
                self.dliste[pk] = [i]
        DEBUG('pliste: %s' % self.pliste,OFF)
        DEBUG('dliste: %s' % self.dliste,OFF)
        return self.dliste

    def match_candidates(self, name, time=None, delta_time=60):
        """Gibt eine Liste von Kandidaten zurück, die für 'name' und 'time'
            in Frage kommen.
            Wenn 'time' nicht bekannt ist, ist natürlich keine Einschränkung
            möglich.
            Mit 'delta_time' (in Sek.) kann die Genauigkeit beeinflusst werden.
        """
        DEBUG('in match_candidates() with name %s  time %s  delta_time=%s' % \
                  (name, time, delta_time), OFF)
        ret = []
        delta = float(delta_time)
        if self.dliste.has_key(name):
            liste = self.dliste[name]
            ret = liste[:]
            DEBUG('in match_candidates()::  ret: %s' % ret, OFF)
            if not time is None:
                for l in liste:
##                    print 'time', l.time, time, (float(l.time)/1000. - time)
                    if abs(float(l.time)/1000. - time) > delta:
                        ret.remove(l)
        return ret

    def get_match(self, name, time, score):
        ret = None
        liste = self.match_candidates(name, time)
        if time is None:
            DEBUG('time is None and len liste is %d\nfor %s with score%s' \
                  % (len(liste),name,score))
            for l in liste:
                print l
        if len(liste) == 1 and time is None:
            ret = liste[0]
        else:
            for l in liste:
                if (l.me_score,l.op_score) == score:
                    ret = l
                    break
                else:
                    print name, l.time, time
                    DEBUG('%s %f %s %s %s %s' % \
                          (name, (float(l.time)/1000. - time),
                            'score  SOLL', score, 
                            'IST', (l.me_score,l.op_score)))
        return ret

    win = lambda p: int(p.win)      # TODO: wo wird das gebraucht?
    
    def average(self, liste, value):
        h = [int(i.interpreted_line[value]) for i in liste]
        try:
            ret = sum(h)/float(len(h))
        except ZeroDivisionError:
            ret = 0.
        return ret
    
    def get_average_delta(self, ranges):
        ret = []
        act = self.average(self.pliste,'win')
        for r in ranges[:-1]:
            this = self.average(self.pliste[:-r],'win')
##            print this,act,(act-this),(act-this)/r,r
	    ret.append('%6.2f./...' % ((act-this)/r*10000.,))
        ret.append('')
        return ret

    def get_averages(self, up_to_index=0):
        spans = (3,5,10,20,50,100)
        rspans = list(spans)
        spans = spans + (len(self.liste),)
        rspans.reverse()
        ret = []
        if up_to_index:
            aliste = self.pliste[:min(up_to_index,len(self.pliste))]
        else:
            aliste = self.pliste
        for i in rspans:
            if len(aliste) < i:
                continue
            else:
                l = aliste[-i:]
                ret.append(self.average(l,'win'))
        ret.reverse()
        spans = spans[:len(ret)] + (spans[-1],)
##        print spans,len(spans),len(ret),'###############'
        ret.append(self.average(aliste,'win'))
        delta = self.get_average_delta(spans)
        return zip(spans,ret,delta)

    def gliding_averages(self,):
        out = ''
        av = matches.get_averages()
        titles = [a for a,b,c in av]
        out = 'Datum;;'
        for t in titles:
            out += '%d;' % t
        out += '\n'
        for i in range(25,len(self.pliste)):
            timestamp = self.pliste[i].interpreted_line['time']
            timestr = self.pliste[i].interpreted_line['str_time']
            times = timestr[:8]+';'+str(timestamp)+';'
            av = matches.get_averages(up_to_index=i+1)
            values = [b for a,b,c in av]
            for t in values:
                if t == '':
                    out += ';'
                else:
                    out += '%6.4f;' % (t,)
            yield times + out[:-1].replace('.',',')
            out = ''

    def total_rating_delta(self, ratings):
        rsum = 0
        for k in self.pliste:
            r,d = k.get_rating(ratings)
            rsum += d
        return rsum

    def experience(self):
        rsum = 0
        P = None
        for p in self.pliste:
            rsum += int(self.pliste[0].interpreted_line['ml'])
            if P is None and rsum > 400:
                P = p
        return rsum, P
        #return reduce(lambda x, y: x+int(y.interpreted_line['ml']), self.pliste)

    def get_time_slices(self,):
        print self
        return
    
    def __repr__(self,):
        return "%d entries in %s" %(len(self),self.full_path)

class JavaMatch(Line):

    str_win = {'1':'+++', '0':'---'}

    def __init__(self, line, **kw):
        self.delimiter = ' '
        self.interpretation = ['opponent', 'me_score','op_score','ml','time','win']
        self.key = 'opponent'
        Line.__init__(self, line)

    def process(self,):
        il = self.interpreted_line
        il['str_time'] = time.strftime(TIMEFMT,time.localtime(float(il['time'])/1000.))
        il['str_win'] = self.str_win[il['win']]
        
    def get_rating(self, ratings):
        """Gibt das Rating nach dem Match zurück sowie das Delta zu vorher."""
        rating,delta = ratings.match_rating(int(self.time),delta_time=2000,
                                                                    delta=True)
        if not rating is None:
            ret = rating.rating, delta
        else:
            ret = None, delta
        return ret

    def get_opponents_rating(self, ratings):
        """Gibt das Rating des Gegners vor dem Match zurück."""
        return ratings.opponents_rating(int(self.time), self)

    def print_formatted(self,):
        self.process()
        il = self.interpreted_line
        return '%(str_time)s ML %(ml)s %(str_win)s %(me_score)s:%(op_score)s %(opponent)s ' % il

class JavaRatings(Liste):

    def __init__(self, liste, **kw):
        Liste.__init__(self, liste)
        DEBUG('JavaRatings.__init__()++++++++++',OFF)
        DEBUG('kw: %s' % kw,OFF)
        DEBUG('%s' % liste,OFF)

    def match_rating(self, time_seconds, delta_time=1000, delta=False):
        """Gibt für den angegebenen Zeitpunkt das Rating (nach dem Match) zuück.
            Ist 'delta'==True, so wird ein Tuple (rating, delta) zurückgegeben,
            wobei delta den Unterschied zu 'vor dem Match' angibt.
        """
        DEBUG('in match_rating() with  time %s  delta_time=%s   delta=%s' % \
                  (time_seconds, delta_time, delta), OFF)
        before = 0.
        ret = None
        delta_rating = 0.
        for t in self.pliste:
            if abs(long(t.time) - time_seconds) < delta_time:
                ret = t
                break
            before = t
        if before:
            delta_rating = float(t.rating) - float(before.rating)
        if delta:
            ret = (ret, delta_rating)
        return ret

    def opponents_rating(self, time_seconds, match, delta_time=1000):
        """Gibt für den angegebenen Zeitpunkt das Rating des Gegners zuück."""
        DEBUG('in opponents_rating() with  time %s  delta_time=%s' % \
                  (time_seconds, delta_time,), OFF)
        me,d = self.match_rating(time_seconds, delta_time=delta_time,
                                                                 delta=True)
        if me is None:
            o_rating = -50.
        else:
            me = float(me.rating) - d     # korrigiere Rating auf Wert vor Match
            o_rating = self.rating_difference(d, float(match.ml), me)
        return o_rating

    def rating_difference(self, delta, ML, my_rating):
        """Calculates the rating difference (formulas below).
          Let D = abs(r1-r2)      (rating difference)
          Let P_upset = 1/(10^(D*sqrt(n)/2000)+1) (probability that underdog wins)
          Let P=1-P_upset if the underdog wins and P=P_upset if the favorite wins.

          For the winner:
            Let K = max ( 1 , -experience/100+5 )
            The rating change is: 4*K*sqrt(n)*P
          For the loser:
            Let K = max ( 1 , -experience/100+5 )
            The rating change is: -4*K*sqrt(n)*P
        """
        K = 1.
        sqrtN = sqrt(ML)
        P = delta/sqrtN/4. #/K   (TODO  fehlt jetzt noch - betrifft nur meine Startzeit)
                        # ausrechnen, ob ich höher oder niedriger gewertet bin
        higher = 1 - 2*int((P < -.5) or ((P > 0) and (P < .5)))
        P = abs(P)
##        print delta, P, ML, self
        if P > .5:
            P = 1. - P
        try:
            D = log10(1./P - 1.)*2000./sqrtN
            ret = my_rating + higher * D
        except:
            ret = -100.
        return ret

    def __repr__(self,):
        return "%d entries in %s" %(len(self),self.full_path)

class JavaRating(Line):

    def __init__(self, line, **kw):
        self.delimiter = ' '
        self.interpretation = ['time', 'rating','experience']
        self.key = 'time'
        Line.__init__(self, line)

    def process(self,):
        il = self.interpreted_line
        il['str_time'] = time.strftime(TIMEFMT,time.localtime(float(il['time'])/1000.))
##        il['long_time'] = long(il['time'])
        
    def print_formatted(self,):
        self.process()
        il = self.interpreted_line
        return '%(str_time)s: %(rating)s  exp %(experience)s' % il

def get_matches(root, opponent=''):
    if opponent:
        kw = {'opponent':opponent}
    else:
        kw = {}
    filename_matches = os.path.join(root,'matches')
    matches = JavaMatches(filename_matches, **kw)
    matches.interpret(JavaMatch)
    matches.list2hash()
    filename_ratings = os.path.join(root,'ratings')
    ratings = JavaRatings(filename_ratings)
    ratings.interpret(JavaRating)
    ratings.list2hash()
    return matches,ratings

def test_sind_alle_drin(matches):
    befund = True
    for i in matches.pliste:
        il = matches.dliste[i.primary_key()]
        found = False
        for l in il:
            if str(i) == str(l):
                found = True
                break
        if not found:
            print i
            befund = False
    if not befund:
        print "test_sind_alle_drin:","Abweichungen gefunden"
    return

def print_opponents(matches, threshold=10):
    print len(matches.dliste),'unterschiedliche Opponenten'
    print 'Mehr als %d Spiele mit....' % threshold
    outs = {}
    for k in matches.dliste:
        lenm = len (matches.dliste[k])
        if lenm > threshold:
            if outs.has_key(lenm):
                outs[lenm].append(k)
            else:
                outs[lenm] = [k,]
    k2 = outs.keys()
    k2.sort()
    k2.reverse()
    for k in k2:
        for o in outs[k]:
            print k,o
    
def markierung_fuer_averages(d):
    if d > 0.:
        c = '+'
    elif d < 0.:
        c = '-'
    else:
        c = ''
    if abs(d) > .02:
        c *= 2
    return c

def listing(matches, ratings, warning=False, tail=0):
    """Erstellt ein Listing der gewünschten Matches (alle oder <opponent>).
    Dabei werden auch die Gewinne/Verluste im Rating ausgegeben.
    """
    rsum = 0
    old_rating = 1500.
    abweichung = 0.
    if tail > 0:                        # TODO: hat matches (oder Liste) bereits
        pliste = matches.pliste[-tail:] #       einen "Tail"-Mechanismus?
    else:
        pliste = matches.pliste
    for k in pliste:
        r,d = k.get_rating(ratings)
        rsum += d
        warn = ''
        if r is None:
            warn = '!!!!! rating is None !!!!'
        elif warning:
            od = (float(r) - old_rating)
            abweichung += od
            if d != od:
                warn = '!!!!! %7.2f != %7.2f !!!!' % (od, d)
            old_rating = float(r)
        print '%-50s %7.2f %10.2f   %s' % (k.print_formatted(),d, rsum, warn)
    if warning:
        print ' '*46+'Gesamtabweichung', abweichung

def usage(progname):
    usg = """usage: %prog [<gegner>]
  %prog """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-a", "--averages",
                  action="store_true", dest="averages", default=False,
                  help="calculate and print averages snapshot")
    parser.add_option("-A", "--gliding_averages",
                  action="store_true", dest="gliding_averages", default=False,
                  help="calculate and print gliding averages")
    parser.add_option("-l", "--list",
                  action="store_true", dest="listing", default=False,
                  help="list the matches")
    parser.add_option("-t", "--tail",
                  action="store", dest="tail", type='int', default=0,
                  help="show only <n> trailing entries")
    parser.add_option("-r", "--root",
                  action="store", dest="file_root",
                  default='/opt/JavaFIBS2001/user/sorrytigger',
                  help="root path to matches and ratings")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) > 0:
        opponent = args[0]
    else:
        opponent = ''

    file_root = options.file_root
    if not os.path.isdir(file_root):
        file_root = '/opt/JavaFIBS2001/user/sorrytigger'
        if options.verbose:
            print 'default root wird verwendet:', file_root

    matches,ratings = get_matches(file_root, opponent=opponent)
    matches.process()

##    if options.testing:                 # TODO: Tests: ab nach tests/....
##        test_sind_alle_drin(matches)
    if options.verbose:
        print_opponents(matches)
        print matches.experience()
    if options.listing:
        listing(matches, ratings, warning=options.verbose, tail=options.tail)
    if options.averages:
        av = matches.get_averages()
        ref = av[-1][1]
        for a,b,d in av:
            c = markierung_fuer_averages(b-ref)
            b *= 100.
            print '%4d Spiele: %6.2f%%  %-2s %s' % (a,b,c,d)
    if options.gliding_averages:
        for avg in matches.gliding_averages():
            print avg
