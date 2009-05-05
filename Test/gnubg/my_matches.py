#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""Stellt Einträge in 'matches'-Datei zur Verfügung."""

import sys
import os
import time
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
##    3) Bei -l kann man neben den Spielen die Änderung im Rating ausgeben

class JavaMatches(Liste):

    def __init__(self, liste, **kw):
        Liste.__init__(self, liste)
        DEBUG('JavaMatches.__init__()++++++++++',OFF)
        DEBUG('kw: %s' % kw,OFF)
        DEBUG('%s' % liste,OFF)

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

    win = lambda p: int(p.win)
    
    def average(self, liste, value):
        h = [int(i.interpreted_line[value]) for i in liste]
        return sum(h)/float(len(h))
    
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
                ret.append('')
            else:
                l = aliste[-i:]
##            print i,len(l),self.running_average(l,'win')
                ret.append(self.average(l,'win'))
        ret.reverse()
        ret.append(self.average(aliste,'win'))
        delta = self.get_average_delta(spans)
        return zip(spans,ret,delta)

    def gliding_averages(self,):
        out = ''
        av = matches.get_averages()
        titles = [a for a,b in av]
        out = 'Datum;;'
        for t in titles:
            out += '%d;' % t
        out += '\n'
        for i in range(25,len(self.pliste)):
            timestamp = self.pliste[i].interpreted_line['time']
            timestr = self.pliste[i].interpreted_line['str_time']
            times = timestr[:8]+';'+str(timestamp)+';'
            av = matches.get_averages(up_to_index=i+1)
            values = [b for a,b in av]
            for t in values:
                if t == '':
                    out += ';'
                else:
                    out += '%6.4f;' % (t,)
            yield times + out[:-1].replace('.',',')
            out = ''

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

def get_matches(root):
    filename_matches = os.path.join(root,'matches')
    matches = JavaMatches(filename_matches)
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

def usage(progname):
    usg = """usage: %prog <...>
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
    parser.add_option("-t", "--test",
                  action="store_true", dest="testing", default=False,
                  help="do some testing")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) > 0:
        file_root = args[0]
    else:
        file_root = ''

    if not os.path.isdir(file_root):
        file_root = '/opt/JavaFIBS2001/user/sorrytigger'
        print 'default root wird verwendet:', file_root

    matches,ratings = get_matches(file_root)
    matches.process()

    if options.testing:
        test_sind_alle_drin(matches)
    if options.verbose:
        print len(matches.dliste),'unterschiedliche Opponenten'
        for k in matches.dliste:
            if len (matches.dliste[k])>10:
                print k, len (matches.dliste[k])
    if options.listing:
        for k in matches.pliste:
            print k.print_formatted()
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
