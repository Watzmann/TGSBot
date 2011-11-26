#!/usr/bin/env python

class A:

    class B:

        def __init__(self,):
            self.a = 'hallo'

    i = 0
    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    def __init__(self,):
        self.__dict__ = self.__shared_state
        self.i += 1
        print self.i, self.B().a

def do_test():
    r1 = A()
    r2 = A()
    r3 = A()
    r4 = A()
    
if __name__ == '__main__':
    do_test()
