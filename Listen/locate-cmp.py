#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""Dateien aus einer Liste werden mit locate gesucht und verglichen.
  Ausgegeben werden Dateien, die _nicht_ oder zu denen unterschiedliche
  Versionen gefunden werden.
    :: <dateiname>      Unterschiede gefunden; sie werden eingerückt gelistet
    -- <dateiname>      Datei mit "locate" _nicht_ gefunden
    ++ <dateiname>      Datei mit "locate" _gefunden_ (Option --existing)"""

# mit folgendem Befehl (Beispiel) kann man eine entsprechende Liste erzeugen
# find /var/export/Download -maxdepth 1 -type f -print

import sys,os
from optparse import OptionParser
from listen import Liste
from el_listen import Entry

class Lines(Liste):
    def __init__(self, filename,):
        Liste.__init__(self, filename)
        # Liste: das entspricht dort dem my_filter() kombiniert mit interpret()
        self.results = {}
        self.pliste = []

    def dir_filter(self,):
        # geht nicht in my_filter, weil dort die interpretierten Entrys noch
        # nicht bekannt sind und somit die Abfrage .is_directory() fehlt
        liste = []
        for i in self.pliste:
            if not i.is_directory():
                if options.verbose:
                    print i.full_path
                liste.append(i)
        self.pliste = liste
        return liste
        
def usage(progname):
    usg = """usage: %s <input_list>
  %s""" % (os.path.basename(progname),__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-e", "--existing",
                  action="store_true", dest="existing", default=False,
                  help="print existing files (i.e. that can be deleted)")
    types = Entry.types
    default = Entry.default
    parser.add_option("-t", "--list_type",
                  action="store", type='string', dest="list_type", default=default,
                  help="set the type of the input_list (%s) default='%s'" % (types,default))
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)

    fname = args[0]
    lines = Lines(fname)
    lines.interpret(Entry, **{'list_type':options.list_type})
    lines.dir_filter()
    kw ={'liste':lines,'dic':lines.results}
    lines.process(**kw)
    for l in lines.liste:
        print '>',l,lines.results[l]['found']
    lines.print_lines()
    sys.exit(0)
    # Die Auswertung des Ergebnisses ist "wessen Zuständigkeit"????
    result = lines.results
    for k in result.keys():
        founds = result[k]['found']
        if options.existing:
            if founds and 'equal' in result[k]['equal']:
                print '++',k
                print '    ',founds[result[k]['equal'].index('equal')]
        if result[k]['diffs']:
            print '::',k
            for e,i in enumerate(result[k]['equal']):
                if 'different' == i:
                    print '    ',founds[e]
        elif not founds:
            print '--',k

##    fmt = options.format
##    print '%s: %d %s' % (inhalt.name,inhalt.sumsize(fmt=fmt),fmt)
