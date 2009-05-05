#!/usr/bin/python

import sys
import re

class DictWrapper:

    def __init__(self, ):
        pass
        
class StreamReader:

    def __init__(self, stream):
        self.stream = stream
        a = stream.read()
        null = ()
        try:
            self.mydict = eval(a)
        except:
            print 'Kann Datei %s nicht evaluieren!' % stream.name
            raise
        self.children = self.mydict.get('children',[])
        
    def __del__(self, ):
        self.stream.close()

if __name__=="__main__":

    if len(sys.argv) > 1:
        fname = sys.argv[1]
        print fname
        sys.exit()
    else:
        fname = 'Lesezeichen-2008-10-28.json'

    mydict = StreamReader(open(fname))
    for k in mydict.mydict:
        if k != 'children':
            print k, ':', mydict.mydict[k]
    for c in mydict.children:
        print '#####'*3, c
