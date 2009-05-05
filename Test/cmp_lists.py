#!/usr/bin/python
"""cmp_lists

Compare two lists and show differences.
Two lists (list_1, list_2) are compared. Elements that differ are then listed.

(c) ah 08/2005
"""

class clist:
    def __init__(self,l1,l2):
        self.full_list_1 = l1[:]
        self.full_list_2 = l2[:]
        self.work_list_1 = l1[:]
        self.work_list_2 = l2[:]
        self.corresponding = []
        self.in1 = []
        self.in2 = []
        self.cmp_l(self.work_list_1,self.work_list_2)

    def cmp_l(self,l1,l2):
        for l in l1:
            if l in l2:
                self.corresponding.append(l)
                l2.remove(l)
            else:
                self.in1.append(l)
        self.in2 = l2
        self.match = (len(self.in1) == 0) and (len(self.in2) == 0)

def p_all(a):
    if a.match:
        print 'lists match exactly'
    else:
        #print 'corresponding:',a.corresponding
        print '%d corresponding elements' % len(a.corresponding)
        print 'solely in l1:'
        for l in a.in1:
            print ' ',l
        print 'solely in l2:'
        for l in a.in2:
            print ' ',l

import sys

def main(l1,l2):
    #l1 = sys.argv[1]
    #l2 = sys.argv[2]
    print 'comparing',l1,'und',l2
    #print type(l1)
    a = clist(l1,l2)
    p_all(a)

if __name__ == '__main__':
    l1 = range(5)
    l2 = range(3,8)
    main(l1,l1)
    main(l1,l2)
