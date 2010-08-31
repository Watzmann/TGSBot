#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Version of SIBS."""

##from sibs_utils import REV
##from persistency import REV
##from sibs_user import REV
##from telnet_server import REV
##from clip import REV
##from command import REV

VERSION = '0.1'
REV = '$Revision$'

class Version:
    
    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    def __init__(self,):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'revisions'):
            self.revisions = {}

    def register(self, module, rev):
        self.revisions[module] = int(rev.strip('$').split(':')[1].strip())

    def version(self, module=None):
        if module is None:
            max_rev = str(max(self.revisions.values()))
            return '.'.join([VERSION,max_rev])
        else:
            revs = self.revisions
            if revs.has_key(module):
                v = '.'.join([VERSION,str(revs[module])])
                return 'module %s: %s' % (module, v)
            else:
                return ''

v = Version()
v.register(__name__, REV)

if __name__ == "__main__":
    print 'module name:', __name__
    print v.version()
    print v.version(1)
    print v.version(__name__)
