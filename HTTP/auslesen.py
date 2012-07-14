#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

TODO = """x) zwischen jedem Zugriff ein paar Sekunden warten
2) in zeit_spiele.py schauen, ob Spiel schon vorhanden ist
x) Label ausformulieren
x) game_id noch einbauen"""

from http.client import *
from read_zeit_sudoku import ZeitSudoku
import time

class Sucher(object):

    def __init__(self, year, month, day, level):
        self.game = self.compose_game(year, month, day, level)
        self.label = self.compose_label(year, month, day, level)
        self.nowait = False

    def compose_game(self, year, month, day, level):
        if level > 2:
            action = 'level'
        else:
            action = 'day'
        key = '24091123601092'
        return "action=%s&kd_nr=%s&year=%d&month=%02d&day=%02d&level=-c+%d" % \
                                    (action, key, year, month, day, level)

    def compose_label(self, year, month, day, level):
        lc = {2:'l',3:'m',4:'s',}
        return 'zeit%2s%02d%02d%c' % (str(year)[-2:], month, day, lc[level])

    def extract(self, text):
        return text

    def suche (self,):
        verbindung = HTTPConnection('sudoku.zeit.de')     # hier darf natuerlich nur der Server benannt werden
                                                          # also nicht gleich in /cgi-bin/sudoku hinabsteigen
        suchwort = self.game
        verbindung.request('GET', '/cgi-bin/sudoku/sudoku_kd_app_relaunch.pl?'+suchwort)  #2
        antwort = verbindung.getresponse()
        if int(antwort.status)==200:                      #3
            if False:       # dient nur als Weiche zum Debugging
                htmltext = antwort.read()
                ergebnis = self.extract(htmltext)
                print(ergebnis)
            else:
                self.zs = ZeitSudoku(antwort)
                self.zs.write()
        else:
            print('Keine Antwort von Die Zeit auf', suchwort)     #6
        verbindung.close()
        if not self.nowait:
            time.sleep(2)
        return

class Benutzungsoberflaeche(object):
    def __init__(self):
        s = Sucher(2007,9,28,2)
        #print suchwort
        s.suche()

if __name__ == '__main__':
    Benutzungsoberflaeche()

