#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unicodedata import *
from types import *

print 'hallo'

strings = {u'jüßen':"""Als Unicode wird es auf Console und DOS-Box korrekt
              dargestellt; wird es codiert, wird es im interaktiven Fenster
              bei UTF-8 unleserlich, in der DOS-Box sind _alle_ unleserlich,
              auf der Console (Linux) ist nur UTF-8 leserlich.""",
           'lüßen':'Decodierung misslingt nur bei UTF-8 (DOS und Linux).',
           }

EC = ['   latin-1',
#      '    cp1252',
      '     utf-8',
      'iso-8859-1',
      ]

def info(s):
    print s
    for i in s:
        g = ''
        if ord(i) > 0x7f:
            g = 'x'
        print '#',i,type(i),ord(i),hex(ord(i)),g

    if type(s) is UnicodeType:
        for i in EC:
            t = s.encode(i)
            print i,':',t,'\t(mit dem angegebenen Codec kodiert) %s' % type(t)
    elif type(s) is StringType:
        for i in EC:
            try:
                print i,':',s.decode(i)
            except:
                print 'schief gegangen mit', i
    else:
        print 'strange type', type(s)


print 'v'*50
print 'v'*50
for k in strings.keys():
    print '#######', k, strings[k]
    info(k)
