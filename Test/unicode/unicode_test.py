#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unicodedata

cases = {'8bit': range(256)
        ,'umlaute': ['']
    }


##u = unichr(233) + unichr(0x0bf2) + unichr(3972) + unichr(6000) + unichr(13231)
##print u.encode('utf-8')
##
##for i, c in enumerate(u):
##    print i, '%04x' % ord(c), unicodedata.category(c),
##    print unicodedata.name(c)
##
### Get numeric value of second character
##print unicodedata.numeric(u[1])
##print 'u selbst:',u
##print 'länge',len(u)

#sys.exit(0)

def test(chars):
    for c in range(256):
        u = unichr(c)
        try:
            print c, u, '%04x' % ord(u), unicodedata.category(u),
            print unicodedata.name(u)
        except:
            print

if __name__ == '__main__':
    #test(range(256))
    #test(range(256))
    
# Gut wäre:
#   - Zeichen ausgeben; Code auf der cmd-line
#   - 
