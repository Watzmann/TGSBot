#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Version of SIBS."""

VERSION = '0.7'
VERSION_STRING = 'alpha'
REV = '$Revision$'

class Version:
    
    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    def __init__(self,):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'revisions'):
            self.revisions = {}

    def register(self, module, rev):
        try:
            self.revisions[module] = int(rev.strip('$').split(':')[1].strip())
        except IndexError:
            self.revisions[module] = -1

    def version(self, module=None):
        if module is None:
            max_rev = '6'    #str(max(self.revisions.values()))
            return '%s.%s  %s' % (VERSION, max_rev, VERSION_STRING)
        else:
            revs = self.revisions
            if revs.has_key(module):
                v = '.'.join([VERSION,str(revs[module])])
                return 'module %s: %s' % (module, v)
            else:
                return ''

    def registered_modules(self,):
        return self.revisions.keys()

v = Version()
v.register(__name__, REV)

if __name__ == "__main__":
    print 'module name:', __name__
    print v.version()
    print v.version(1)
    print v.version(__name__)
