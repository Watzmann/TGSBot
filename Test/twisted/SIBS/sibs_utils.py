#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities für SIBS.
"""

REV = '$Revision$'

import os

def render_file(filename):
    f = open(os.path.join('ressources',filename))
    txt = f.read()
    f.close()
    return txt


## TODO: man kann die Files schon statisch einlesen.
##   Um die Möglichkeit, im Betrieb nachzuladen könnte man ein dirty-Flag
##   einrichten, das man per Admin-Befehl auf dirty setzt; bei den nächsten
##   Zugriffen wird dann von der Platte nachgeladen
