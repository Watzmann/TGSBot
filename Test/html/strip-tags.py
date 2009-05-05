#!/usr/bin/python
# -*- coding: utf-8 -*-

"""strip-tags.py   (c) 12/2005 AHausmann AHa.Doc.

strip-tags holt den Text aus dem <div id="contents"> heraus; html-tags
sind entfernt.

Status: erste Entwicklung, läuft, ungetestet.
"""

print 'ok', __doc__

from HTMLParser import HTMLParser
import sys,os

class Tree:
    def __init__(self,root):
        liste = os.walk(root)
        self.rootLen = len(root)
        self.data = self.bereiteListe(liste)
        return

    def bereiteListe(self,generator):
        """hier wird nach dem Zeilenende gesucht, einem Feld mit dem Inhalt '1'
    Grund: in beschreibenden Feldern koennen durchaus Feldtrenner (';') vorkommen
    """
        liste = []
        for e in generator:
            a,b,c = e
            p = a[self.rootLen:]
            for x in b:
                liste.append((os.path.join(p,x),'d'))
            for x in c:
                liste.append((os.path.join(p,x),'f'))
        return liste

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
            if tag == 'div':
                self.divLevel +=1
            if tag in self.paragraph:
                self.Text.append('')
        if tag == 'div' and len(attrs):
            for a in attrs:
                if a == ('id','content'):
                    self.record = True
                    self.divLevel = 1
                    break
    def handle_endtag(self, tag):
        if self.record and tag == 'div':
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

def importTree(rootName=''):
    if not rootName:
        return []
    satz = Tree(rootName)
    # ein datensatz besteht aus:
    # path rel to root,typ,
    return satz.data

def convert(source,dest):
    g = HtmlFile(source)
    text = g.Text
##    print '---------'*5
    f = open(dest,'w')
    for t in text:
        f.write(t+'\n')
    f.close()
    print source,'::',dest
    return

if __name__ == '__main__':
    default = '/home/hausmann/Documents/AHa.Doc/Marketing/aha-doc.de/aha-doc'
    try:
        root = sys.argv[1]
    except IndexError:
        print 'kein Argument angegeben! (root-path)'
        print 'ich arbeite mit',default
        root = default
    tree = importTree(root)
    files = []
    for e,i in enumerate(tree):
        s = i[0]
        if s.endswith('.html'):
            p2=-2
            p = s.find('/')
            if p > -1:
                p2 = s[p+1:].find('/')
                r = s[p+1:p2+1]
            else:
                x,y = tree[e]
                x = '/' + x
                tree[e] = (x,y)
                r = 'home'
            files.append((e,r+'.txt'))
    for i,j in files:
        convert(root+tree[i][0],j)
        #break
