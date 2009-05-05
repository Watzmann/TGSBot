#!/usr/bin/python

base = 10

class row111:
    def __init__ (self,list):
        self.list = list
        self.index = -1
        self.results = []
        self.build()

    def __iter__ (self):
        return self

    def next (self):
        self.index += 1
        if self.index == len(self.results):
            raise StopIteration
        return self.results[self.index]

    def build (self,preset=(-1,-1,-1)):
        A,B,C = preset
        alist = self.list[:]
        if A > -1: alist = [A]
        for a in alist:
            avail = self.list[:]
            if A == -1: avail.remove(a)
            blist = self.list[:]
            if B > -1: blist = [B]
            for b in blist:
                if B == -1:
                    if b not in avail: continue
                    avail.remove(b)
                c = a + b
                if c in avail:
                    self.results.append((a,b,c))
                avail.append(b)

class row112(row111):
    def __init__ (self,list):
        row111.__init__(self,list)

    def build (self):
        for b in self.list[:]:
            avail = self.list[:]
            avail.remove(b)
            for d in self.list[:]:
                if d not in avail: continue
                avail.remove(d)
                zwStelligList = self.list[:]
                if 0 in zwStelligList: zwStelligList.remove(0)
                for c in zwStelligList:
                    if c not in avail: continue
                    avail.remove(c)
                    a = 10 * c + d - b
                    if a in avail:
                        self.results.append((a,b,10*c+d))

def senkrecht (c1,c2,c3):
    a,b,c = c1
    d,e,f = c2
    i,j,k = c3
    m = (a+d == i)
    n = (b+e == j)
    o = (c+f == k)
    #print '%s %s %s' % (m,n,o)
    return (m and n and o)

def rfl (list,val):
    if val < 10:
        list.remove(val)
    else:
        a,b = divmod(val,10)
        list.remove(a)
        list.remove(b)
    return list

list = range(base)

row1 = row111(list)
print
for i in row1:
    #print
    #print 'row1: %d + %d = %d' % i
    rlist = list[:]
    for r in i:
        rfl(rlist,r)
    #print 'rlist', rlist
    row2 = row112(rlist)
    for j in row2:
        #print 'row2: %d + %d = %d' % j
        slist = rlist[:]
        for s in j:
            rfl(slist,s)
        #print 'slist', slist
        row3 = row112(slist)
        for k in row3:
            if senkrecht(i,j,k):
                print
                print 'row1: %x + %x =  %x' % i
                print 'row2: %x + %x =  %x' % j
                print 'row3: %x + %x = %x' % k
    

