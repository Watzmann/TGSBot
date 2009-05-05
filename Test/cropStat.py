#!/usr/bin/python

def decompose(s):
    all = s.split(' ')
    l = all[1].split(',')
    l += all[-1].split(',')
    return [int(n) for n in l]

def add(a,b):
    s = []
    for n,i in enumerate(a):
        ##print type(i),type(b[n]),
        s.append(i+b[n])
        ##print i,b[n],s[n]
    return s
        
f = open('Java-PT.3/cropped/crop-Log','r')
l = f.readline()
i = 0
S = [0,0,0,0]

while l != '':
    if '::' in l:
        s = decompose(l)
        i+=1    
        #print '%2d: %s' % (i,l),
        S = add(S,s)
        print i,S,divmod(S[0],16)[1],divmod(S[2],16)[1]
    l = f.readline()

print S,i,[s/i for s in S]
