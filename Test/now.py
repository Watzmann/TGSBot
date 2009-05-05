#!/usr/bin/python

import time

class now:
    def __init__ (self):
        self.snaptime()
    def __str__ (self):
        return self.ntime()
    def __repr__ (self):
        return self.ntime()
    def __sub__ (self, a):
        print self.ntime()
        print a.ntime()
        print self.second - a.second
        return
    def __call__ (self, t=-1.):
        if t < 0.:
            self.t = time.time()
        else:
            self.t = t
        self.storetime()
        return
    def storetime (self):
        self.year, \
        self.month, \
        self.day, \
        self.hour, \
        self.minute, \
        self.second, \
        self.dow, \
        self.doy, \
        self.dst = time.localtime(self.t)    # dst = daylight saving time
    def snaptime (self):
        self.t = time.time()
        self.storetime()
    def ntime (self):                       # ntime() = display time
        return time.ctime(self.t)

class today(now):
    def __init__ (self):
        now.__init__(self)
    def update (self,date_tupel):
        tt = date_tupel
        if len(tt) < 9:
            raise TypeError
        if tt[0] < 1970 or tt[0] > 2038:
            raise OverflowError
        self.t = time.mktime(tt)
        self(self.t)
        return
    def lap (self, n=-1.):
        if n < 0.:
            n = time.time()
        l = n - self.t
        sek = l
        min = sek/60
        std = min/60
        tage = std/24
        woch = tage/7
        jahre = tage/365.25
        monat = jahre * 12
        return (sek,min,std,tage,woch,monat,jahre)
    def printLap (self, differenz=(0,0,0,0,0,0,0.), msg='Alter:'):
        print msg, 
        print '%d Sekunden, %d Minuten, %d Stunden, ' % differenz[0:3]
        print '%d Tage, %d Wochen, %d Monate,' % differenz[3:6],
        print '%2.2f Jahre' % differenz[6:7]
        return

class birthday(today):
    def __init__ (self):
        today.__init__(self)
    def __sub__ (self, other):
        return self.printLap(self.lap(other.t), msg='')

if __name__ == '__main__':
    n = now()
    print "wir schreiben das Jahr", n.year
    print n
else:
    print "'now' geladen", now()
