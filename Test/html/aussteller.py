#!/usr/bin/python
# -*- coding: utf-8 -*-

"""aussteller.py   (c) 6/2006 AHausmann AHa.Doc.

liest das Ausstellerverzeichnis der ITKom 2006 Mainz und liefert alphabetische Liste

Status: erste Entwicklung, läuft, ungetestet.
"""

print 'ok', __doc__

from HTMLParser import HTMLParser
import sys,os

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.Text = []
        self.record = False
        self.attach = False
        self.Umlaut = dict([['a','ä'],['o','ö'],['u','ü'],['A','Ä'],['O','Ö'],['U','Ü']])
        self.paragraph = ['h'+str(x) for x in range(1,5)]+['p','div']
        print self.paragraph
        return
    def handle_starttag(self, tag, attrs):
        if self.record:
            if tag == 'p':
                self.divLevel +=1
            if tag in self.paragraph:
                self.Text.append('')
        if tag == 'p' and len(attrs):
            for a in attrs:
                if a == ('class','bodytext'):
                    self.record = True
                    self.divLevel = 1
                    break
    def handle_endtag(self, tag):
        if self.record and tag == 'p':
            self.divLevel -=1
            if self.divLevel == 0:
                self.record = False
    def handle_entityref(self, name):
        if self.record:
            if name.endswith('uml'):
                self.Text[-1] += self.Umlaut[name[0]]
                self.attach = True
            if name == 'szlig':
                self.Text[-1] += 'ß'
                self.attach = True
            if name == 'amp':
                self.Text[-1] += '&'
                self.attach = True
    def handle_data(self, data):
        if self.record:
            d = data.strip()
            if not d:
                return
            if self.attach:
                self.Text[-1] += d
                self.attach = False
            else:
                self.Text.append(d)
    def getText(self):
        return self.Text

class HtmlFile:
    def __init__(self,name):
        self.h = MyHTMLParser()
        h = self.h
        f = open(name)
        h.feed(f.read())
        h.close()
        self.Text = h.getText()
        return

def convert(source):
    g = HtmlFile(source)
    text = g.Text[:]
    print len(text)
    for e,t in enumerate(text):
        if t[:3] in ('Der','Die','Das'):
##            print t[:3],
            text[e] = t[4:]
##            print t
    text.sort()
    for t in text:
        print '---------'*5
        print t
##    print source,'::',dest
    return

if __name__ == '__main__':
    default = '/home/hausmann/Recherchen/Markt/it-kom-Mainz/aussteller-2006.html'
    try:
        root = sys.argv[1]
    except IndexError:
##        print 'kein Argument angegeben! (root-path)'
##        print 'ich arbeite mit',default
        root = default
    convert(root)
