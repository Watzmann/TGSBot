#
# Tools zum Testen eines Konnektors fuer den Brainfiler
#
# c Pylon AG  Andreas Hausmann Sept 2004

import types
import sys

class printElements:
    """Diese Klasse zeigt die Elemente eines beliebigen Objekts"""
#    print '... und aus der Klasse "printElements"'
    def __init__(self,myObject):
        self.obj = myObject
        print myObject

    def showAll(self):
        print ">>>>>>>>>>>>>> in showAll"
        print dir(self.obj)
        print self.obj.__doc__
        print help(self.obj)


class ahDebugModes:
    debugGeneral = True     # Debugging Generalschalter (True: an; False: generell aus)
    debugLevel = 1
    Levels = dict([('silent',0), \
                   ('quiet' ,1), \
                   ('trace' ,2), \
                   ('medium',3), \
                   ('loud'  ,4), \
                   ('detail',5),])

    def switchedOn (self, level):
        state = (level <= self.debugLevel) and self.debugGeneral
        if False and self.debugLevel == 5:
            print "in Debugging: switchedOn", level, '<=', self.debugLevel, 'and', self.debugGeneral, '=:', state
        return state

    def setLevel (self, lev):
        if type(lev) is types.IntType:
            self.debugLevel = lev
        elif type(lev) is types.StringType:
            self.debugLevel = Levels[lev]
        ahDebug (5, "in Debugging: new level '%s'" % self.getLevel('name'))

    def getLevel (self, key=''):
        rt = self.debugLevel
        if key != '':
            rt = self.Levels.keys()[self.Levels.values().index(rt)]
        return rt

    def Off (self):
        self.debugGeneral = False

    def On (self):
        self.debugGeneral = True


Dbg = ahDebugModes()
errStr  = "--------- ERROR ---------"
warnStr = "-------- Warning --------"

def ahDebugList (msg1, list):
    for i, l in enumerate(list):
        print "##: %s (%s) %s" % (msg1, i, repr(l))

def ahDebug (dbg, msg1, msg2=""):
    if not Dbg.switchedOn(dbg):
        return
    if type(msg2) is types.ListType:
        #print '++++++++++++++++++++++',msg1, msg2
        ahDebugList (msg1, msg2)
    else:
        if msg2=="":
            print "##:", msg1
        else:
            print "##:", msg1, `msg2`

def ahWarning (msg1, msg2=""):
    if not Dbg.switchedOn(2):
        return
    if msg2=="":
        print warnStr, msg1
    else:
        print warnStr, msg1, `msg2`

def ahError (msg1,msg2):
    if not Dbg.switchedOn(1):
        return
    if msg2=="":
        print errStr, msg1
    else:
        print errStr, msg1, `msg2`

def step(frame, event, arg):
    if event=='call' or event=='line':
        fn = frame.f_code.co_filename
        sys.stderr.write("%s:%s\n" % (fn, frame.f_lineno))

def setLevel (level):
    Dbg.setLevel(level)
    return

def getLevel ():
    return Dbg.getLevel()

def getLevelByName ():
    return Dbg.getLevel('name')

def starttrace():
    sys.settrace(step)

def stoptrace():
    sys.settrace(None)
