#!/usr/bin/python
# -*- coding: utf-8 -*-
"""testet um die getter- setter-Methoden herum"""

class C(object):
    myname = "C"
    def getx(self):
        print 'in %s.getx()' % self.myname
        return self.__x
    def setx(self, value):
        print 'in %s.setx():' % (self.myname,), value
        self.__x = value
    def delx(self):
        print 'in %s.del()' % self.myname
        del self.__x
    x = property(getx, setx, delx, "I'm the 'x' property.")
    y = property(getx, setx, delx, "I'm the 'y' property.")

class Test(C):
    myname = "Test"
    def __init__(self, start=''):
        self.value = start

    def printValue(self,):
        print 'Value:', self.value

    def setValue(self, value):
        print 'im setter'
        self.value = value

if __name__ == '__main__':
    test = Test('Anfang')
    test.printValue()
    test.value = 'Ende'

    print 'print test.value'+' '*10,    
    print test.value
    print
    
    test.printValue()
    setattr(test,'value','von setattr gesetzt')
    print test.value
    test.printValue()

    print 'test.x = 6'+' '*10,
    test.x = 6
    print
    
    print 'test.y = 7'+' '*10,
    test.y = 7
    print

    print "print test.y"+' '*10,test.y

    print 'del test.y'+' '*10,
    del test.y
    print
