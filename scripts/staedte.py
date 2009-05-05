#!/usr/bin/python
# -*- coding: utf-8 -*-
"""erstellt Liste von Städten aus der Aufstellung, die man auf
http://cities.eurip.com/gebiet/bundeslaender/rheinland-pfalz_Z.html
findet. Die Datei, die ausgewertet wird, wird durch Copy-Paste aus
Browser erstellt.
"""
# Das Format der input-Datei ist etwa wie folgt:
#
#
##Infos zu Abentheuer     Abentheuer in Rheinland-Pfalz mit 500 Einwohnern
##[Branchenverzeichnis] [Veranstaltungen]
## 
##Infos zu Abtweiler      Abtweiler in Rheinland-Pfalz mit 200 Einwohnern
##[Branchenverzeichnis] [Veranstaltungen]
##

# Zeitverbrauch!!!!!!!!
# 15 Min Erstellen der Datei (Rh-Pf)
# 45 Min Skript zum Auswerten
# 20 Min Import und Auswertung in Calc
# 60 Min Aufbohren auf alle Länder
# 60 Min Import und Auswertung in Calc
# 210 Min Korrektur von Einträgen

import sys
from optparse import OptionParser
import os

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
##    def_format = 'MB'
##    parser.add_option("-f", "--format",
##                  dest="format", default=def_format,
##                  help="""set output format to one of 'B,kB,MB,GB';
##                default is %s.""" % def_format)
    return parser,usg

laender = {
    'bayern':'Bayern',
    'bw':'Baden-Württemberg',
    'brandenburg':'Brandenburg',
    'hessen':'Hessen',
    'mv':'Mecklenburg-Vorpommern',
    'niedersachsen':'Niedersachsen',
    'nrw':'Nordrhein-Westfalen',
    'rhpf':'Rheinland-Pfalz',
    'saarland':'Saarland',
    'sachsen':'Sachsen',
    'sanh':'Sachsen-Anhalt',
    'sh':'Schleswig-Holstein',
    'thur':'Thüringen',
    'stadtstaaten':''
    }

class Zeile:
    def __init__(self,line,land):
        self.land = land
        try:
            info = (line.index('Infos'),line.index('zu'), \
                    line.index('in'),line.index(land))
            einw = (line.index('mit'),line.index('Einwohnern'))
            pos = info+einw
        except ValueError:
            #print line
            pos = info
            #sys.exit(1)
        #print pos,len(pos)==6
        npos = (info[2] - info[1])/2
        self.name = ' '.join(line[2:2+npos])
        if len(pos)==6:
            self.einwohner = line[einw[-1]-1]
        else:
            self.einwohner = -1
        return
    def getExport(self,):
        return [self.name,self.land,self.einwohner]
    
def main(fname):
    #print 'Verwende',os.path.basename(fname)
    f = file(fname)
    l = [a.strip('\n') for a in f.readlines()]
    n = []
    for a in l:   #[:15]:
        s = a.split()
        if 'Infos' in s:
            #print s
            z = Zeile(s,laender[fname])
            m = z.getExport()
            print m[0]+';', m[1]+';', m[2]
            n.append(s)
    if options.verbose:
        print len(n),'Städte'
    return

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) < 1:
        print usg
        print "!! Namen der Datei mit Roh-Liste von Städten angeben"
        sys.exit(1)

    for i in args:
        land = os.path.basename(i)
        if options.verbose:
            print options,args
            print 'Verwende',land
        main(land)
