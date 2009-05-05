#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

import sys
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.Text = []
        self.Label = {}
        self.record = False
        self.attach = False
        return

    def handle_starttag(self, tag, attrs):
        if tag == 'form':
            d = dict(attrs)
            if d.has_key('name') and d['name'] == 'sudoku_form':
                self.record = True
        if self.record and tag == 'td':
            self.attach = True          # es beginnt der Teil mit den Daten
        elif self.attach and tag == 'input':
            d = dict(attrs)             # Daten stehen nur in den Attributen
            n = {}
            n['name'] = d.get('name','')
            n['type'] = d.get('type','')
            n['value'] = d.get('value','x')
            self.Text.append(n)
        elif not self.attach and tag == 'input':
            d = dict(attrs)             # erst noch die Label-Daten
            if d.get('name','') in ['year','month','day','level','game_id',]:
                self.Label[d['name']] = d.get('value','')

    def handle_endtag(self, tag):
        if self.record and tag == 'form':
            self.record = False
        elif self.attach and tag == 'td':
            self.attach = False

    def getText(self):
        return self.Text

    def getLabel(self):
        return self.Label

class HtmlStream:

    def __init__(self, stream):
        self.h = MyHTMLParser()
        h = self.h
        h.feed(stream.read())
        h.close()
        return

    def getText(self):
        return self.h.getText(), self.h.getLabel()

class ZeitSudoku:

    def __init__(self, stream):
        liste, label = HtmlStream(stream).getText()
        level = {'2':'l','3':'m','4':'s',}
        self.g_label = self.r_label = 'zeit%2s%02d%02d%c' % \
                       (label['year'][-2:],int(label['month']),
                        int(label['day']),level[label['level'][-1]])
        self.r_label += '_solution'
        self.game_id = label['game_id']
        self.game,self.result = self.process(liste)

    def process(self, liste):
        g = {}
        for e,i in enumerate(liste):
            n = i['name']
            if n.startswith('FELD'):
                f = int(n[4:])
            elif n.startswith('HIDDEN'):
                f = int(n[6:])
            else:
                f = 99
            j = e/2 + 1
            if f != j:
                print \
        'Warning: Synchronisation Error!! Fieldname %d != %d list index' % (f,j)
            v = i['value']
            if v == '':
                v = '.'
            if f not in g:
                g[f] = {}
            g[f][i['type']] = v
  
        game = []
        result = []
        r = g.keys()
        r.sort()
        gt = (g[a]['text'] for a in r).next
        gh = (g[a]['hidden'] for a in r).next
        for i in range(9):
            game.append('%s'*9 % (gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt()))
            result.append('%s'*9 % (gh(),gh(),gh(),gh(),gh(),gh(),gh(),gh(),gh()))
        return (tuple(game),tuple(result))

    def write(self,):
        fmt = "    '%s': ("+"'%s',"*9+"),"
        gt = (a for a in self.game).next
        print fmt % (self.g_label,gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt())
        gt = (a for a in self.result).next
        print fmt % (self.r_label,gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt())
        print "    '%s_id': %s," % (self.g_label,self.game_id)

    def entries(self,):
        h = {}
        gt = (a for a in self.game).next
        fmt = "("+"'%s',"*9+"),"
        h[self.g_label] = fmt % (gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt())
        gt = (a for a in self.result).next
        h[self.r_label] = fmt % (gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt(),gt())
        h[self.g_label+'_id'] = self.game_id
        return h

if __name__ == "__main__":
    if len(sys.argv) < 2:
        fname = "ah.html"
    else:
        fname = sys.argv[1]

    f = open(fname)
    zs = ZeitSudoku(f) 
    f.close()
    zs.write()
##    for i,j in zip(zs.game,zs.result):
##        print i,j
