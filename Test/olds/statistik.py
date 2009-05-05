#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""statistik.py prints out statistics in backup information"""

__svn_date__ = "$Date: 2007-10-14 17:49:30 +0200 (So, 14 Okt 2007) $"[8:-2]
__version__ = "$Revision: 195 $"[11:-2]
__svn_url__ = "$HeadURL: svn+ssh://BIC/srv/svn/repositories/Entwicklung/Python/trunk/Test/olds/statistik.py $"[10:-2]
__release__ = "1.0.0"  # Eintragung per Hand (vielleicht geht das auch über svnimport sys
__TODO__="""
TODO
- Klassen überarbeiten"""
import sys
import os
from glob import glob
from optparse import OptionParser
from datetime import datetime
import time

class Entry:

    def __init__(self, fullpath, today, time_format=None):
        self.set_time_format(time_format)
        self.fullpath = fullpath
        self.today = today
        self.basename = os.path.basename(fullpath)
        self.fullflag = self.basename.startswith('full')
        self.preset_time()
        return

    def date(self,):
        ret = getattr(self, 'datename', None)
        if ret is None:
            ret = '.'.join(self.basename.split('.')[1:])
            self.datename = ret
        return ret
    
    def preset_time(self,):
        self.timestamp = self.bu_time(self.basename)
        self.time_passed = self.set_time(self.today)
        return

    def set_time(self, reference):
        self.time_passed = (reference - self.timestamp)
        return

    def bu_time(self, fname):
        fn = fname.split('.')[1][:-6]
        if self.time_format is None:
            fs = fn.split('-')
            if len(fs) == 3:
                fmt = (len(fs[0]),len(fs[1]),len(fs[2]),)
                if fmt == (4,2,2):
                    self.set_time_format("%Y-%m-%d")
            if len(fs) == 4:
                fmt = (len(fs[0]),len(fs[1]),len(fs[2]),len(fs[3]),)
                if fmt == (4,2,2,8):
                    self.set_time_format("%Y-%m-%d-%H:%M:%S")
        d = datetime(*time.strptime(fn, self.time_format)[0:6])
        return d

    def pretty_print(self,):
        print self.time_passed,self.basename,self.fullflag,self.timestamp
        
    def __str__(self,):
        return self.basename

    def set_time_format(self, format):
        self.time_format = format
        if format is None:
            self.hours = False
        elif len(format) <= 8:
            self.hours = False
        else:
            self.hours = True

class FileListe:

    def __init__(self, files):
        self.presentation = Presentation('days',(5,'o','+'))
        self.files = files
        self.sorted = False
        return

    def add(self, key, value):
        self.files[key] = value
        self.sorted = False

    def sorted_list(self,):
        if not self.sorted:
            files = self.files.keys()
            files.sort()
            self.sfiles = files
            self.sorted = True
        return self.sfiles

    def print_sorted(self,):
        for d in self.sorted_list():
            self.files[d].pretty_print()
        return

    def statistik(self,):
        next = getattr(self, 'next', None)
        if next is None:
            return
        old = self.sorted_list()[0]
        entry = self.first()
        for i in self.sorted_list()[1:]:
            entry.set_time(self.files[i].timestamp)
            self.files[old] = entry
            entry = self.files[i]
            old = i
        entry.set_time(self.next)
        self.files[old] = entry

    def print_statistik(self,):
        for i in self.sorted_list():
            print self.files[i].basename.rjust(26), \
                self.presentation.representation(self.files[i].time_passed)
##
##            pd,dc,pc = self.presentation.designators()
##            td = self.files[i].time_passed
##            passed = td.days
##            if self.files[i].hours:
##                passed = passed * 24 + td.seconds / 3600
##            if options.dynamic and passed == 0:
##                passed = td.seconds / 3600        
##                pd,dc,pc = self.presentation.designators('hours')
##            if options.dynamic and passed == 0:
##                passed = td.seconds / 900        
##                pd,dc,pc = self.presentation.designators('quarters')
##            if passed < pd:
##                passed = dc * passed
##            else:
##                passed = dc * (pd-1) + pc + dc * (passed-pd)
##            print self.files[i].basename.rjust(26), passed

    def first(self,):
        if len(self.files):
            ret = self.files[self.sorted_list()[0]]
        else:
            ret = Entry('', datetime.now())
        return ret

    def start(self,):
        return self.first().timestamp

    def __str__(self,):
        return self.first().basename

    def __len__(self,):
        return len(self.files)

