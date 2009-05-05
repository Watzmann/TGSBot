#!/usr/bin/python

"""Zope Entwicklung Helferlein
inhalte.py konvertiert eine Parameterliste in einen String, der als
Request uebergeben werden kann.

inhalte.py <parameterliste>

(c) Oktober 2005, AHa.Doc., Andreas Hausmann
"""

import sys

a = sys.argv[1] + ','
list = a.split("='',")

out = ''
for i in list[:-1]:
    out += "'&%s='+%s+" % (i,i)

print out.strip('+')
