
import os

class Test1:
    def __init__(self,):
        print __name__

    def tables(self,):
        self.tabs = self.load('tables')
        for t in self.tabs.keys():
            print t, self.tabs[t]

    def spoons(self,):
        self.sps = self.load('spoons')
        for t in self.sps.keys():
            print t, self.sps[t]

    def load(self, name):
        fname = os.path.join('data',name+'.dat')
        f = file(fname)
        lst = [l.rstrip('\n') for l in f.readlines()]
        print name
        #print lst
        dct = {}
        for i in lst:
            a = i.split(';')
            dct[a[0]] = a[1]
        return dct
