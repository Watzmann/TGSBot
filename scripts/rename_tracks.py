#!/usr/bin/python
# -*- coding: utf-8 -*-
"""teste Argumente von der Befehlszeile


(c) 10/2005 Andreas Hausmann
"""

import os

dir = 'tokio-hotel'
liste=[
    ('track_01.mp3','schrei.mp3'),
    ('track_02.mp3','durch-den-monsun.mp3'),
    ('track_03.mp3','leb-die-sekunde.mp3'),
    ('track_04.mp3','rette-mich.mp3'),
    ('track_05.mp3','freunde-bleiben.mp3'),
    ('track_06.mp3','ich-bin-nich-ich.mp3'),
    ('track_07.mp3','wenn-nichts-mehr-geht.mp3'),
    ('track_08.mp3','lass-uns-hier-raus.mp3'),
    ('track_09.mp3','gegen-meinen-willen.mp3'),
    ('track_10.mp3','jung-und-nicht-mehr-jugendfrei.mp3'),
    ('track_11.mp3','der-letzte-tag.mp3'),
    ('track_12.mp3','unendlichkeit.mp3')]

os.chdir(dir)
print os.getcwd()

for i in os.listdir('.'):
    j = i+'.mp3'
    print i,'->',j
    os.rename(i,j)
