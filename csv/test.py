#!/usr/bin/python

"""ich lese csv-Dateien ein
"""
import sys

class CSV:
    def __init__(self,fname):
        fi = open(fname)
        self.lines = fi.readlines()
        ml = self.mend(self.lines)
        self.data = self.splitLines(ml)
        return

    def mend(self,lines):
        """hier wird nach dem Zeilenende gesucht, einem Feld mit dem Inhalt '1'
    Grund: in beschreibenden Feldern koennen durchaus Feldtrenner (';') vorkommen
    """
        rlines = []
        m = None
        for l in lines:
            l = l.rstrip('\n')
            if not l.endswith(';1'):
                if m:
                    m += l
                else:
                    m = l
                continue
            if m:
                m += l
                rlines.append(m)
                m = None
            else:
                rlines.append(l)
        return rlines

    def splitLines(self,lines):
        """hier wird jede Zeile in Listenelemente aufgespalten. Dabei wird das Feld,
    in dem eine Beschreibung mit Feldtrenner(';') stehen kann, wieder zusammen-
    gefasst
    """
        rlines = []
        for l in lines:
            a = l.split(';')
            b = a[:11] + [''] + a[-4:-1]
            b[11] = a[11:-5][0]
            c = [x.strip('"') for x in b]
            #print c
            rlines.append(c)
        return rlines

def main(fname=''):
    if not fname:
        return
    satz = CSV(fname)
    return satz.data

if __name__ == '__main__':
    d = main(sys.argv[1])
    print len(d)
    print d[1]
    print
    for e,i in enumerate(d):
        if len(i) != 15:
            print e,len(i),i[-3:]
        print e,i[2],i[9]
    
