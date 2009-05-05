#!/usr/bin/python
# -*- coding: latin-1 -*-
"""Das Skript soll das Coding einer Datei ermitteln.
Möglicher Input sind Dateiname oder stdin.
Das Coding wird zeilenweise ermittelt. Für jede Zeile wird (aktuell)
ein set of flags ausgegeben - ein 'x' für jeden geglückten Decodierungs-
versuch.
TODO: Die Ausgabe darf gerne noch reduziert werden. Gewünscht ist ein
Ergebnis der Art 'utf-8' oder ('latin-1','iso-8859-1').
"""

import sys
from unicodedata import *
from types import *
from optparse import OptionParser
from Listen.listen import Liste

strings = {'jüßen':"""Als Unicode wird es auf Console und DOS-Box korrekt
              dargestellt; wird es codiert, wird es im interaktiven Fenster
              bei UTF-8 unleserlich, in der DOS-Box sind _alle_ unleserlich,
              auf der Console (Linux) ist nur UTF-8 leserlich.""",
           'lüßen':'Decodierung misslingt nur bei UTF-8 (DOS und Linux).',
           }

EC = ['   latin-1',
      '    cp1252',
      '     utf-8',
      'iso-8859-1',
      ]

class My_Liste(Liste):

    def __init__(self, liste, **kw):
        Liste.__init__(self, liste, **kw)

    def my_filter(self, **kw):
        ls = []
        flags = []
        for l in self._raw_liste:
            ls.append(l)
            flags.append(self.coding(l))
        self.tagged = zip(flags,ls)
        return ls

##    def tar_reduce(self, depth=DEF_DEPTH):
##        l = []
##        for i in self.liste:
##            a = i.split('/')
##            if (depth == 0) or (len(a) < depth+2):
##                l.append(i)
##        return l
##
    def coding(self, s):
#        print s
        if type(s) is UnicodeType:
            for i in EC:
                t = s.encode(i)
                print i,':',t,'\t(mit dem angegebenen Codec kodiert) %s' % type(t)
        elif type(s) is StringType:
            l = {}
            for i in EC:
                try:
                    #print i,':',s.decode(i)
                    a = s.decode(i)
                    l[i] = True
                except:
                    l[i] = False
                    #print 'schief gegangen mit', i
        else:
            print 'strange type', type(s)
        return tuple([l[i] for i in EC])

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-s", "--strings",
                  action="store_true", dest="strings", default=False,
                  help="use internal strings (test mode)")
    return parser,usg

table = {True: 'x', False: '.'}
def convert(x):
    return table[x]

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        args.append('-')

    if options.strings:
        param = strings.keys()
    else:
        param = args[0]
    l = My_Liste(param,)
    for i in l.tagged:
        x = ''.join(map(convert, i[0]))
        print x, i[1].decode('latin-1').encode('utf-8')
