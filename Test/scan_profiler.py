#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""was macht das script"""

import sys
import os.path
import datetime
from optparse import OptionParser

#----------------------------------------
# import listen modules
# this is done by extending the sys.path variable
# TODO: global mechanism
ipath = "/var/develop/Python/Source/Listen"
if not ipath in sys.path:
    sys.path.append(ipath)

from listen import Liste
from el_listen import Line
#----------------------------------------

class ListenParser(Liste):
    """Adds specific methods to Liste"""
    
    def build_scan_logs(self,):
        """Build Scan-Log-Events from list of Log-Entries.

A Scan-Log-Event is a single or multiline log entry:
  - Entries like INFO, Warning, ...
  - Entries like ERROR + Traceback
"""
        self.scan_log_events = a = []
        p = None
        old = None
        for i in self.pliste:
            if i.is_regular():
                if not p is None:
                    p.previous = old
                    a.append(p)
                    old = p
                p = LogEvent(i)
            else:
                p.append(i.line)
        if not p is None:
            a.append(p)
        self.index = EventDictionary(self.scan_log_events).index

    def print_scan_logs(self, headers=False, indicate_start=False):
        for i in self.scan_log_events:
            if indicate_start and i.start:
                print '#'*20,'START SCAN','#'*20
            if indicate_start and i.end:
                print '#'*20,'END   SCAN','#'*20
            if headers:
                print i.major.line_interpreted()
            else:
                print i

    def build_scan_events(self,):
        """Build Scan-Events from list of Scan-Log-Entries

A Scan-Event is a whole cycle consisting of multiple log entries:
  - starting with Scanner getting ready
  - ending with closing the ScanClient
"""
        for p in self.index['component']['DmsFrame::MnuOpenScanner']:
            if p.major.message == 'MnuOpenScanner von DmsFrame':
                p.start = True
                if p.previous is not None:
                    p.previous.end = True
                #print p.major.line_interpreted()

        self.scan_events = a = []
        se = []
        for p in self.scan_log_events:
            se.append(p)
            if p.end:
                a.append(ScanEvent(se))
                se = []
        if se:
            a.append(ScanEvent(se))
        self.profile_scan_events()

    def print_scan_events(self,):
        for i in self.scan_events:
            print i
            print '-'*40

    def profile_scan_events(self,):
        if not hasattr(self,'scan_events'):
            return
        for i in self.scan_events:
            i.profile()

    def statistics(self,):
        if not hasattr(self,'scan_events'):
            return
        self.stats = stat = Statistics(self.scan_events, )
        stat.sum_up()
        stat.histogram()
##        for i in stat.result:
##            print 'stat', i.ljust(10), stat.result[i]
        sr = stat.result
        for i in self.scan_events:
            for p in i.stamps.profile:
                for v in i.stamps.profile[p]:
                    if v > sr[p][2]:
                        print 'Ausreisser',p,v
                        print i

    def print_csv(self, fname='scan_statistics.csv'):
        import csv
        cf=open(fname,'wb')
        writer=csv.writer(cf,dialect='excel',delimiter=';')
        self.stats.csv_out(writer)
        cf.close()

class LogEvent:
    """Contains a single Log Entry:
  - Entries like INFO, Warning, ...
  - Entries like ERROR + Traceback
"""
    from StringIO import StringIO

    def __init__(self, major=None):
        self.entry = [major]
        self.major = self.entry[0]
        self.start = False
        self.end = False
        self.previous = None
        
    def append(self, line):
        self.entry.append(line)
        
    def __repr__(self,):
        c = self.StringIO()
##        print >> c, self.entry[0].line,
##        print >> c
        print >> c, self.major.line_interpreted(),
##        print >> c, self.major.line_formatted(),
        if len(self.entry) > 1:
            for i in self.entry[1:]:
                print >> c
                print >> c, i,
        return c.getvalue()