class FileStatistik:
    
    def __init__(self, verzeichnis):
        self.presentation = Presentation('days',(14,'#',':'))
        self.time_format = None
        self.now = datetime.now()
        if not os.path.exists(verzeichnis):
            print 'ERROR:', verzeichnis, 'does not exists'
            sys.exit(1)
        expr = os.path.join(verzeichnis,'*.200*-band?')
        self.files = FileListe(self.assess(glob(expr)))
        self.full = self.groups()
        self.full_statistik()

    def assess(self, files):
        ad = {}
        for k in files:
            dnv = Entry(k, self.now, self.time_format)
            ad[dnv.date()] = dnv
            self.time_format = dnv.time_format
        return ad

    def groups(self, files=None):
        if files is None:
            files = self.files.files
        g = FileListe({})
        liste = [g]
        fls = files.keys()
        fls.sort()
        for d in fls:
            if files[d].fullflag:
                g = FileListe({})
                liste.append(g)
            g.add(d, files[d])
        if len(liste[0]) == 0:
            del liste[0]
        return liste

    def full_statistik(self,):
        old = self.full[0]
        for i in self.full[1:]:
            #print old,old.start(),i,i.start()
            old.lasts = (i.start() - old.start())
            old.next = i.start()
            old.statistik()
            old = i
        old.lasts = (self.now - old.start())
        old.next = self.now
        old.statistik()

    def print_full_statistik(self,):
        for i in self.full:
            print i, self.presentation.representation(i.lasts)

class Presentation:

    def __init__(self, resolution='days', cset=(5,'o','+')):
        self.keys = ['period','period_char','limit_char',]
        quarterly_l = [4,'.',',']
        hourly_l = [6,'*','|']
        daily_l = [5,'o','+']
        self.resolution_designators = ['days','hours','quarters']
        self.quarterly = dict(zip(self.keys,quarterly_l))
        self.hourly = dict(zip(self.keys,hourly_l))
        self.daily = dict(zip(self.keys,daily_l))
        self.register = {'':{},'days':self.daily,
                         'hours':self.hourly,'quarters':self.quarterly}
        self.set_resolution(resolution)
        self.set_designators(resolution, cset)

    def set_resolution(self, resolution):
        if not resolution in self.resolution_designators:
            print 'WARNING: wrong resolution designator', resolution
            return
        self.resolution = resolution
        self.register[''] = self.register[resolution]

    def designators(self, resolution=''):
        rc = self.register[resolution]
        return (rc['period'],rc['period_char'],rc['limit_char'])

    def set_designators(self, resolution, cset):
        for k,c in zip(self.keys, cset):
            self.register[resolution][k] = c

    def representation(self, timediff, hours=False):
        pd,dc,pc = self.designators()
        passed = timediff.days
        res = 'days'
        if hours:
            passed = passed * 24 + timediff.seconds / 3600
            res = 'hours'
            self.set_resolution(res)
        if options.dynamic:
            for d,s in ((3600,'hours'),(900,'quarters')):
                if passed == 0:
                    passed = timediff.seconds / d        
                    pd,dc,pc = self.designators(s)
                    res = s
        if options.numeric:
            passed = '%d %s' % (passed,res)
        elif passed < pd:
            passed = dc * passed
        else:
            passed = dc * (pd-1) + pc + dc * (passed-pd)
        return passed

def version():
    vers = 'Version'
    k = ['Date','Version','URL','Release']
    v = [__svn_date__,__version__,__svn_url__,__release__]
    d = dict(zip(k,v))
    if options.verbose:
        for k,v in d.items():
            print k,v
    elif options.todos:
        for k,v in d.items():
            print k,v
        print __TODO__
    else:
        print vers, d[vers]
    sys.exit(0)
    
def usage():
    usg = """usage: %%prog <...>
  %s""" % (__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-d", "--dynamic",
                  action="store_true", dest="dynamic", default=False,
                  help="dynamic: change resolution dynamically)")
    parser.add_option("-n", "--numeric",
                  action="store_true", dest="numeric", default=False,
                  help="numeric presentation of backup duration")
    parser.add_option("-a", "--all",
                  action="store_true", dest="all", default=False,
                  help="print out all available backups")
    parser.add_option("-f", "--full_statistik",
                  action="store_true", dest="full_statistik", default=False,
                  help="print out statistics of full backups")
    parser.add_option("-V", "--version",
                  action="store_true", dest="version", default=False,
                  help="print version information to stdout and exit")
    parser.add_option("-T", "--todos",
                  action="store_true", dest="todos", default=False,
                  help="print full version information to stdout and exit")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage()
    (options, args) = parser.parse_args()
    if options.version or options.todos:
        version()
    if options.verbose:
        print options,args

    defaults = '/var/develop/Python/Source/Test/olds/uranus'
    #defaults = '/root/BU/olds'
    if len(args) == 0:
        print "using default directory", defaults
        verzeichnis = defaults
    else:
        verzeichnis = args[0]

    if options.verbose:
        print verzeichnis
        
    fs = FileStatistik(verzeichnis)
##    fs.files.print_sorted()
##    sys.exit()
    if options.full_statistik:
        fs.print_full_statistik()
##    print '-'*60
    elif options.all:
        for i in fs.full:
            i.print_statistik()
    else:
        l = fs.full[-1]
        print l, fs.presentation.representation(l.lasts)
        l.print_statistik()
