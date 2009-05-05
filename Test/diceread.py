#!/usr/bin/python
"""Mit diesem Programm konnte ich die unten angegebene Datei von diceware
lesen; in die Datei waren jede Menge Nullen eingestreut; ich habe nicht heraus-
gefunden, wie man das Encoding waehlt, um auf elegantere Weise eine Trans-
skription durchzufuehren."""

import string

fname = '/home/andreas/Documents/LessonsLearnt/diceware_german[1].txt'
f = open (fname,'r')

while True:
    t = f.readline()
    if t == '': break
    l=[]
    for i in t:
        if i != '\x00': l.append(i)
    s = string.join(l,'')
    if s == '\n': continue
    print s,
