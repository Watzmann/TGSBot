#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe twisted-book Kap. 4.2.1
"""
from twisted.plugin import getPlugins
from matsim import imatsim

def displayMaterial(m):
    print 'A material with yield stress %s at 500 K' % (m.yieldStress(500),)
    print 'Also a dielectric constant of %s.' % (m.dielectricConstant,)

def displayAllKnownMaterials():
    for material in getPlugins(imatsim.IMaterial):
        print material
        displayMaterial(material)

if __name__ == "__main__":
    displayAllKnownMaterials()
