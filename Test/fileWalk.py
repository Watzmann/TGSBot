#!/usr/bin/python
# -*- coding: utf-8 -*-

"""liest Files vom FileSystem in Plone ein

fileImport.py ist die external Method für den FileImport.
Es wird ein Baum ab dem Verzeichnis <root> eingelesen (class Tree),
gelabelt (Dokumenttypen)
(c) 2005 AHa.Doc. Andreas Hausmann
"""
import sys,os

def listDir(rootName=''):
    p = []
    list = os.listdir(rootName)
    for i in list:
        pfad = os.path.join(rootName,i)
        type = 'o'
        if os.path.isdir(pfad):
            type = 'd'
            p += listDir(pfad)
        if os.path.isfile(pfad):
            type = 'f'
        p.append((os.path.join(rootName,i),i,type))
    return p

if __name__ == '__main__':
    default = '/home/hausmann/Entwicklung/Import/Archiv'
    liste = listDir(default)
    for p,l,t in liste:
        print p,l,t
