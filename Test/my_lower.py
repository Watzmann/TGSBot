# -*- coding: utf-8 -*-

umlaute = ((u'Ä', u'ä'), (u'Ö', u'ö'), (u'Ü', u'ü'))

def my_lower(string):
    low = string.lower().decode('latin-1')
    ret = list(low)
    for s,t in umlaute:
        while s in ret:
            idx = ret.index(s)
            ret[idx] = t
    return ''.join(ret)

examples = (
    'Böse',
    'Bärtig',
    'Büste',
    'ÖSTLICH',
    'ÜBEL',
    'ÄRGER',
    )

if __name__ == '__main__':
    for s in examples:
        r = s.decode('utf-8').encode('latin-1')
        print s, '->', my_lower(r)
    f = open('/home/andreas/test.encoding')
    string = f.readline()
    f.close()
    print string.decode('latin-1'), '->', my_lower(string)
