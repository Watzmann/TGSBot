#!/usr/bin/python
# -*- coding: utf-8 -*-

"""liest Files vom FileSystem in Plone ein

fileImport.py ist die external Method für den FileImport.
Es wird ein Baum ab dem Verzeichnis <root> eingelesen (class Tree),
gelabelt (Dokumenttypen)
(c) 2005 AHa.Doc. Andreas Hausmann
"""
import sys,os

def hoch(zahl,exp):
    if exp==1:
        return zahl
    else:
        return zahl * hoch(zahl,exp-1)

print 7,3,hoch(7,3)
