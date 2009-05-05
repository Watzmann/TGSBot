#!/usr/bin/python
# -*- coding: utf-8 -*-
"""entzippt die zip-Files von der DVD 'Website Templates'"""

import sys
from optparse import OptionParser
import os
import zipfile
from stat import S_IWUSR, S_IWGRP

class Unzip:
    def __init__(self, zip_file):
        self.recurse = False
        self.zip = zip_file
        self.extract()
        
    def extract(self):
        # create directory structure to house files
        self._createstructure()

        # extract files to directory structure
        for i, name in enumerate(self.zip.namelist()):

            if not name.endswith('/') and not os.path.exists(name):
                direc = os.path.split(name)[0]
                if direc and not os.path.exists(direc):
                    os.makedirs(direc)
                outfile = file(name, 'wb')
                outfile.write(self.zip.read(name))
                #outfile.flush()
                outfile.close()
                if '.zip' == os.path.splitext(name)[1]:
#                    print '*********************************'
                    self.recurse = True
                    

    def _createstructure(self):
        self._makedirs(self._listdirs())

    def _makedirs(self, directories):
        """ Create any directories that don't currently exist """
        for curdir in directories:
            if not os.path.exists(curdir):
                os.makedirs(curdir)

    def _listdirs(self):
        """ Grabs all the directories in the zip structure
        This is necessary to create the structure before trying
        to extract the file to it. """
        zf = self.zip
        dirs = []

        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name)

        dirs.sort()
        return dirs

def usage(progname):
    usg = """usage: %prog <Pfad zu den Website Templates>
  """ + __doc__ + """

  Beispiel: unzip-websites.exe -v C:\\tmp\\Websitetemplates"""
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="suppress status messages")
    parser.add_option("-f", "--force",
                  action="store_true", dest="force", default=False,
                  help="unzip to existing directory")
    parser.add_option("-r", "--remove",
                  action="store_false", dest="remove", default=False,
                  help="remove zipfile after unzipping")
    return parser

def unzip(zip_file):
    try:
        zf = zipfile.ZipFile(zip_file)
    except:
        print 'Fehler! in', zip_file
        return
    u = Unzip(zf)
    if options.remove:
        print 'removing',zip_file
        os.remove(zip_file)
#    print 'a'*20,u.recurse
    return u.recurse

def find_zips(files):
    return [fn for fn in files if '.zip' == os.path.splitext(fn)[1].lower()]

def handle_zips(zips, root, recursion=False):
#    print 'handle zips in',root,'##',os.getcwd()
    cwd = os.getcwd()
    if root.startswith('.'+os.sep):
        root = root[2:]
    elif root.startswith(cwd):
        root = root[len(cwd)+1:]
#    print 'root has turned to', root
    st = os.stat(root)
    os.chmod(root, st.st_mode | (S_IWUSR + S_IWGRP))
    os.chdir(root)
    new_zip = False
    for count,z in enumerate(zips):
        if options.verbose:
            print os.path.join(root,z)
        if not os.path.exists(z):
            print 'Datei %s nicht gefunden' % os.path.join(root,z)
            sys.exit(1)
        zdir = os.path.splitext(z)[0]
        if not options.force and os.path.exists(zdir):
            if not options.quiet and not recursion:
                print 'Verzeichnis %s existiert bereits' % os.path.join(root,zdir)
            continue
        new_zip = unzip(z)
##        print '#'*20,new_zip
##    print '#'*10,new_zip
    if new_zip:
#        print 'recursion','v'*40
        doit('.',True)
#        print 'recursion','^'*40
    
def doit(path, recursion=False):
    liste = os.walk(path)
    for root,dirs,files in liste:
        #print root,dirs,files
        zips = find_zips(files)
        if len(zips) > 0:
            handle_zips(zips, root, recursion)
    return

if __name__ == "__main__":
    parser = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) < 1:
        print parser.print_usage()
        print "!! Der Pfad zu den Website Templates fehlt."
        sys.exit(1)

    doit(args[0])

