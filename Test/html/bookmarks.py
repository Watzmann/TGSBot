#!/usr/bin/python
# -*- coding: utf-8 -*-

"""ich laufe"""

print 'ok', __doc__

from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
    Hrefs = []
    ll = 0
    def __init__(self):
        HTMLParser.__init__(self)
        self.Hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for i in attrs:
                if i[0] == 'href':
                    self.Hrefs.append(i[1])
                    self.ll += 1
                    #print self.Hrefs.append(i[1])
    def handle_endtag(self, tag):
        pass
    def getListHrefs(self):
        return self.Hrefs

class BookMarkFile:
    def __init__(self,name):
        self.h = MyHTMLParser()
        h = self.h
        f = open(name)
        h.feed(f.read())
        h.close()
        self.List = h.getListHrefs()
        self.ll = h.ll
    def getList(self):
        return self.List

name = ['bm.html','bookmarks.html']
b1 = BookMarkFile(name[0])
l1 = b1.getList()[:]
print len(l1),b1.ll
b2 = BookMarkFile(name[1])
l2 = b2.getList()[:]
print len(l2),b2.ll

n = 0
print "\nNur in '%s' vorhanden:" % name[0]
for i in l1:
    if i in l2:
        n += 1
        l2.remove(i)
    else:
        print i

print
print n,'Links gleich'
print len(l2),'links in l2 uebrig'
print "\nNur in '%s' vorhanden:" % name[1]
for i in l2:
    print i

expl = """
Feststellungen (21.5.2005):

1) Das Programm kann bereits solche Links anzeigen, die nur in einem
   der Files vorkommen.
2) Wünschenswert:
   a) Filenamen auf der Kommandozeile
   b) optional die Attribute auch vergleichen (z.B. Modifikationsdatum)
   c) Direkt ein Outputfile schreiben, das beide Linksammlungen enthält
3) Die Struktur mit den Tags <DL> und <DT> habe ich noch nicht verstanden.
4) Ich meine, bereits irgendwo bei Python-Sammlungen einen bookmark-diff
   gesehen zu haben.
"""
print expl

import sys
sys.path[:0] = ['..']
#print sys.path
import cmp_lists
l1 = b1.getList()[:]
l2 = b2.getList()[:]
a = cmp_lists.clist(l1,l2)
cmp_lists.p_all(a)
