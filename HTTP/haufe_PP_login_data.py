#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Extrahiert csv-Datei aus HTML mit Liste von Login-Daten für PartnerPortale (Haufe).
  Einfacher Aufruf. In liste.html ist die besagte html-Datei
  (zB Dropbox-Safe/else/Haufe Gruppe Partner Portal Client.html).
"""

import sys
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.lines = []
        self.Label = {}
        self.record = False
        self.attach = False
        self.data = False
        self.entity = False
        self.columns = ('Portal', 'Login', 'Zugang', 'Key', 'Type', 'IPs',)
        self.entities = {'amp': '&'}
        return

    def handle_data(self, data):
        if self.data:
            self.line.append(data.strip(' \n\t|'))
            if self.entity:
                c = self.line.pop()
                b = self.line.pop()
                a = self.line.pop()
                self.line.append(''.join((a,b,c)))
                self.entity = False

    def handle_entityref(self, name):
        if self.data:
            self.entity = True
            self.line.append(self.entities[name])

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            d = dict(attrs)
            if 'class' in d and d['class'] == 'fullscreen':
                self.record = True
        if self.record and tag == 'tr':
            self.line = []
            self.attach = True          # es beginnt eine Zeile
        elif self.attach and tag == 'td':
            d = dict(attrs)
            if 'class' in d and d['class'] == 'contentDescription':
                self.data = True        # es beginnt der Teil mit den Daten

    def handle_endtag(self, tag):
        if self.record and tag == 'table':
            self.record = False
        elif self.attach and tag == 'tr':
            self.attach = False
            for d in (5,3,2,0):
                if len(self.line) > d:
                    del self.line[d]
            if len(self.line) > 15 and self.line[1] == '-':
                for d in (16,14,13,11,10,8,7,5,4,2):
                    if len(self.line) > d:
                        del self.line[d]
            self.lines.append(dict(zip(self.columns,self.line)))
            #self.lines.append(self.line)
        elif self.data and tag == 'td':
            self.data = False

    def getText(self):
        return self.lines

class HtmlStream:

    def __init__(self, stream):
        self.h = MyHTMLParser()
        h = self.h
        h.feed(stream.read())
        h.close()
        return

    def getText(self):
        return self.h.getText()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        fname = "liste.html"
    else:
        fname = sys.argv[1]
    print >> sys.stderr, 'reading from', fname

    f = open(fname)
    liste = HtmlStream(f).getText()
    f.close()

    print >> sys.stderr, len(liste)
    print '"Portal", "Login erlaubt", "Zugang", "Schlüssel", "Verschlüsselungstyp", "IP Adressen"'
    for l in liste:
        try:
            print '"%(Portal)s","%(Login)s","%(Zugang)s","%(Key)s","%(Type)s","%(IPs)s"' % l
        except:
            pass