class EventDictionary:

    def __init__(self, events):
        indices = ('type', 'module', 'component')
        self.index = idx = dict(zip(indices,({},{},{},)))
        for p in events:
            for ic in indices:
                i = getattr(p.major,ic,None)
                v = idx[ic].get(i,[])
                v.append(p)
                idx[ic][i] = v

class ScanEvent:
    """Contains a (complete) Scan Event:
  - whether complete is indicated by .is_complete()
"""

    from StringIO import StringIO

    def __init__(self, events=[]):
        self.log_events = a = events
        self.start = a[0]
        self.end = a[-1]
        self._complete = (self.start.start and self.end.end)

    def is_complete(self,):
        return self._complete

    def __repr__(self,):
        c = self.StringIO()
        print >> c, '%scomplete' % ('' if self.is_complete() else 'in',)
        print >> c, self.start.major.line_interpreted()
        print >> c, '...'
        print >> c, self.end.major.line_interpreted(),
        return c.getvalue()

    def profile(self,):
        if self.is_complete():
##            print 'profiling', self.start.major.line_interpreted()
            self.index = idx = EventDictionary(self.log_events).index
            note = {}
            try:
                for p in idx['component']['DmsFrame::MnuAcquire']:
                    if p.major.message.startswith('Scanvorgang wird ausge'):
                        note[p] = 'scan'
            except KeyError:
                pass
            try:
                for p in idx['component']['DmsFrame::ProcessXFer']:
                    if p.major.message.startswith('=========='):
                        note[p] = 'process'
                    if p.major.message.startswith('more_to_come'):
                        note[p] = 'convert'
                    if p.major.message.endswith('diese jetzt gescannt werden.'):
                        note[p] = 'wait'
            except KeyError:
                pass
            try:
                for p in idx['component']['DMS::putImage']:
                    if p.major.message.startswith('Die gescannten Seiten'):
                        note[p] = 'transfer'
                    if p.major.message.startswith('Antwort URL'):
                        note[p] = 'XFer'
            except KeyError:
                pass
            try:
                for p in idx['component']['DMS::Static_Delete_Image']:
                    if p.major.message.startswith('Temporaere Bilddaten'):
                        note[p] = 'delete'
            except KeyError:
                pass

            self.events = e = [(self.start,'start')]
            for l in self.log_events[1:-1]:
                if l in note:
                    self.events.append((l,note[l]))
            if self.events[-1][1] == 'process':
                if self.log_events[-2].major.message.endswith('258'):
                    self.events[-1] = (self.events[-1][0],'quit')
            self.events.append((self.end,'end'))
            self.steps = dict(self.events).keys()
            self.stamps = Profile(self)
        else:
##            print 'not profiling', self.start.major.line_interpreted()
            self.stamps = Profile(self, 'not complete')

class LogLine(Line):

    from StringIO import StringIO

    interpretation = ['sdate',      # in self.process() wird direkt auf 
                      'stime',      #   die attribute zugegriffen
                      'type',       # d.h.: Änderungen hier haben
                      'module',     #   Auswirkung dort
                      'component',
                      'message',
                      ]
    fmt = "%Y-%m-%d %H:%M:%S"       # 2007-09-12 13:37:47,151

    def __init__(self, line):
        Line.__init__(self, line, discard_contiguos_blanks=True)
        self._regular = False

    def is_regular(self,):
        return self._regular

    def process(self, **kw):
        #print self.line
        t = self.stime.split(',')
        try:
            self.tseconds = t[1]
            micros = (int(t[1]) * 1000) if t[1] else 0
        except IndexError:
            self.tseconds = None
            micros = 0
        try:
            self.date = datetime.datetime.strptime(self.sdate + t[0], self.fmt)
            self.date = self.date.replace(microsecond = micros)
        except ValueError:
            return
        try:
            self.module = self.module.split('=')[1]
        except:
            return
        try:
            self.component = self.component.split('=')[1]
        except:
            return
        try:
            self.py_file = self.module
            idx = self.message.index('\\t')
            self.module = self.message[:idx].split('=')[1]
            self.message = self.message[idx+3:]
        except:
            pass
        self._regular = True

    def line_interpreted(self,):
        return '%s %s %-8s %s %s %s' % (self.sdate, self.stime, self.type,
                                     self.module, self.component, self.message)

    def line_formatted(self,):
        out = self.StringIO()
        if not self._regular:
            print >> out, '',
        else:
            for l in self.interpretation + ['date', 'tseconds', 'py_file']:
                print >> out, l,':',getattr(self,l,'##')
            print >> out, '-'*60
        return out.getvalue()

