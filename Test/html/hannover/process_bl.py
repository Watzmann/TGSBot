#!/usr/bin/python
# -*- coding: utf-8 -*-

"""process_bl.py   (c) 4/2006 AHausmann AHa.Doc.

process_bl verarbeitet das Suchergebnis für ein Bundesland aus
dem Anbieterverzeichnis der Hannovermesse 2006.
http://www.hannovermesse.de

Das Suchergebnis ist ein html-file (Quellcode aus dem Frameset
der Suchanfrage). Es muss schnell weitergearbeitet werden, da auf
dem Server eine Session läuft, die recht schnell vorbei ist.
Möglicherweise gilt die Session für den Browser und man muss 

Status: erste Entwicklung, läuft, ungetestet.
"""

print 'ok', __doc__

from HTMLParser import HTMLParser
import urllib
import sys,os

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.Text = []
        self.record = False
        return
    def handle_starttag(self, tag, attrs):
        if not self.record: return
        if not tag == 'a': return
        for a in attrs:
            if a[0] == 'onclick':
                b = self.parseline(a[1])
                if b:
                    self.Text.append(b)
                break
        self.record = False
    def handle_endtag(self, tag):
        pass
    def handle_entityref(self, name):
        pass
    def handle_data(self, data):
        pass
    def handle_comment(self, comment):
        if not ('Ausstellereintrag' in comment): return
        if not ('START' in comment): return
        #print '++++++++++#',comment
        self.record = True
    def getText(self):
        return self.Text
    def parseline(self,line):
        a = line.split("'")
        print a
        if len(a) > 1:
            return a[1]
        else:
            return None

class HtmlFile:
    def __init__(self,name):
        self.h = MyHTMLParser()
        h = self.h
        f = file(name)
        h.feed(f.read())
        h.close()
        f.close()
        self.Text = h.getText()
        return

def convert(source,dest):
    g = HtmlFile(source)
    text = g.Text
##    print '---------'*5
    f = open(dest,'w')
    for t in text:
        f.write(t+'\n')
    f.close()
    print len(text),'lines found'
    print source,'::',dest
    return text[1]

def readurl(url,dest):
##    print url,'::',dest
##    url = 'http://www.stiftskantorei-kl.de'
    f = file(dest,'w')
    u = urllib.urlopen(url)
    f.write(u.read())
    u.close()
    f.close()
    print url,'::',dest
    return


if __name__ == '__main__':
    default = '/home/hausmann/Quanta/kleinereSeiten/jupiDokumentation/index.html'
    try:
        root = sys.argv[1]
    except IndexError:
        print 'kein Argument angegeben! (root-path)'
        print 'ich arbeite mit',default
        root = default
    fname = 'trefferliste-Dateien/trefferliste-links_data/trefferliste-links-unten.html'
    url = convert(fname,'bb-1.res')
    readurl('http://www.hannovermesse.de/suche/popup/' + url,'erg.html')
    
        #break
