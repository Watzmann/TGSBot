#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Modul primzahlen.py
Wird im Tkinter-Beispiel ... verwendet.
Python2.x von Uzak: Kapitel 2: Module"""

def p(n):
    """testet, ob n Primzahl ist"""
    for x in range(2,n):
        if n % x == 0:
            return 0
    return 1

def pListe(n):
    """gibt eine Liste mit Primzahlen von 2 bis n zurück"""
    return filter(p,range(2,n))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        n = sys.argv[1]
    else:
        n = 100
    print "Ist %d prim? %s!" % (n,{0:'Nein',1:'Ja'}[p(n)])
    print "...und hier die Liste:"
    print pListe(n)