class Profile:

    def __init__(self, event, comment=''):
        
        def updating(step, value):
            v = prof.get(step,[])
            v.append(value)
            prof[step] = v
            
        def delta_pair(seq):
            i = 0
            for i in range(len(seq)-1):
                yield (seq[i],seq[i+1])
            
        self.comment = comment
        self.caller = event
        
        self.profile = prof = {}
        if event.is_complete():
            last = event.steps[0]
            for s,t in delta_pair(event.events):
                label = s[1]
                delta = t[0].major.date - s[0].major.date
                #print delta, label
                updating(label, delta)

##
##  Die oft auftretende Funktion updating() soll durch
##  eine Klasse ersetzt werden, die die entsprechende
##  Funktionalität bietet
##
##                was ist dict.update()?????
##

class Statistics:

    import math

    def __init__(self, profiles, resolution=10):
        
        def updating(step, value):
            v = acc.get(step,[])
            v += value
            acc[step] = v

        self.resolution = resolution
        self.account = acc = {}
        for i in profiles:
            for p in i.stamps.profile:
                updating(p, i.stamps.profile[p])

    def sum_up(self,):
        self.result = {}
        for i in self.account:
            a = self.account[i]
            if a:
                summ = a[0]
                for b in a[1:]:
                    summ += b
                mean = summ/len(a)
                
                d = abs(a[0]-mean)
                x2 = float('%d.%d' % (d.seconds,d.microseconds))
                summ = x2*x2
                for b in a[1:]:
                    d = abs(b-mean)
                    x2 = float('%d.%d' % (d.seconds,d.microseconds))
                    summ += x2*x2
                d = '%07d' % int(self.math.sqrt(summ/len(a))*1000000)
                x2 = datetime.timedelta(0,int(d[:-6]),int(d[-6:]))
                self.result[i] = mean,x2,mean+2*x2

    def histogram(self,):
        
        def updating(value):
            v = temp.get(value,0)
            v += 1
            temp[value] = v

        self.histo = h = {}
        temp = {}
        res = self.resolution
        for i in self.account:
            a = self.account[i]
            c = [float('%d.%d' % (d.seconds,d.microseconds)) for d in a]
            for v in c:
                updating(int(v/res))
            h[i] = temp
            temp = {}

    def csv_out(self, csv):
        for i in self.histo:
            a = self.histo[i]
            d = a.keys()
            d.sort()
            mx = d[-1]
            c1 = range(mx+1)
            c2 = [0]*(mx+1)
            for e in d:
                c2[e] = a[e]
            csv.writerow([i])
            csv.writerow(c1)
            csv.writerow(c2)

def usage():
    usg = """usage: %%prog <...>
  %s""" % (__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage()
    (options, args) = parser.parse_args()
    if len(args) < 1:
        log_file_name = os.path.expanduser("~/Documents/AHa.Doc/Kunden/STE/Daten/Scanner/ScanClient.log.short")
    else:
        log_file_name = args[0]
    if options.verbose:
        print 'using logfile', log_file_name

    log = ListenParser(log_file_name)
    #print
    log.interpret(LogLine)  # jede Zeile wird eine Logfile-Zeile enthalten
    log.process()           # jede Zeile wird verarbeitet
    #log.print_lines(start = 67, end = 86)

    log.build_scan_logs()
    log.build_scan_events()
    stat = log.statistics()
    log.print_csv(os.path.expanduser("~/tmp/scan_profile.csv"))
    #log.print_scan_logs(headers=True, indicate_start=True)
    #log.print_scan_events()
