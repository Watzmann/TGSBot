#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Dateien aus einer Liste werden mit locate gesucht und verglichen.
  Ausgegeben werden Dateien, die _nicht_ oder zu denen unterschiedliche
  Versionen gefunden werden.
    :: <dateiname>      Unterschiede gefunden; sie werden eingerückt gelistet
    -- <dateiname>      Datei mit "locate" _nicht_ gefunden
    ++ <dateiname>      Datei mit "locate" _gefunden_ (Option --existing)"""

# mit folgendem Befehl (Beispiel) kann man eine entsprechende Liste erzeugen
# find /var/export/Download -maxdepth 1 -type f -print

import sys,os
from optparse import OptionParser

class Entry:
    """The class that takes an entry line, parses and renders information
    and methods concerning the lines contents."""
    
    types = ['tar','long','simple',]
    default = 'simple'
    
    def __init__(self, line, line_type=None):
        self.line_types = {'long': self.parse_long,
                           'tar': self.parse_tar,
                           'simple': self.parse_simple,
                          }
        self.full_name = ''
        self.name = ''
        self.path = ''
        self.access = ''
        self.nr_links = ''
        self.user = ''
        self.group = ''
        self.size = 0L
        self.date = ''
        self.time = ''
        if line_type:
            self.line_type = line_type
        else:
            self.line_type = self.which_type(line)
        self.parse(line, self.line_type)

    def __repr__(self,):
        from StringIO import StringIO
        out = StringIO()
        for i in ('full_name', \
                  'name', \
                  'path', \
                  'access', \
                  'nr_links',
                  'user',
                  'group',
                  'size',
                  'date',
                  'time',):
            ev = eval('self.%s' % i)
            if ev:
                print >> out, '%10s:' % i, ev
        return out.getvalue()
    
    def which_type(self, line):
        # netter versuch
        # von der Idee her gut
        # das kann man ausbauen, aber
        #   - es sollte dann von unten eine eigene Exception hochgegeben werden
        #   - es sollte generalisiert werden
        #   - es sollten spezielle Versuchs-Methoden sein
        for k in self.line_types.keys():
            if k == self.default:
                continue
            print 'trying', k
            try:
                self.line_types[k](line)
                print 'tried',k,'with success'
                return k
            except:
                print 'tried',k,'no success'
                pass
        k = self.default
        try:
            self.line_types[k](line)
            print 'tried',k,'with success'
        except:
            k = 'no_parser'
        return k
    
    def parse(self, line, line_type):
        ret = ''
        if 'no_parser' == line_type:
            print '! no parser available'
        else:
            try:
                ret = self.line_types[line_type](line)
            except:
                print 'encountered errors parsing', line_type
                print '>>>', line
        return ret

    def parse_simple(self, line):
        return self.parse_path(line)

    def parse_long(self, line):     # mit parse_tar zusammenlegen !
        #print line
        self.access = line[:10]
        rest = line[11:]
        a = rest.split(' ')
        while not a[0]:
            del a[0]
        #print a
        self.nr_links = int(a[0])
        self.user = a[1]
        self.group = a[2]
        del a[:3]
##        for i in (self.access,`self.nr_links`,self.user,self.group):
##            print '#'+i+'#',
        while not a[0]:
            del a[0]
        self.size = long(a[0])
        self.date = a[1]
        self.time = a[2]
##        for i in (`self.size`,self.date,self.time):
##            print '#'+i+'#',
        a = self.parse_path(a[3])
##        for i in (self.path,self.name,self.full_name):
##            print '#'+i+'#',
##        print
        return line

    def parse_tar(self, line):
        self.access = line[:10]
        rest = line[11:]
        a = rest.split(' ')
        users = a[0].split('/')
        self.user = users[0]
        self.group = users[1]
        del a[0]
        while not a[0]:
            del a[0]
##        print line
##        for i in (self.access,self.user,self.group):
##            print '#'+i+'#',
        self.size = long(a[0])
        self.date = a[1]
        self.time = a[2]
##        for i in (`self.size`,self.date,self.time):
##            print '#'+i+'#',
        a = self.parse_path(a[3])
##        print a
        return line

    def parse_path(self, fullname):
        a = os.path.split(fullname)
        self.path = a[0]
        self.name = a[1]
        self.full_name = fullname
        return fullname

    def is_directory(self,):
#        print self.access
        return self.access and 'd' == self.access[0]

class Lines:
    def __init__(self, filename, list_type):
        # Liste: __init__() und read_liste_from_file()
        #        dort wird in __init__ noch input unterschieden
        f = open(filename)
        self.lines = [a.strip('\n') for a in f.readlines()]
        f.close()
        # Liste: das entspricht dort dem my_filter() kombiniert mit interpret()
        self.results = {}
        self.entries = []
        for l in self.lines:
            self.entries.append(Entry(l, list_type))
        return
    def do_lines(self,):
        for l in self.entries:
            # die Abfrage nach dir sollte in proc() erfolgen,
            # dito verbose
            if not l.is_directory():
                if options.verbose:
                    print l.full_name
                self.proc(l,self.results)
        return
    def print_lines(self,):
        # das hier geht als spezielle Eigenschaft der Liste durch
        #   allerdings sollte auch eine Line() eine print-Methode haben
        for l in self.entries:
            print l.name, l.path
        return
    def proc(self,entry,dic):
        # das hier ist keine Listen-Eigenschaft (-Methode), sondern eine
        # Zeilen-Eigenschaft.
        b_entry = entry.name
        if not b_entry or ':' == b_entry:
            return          # untersuche _nicht_ Files wie '/home/andreas/:'
        found_list = list(self.find_entry(b_entry))
        #print 'fl',entry.name,found_list
        #print entry
        if entry.full_name in found_list:
            found_list.remove(entry.full_name)
        equal_list = [self.equal_entry(entry.full_name,c_entry) for c_entry in found_list]
        #print 'el',equal_list
        dic[entry.full_name] = {'found':found_list,'equal':equal_list,
                      'diffs':'different' in equal_list}
        #print 'dic',dic[entry.full_name]
        return
    def find_entry(self,entry):
        # wie proc()
        p = os.popen('locate -b "%s"' % entry)
        lines = p.readlines()
        p.close()
        #print entry,':?:',lines
        l = [a for a in lines if not '/.svn' in a]      # masking off .svn
        return [a.strip('\n') for a in l]
    def equal_entry(self,entry,companion):
        # wie proc()
        r = 'equal'
        if os.path.basename(companion) <> os.path.basename(entry):
            return r
        p = os.popen('cmp "%s" "%s" 2>/dev/null' % (entry,companion))
        lines = p.read()
        p.close()
        if lines:
            r = 'different'
        return r
        
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
    lines = Lines(fname, options.list_type)
    lines.do_lines()
    for l in lines.lines:
        print '>',l,lines.results[l]['found']
    lines.print_lines()
    sys.exit(0)
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
