#!/usr/bin/env python
"""
Kleines Test-Programm, mit dem ich ausprobiere, wie man ein Attribut erzeugt,
dessen Name nur als String vorliegt. Mit dieser Technik hat man eine hoehere
Flexibilitaet, z.B. in dem komfortablen Commandline-Parser.
(c) Sept 2005 A.Hausmann
"""

print __doc__

class A:
    def __init__(self):
        pass

    def a(self):
        print 'a::',dir(self)

    def set(self,name,val):
        d = self.__dict__
        print d
        d[name] = val
        print d

a = A()                 # Objekt erzeugen
a.a()                   # Elemente anzeigen
a.set('test',7)         # Attribut setzen, dessen Name als String vorliegt
a.a()                   # Elemente anzeigen
print a.test            # Direkt auf das neue Attribut zugreifen
# neuer Versuch mit setattr
setattr(a,'neu',77)     # Attribut setzen, dessen Name als String vorliegt
a.a()                   # Elemente anzeigen
print a.neu             # Direkt auf das neue Attribut zugreifen

