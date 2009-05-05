# -*- coding: utf-8 -*-
import now
helena=now.birthday()
annabelle=now.birthday()
helena.update((1995,8,14,6,19,00,0,0,-1))
annabelle.update((1997,7,23,16,4,00,0,0,-1))
print 'Helena:', helena
print 'Annabelle:', annabelle
print 'Helena ist um so viel älter als Annabelle:'
helena-annabelle
