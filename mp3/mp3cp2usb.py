#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automatisierte Übernahme von grip-gerippten mp3-Files auf den USB-Stick.

'grip' benennt (in der gängigen Einstellung) die Dateien zunächst
nur mit dem Namen des Stücks. Der mp3-Player spielt dann aber
alphabetisch ab.
mp3cp2usb.py kopiert einen Folder auf /media/usbdisk/mp3 und benennt
dabei die Dateien um, indem es dem Namen die Nummer des Stückes
aus den Metadaten (TRCK) voranstellt.

(c) Sep 2005, Andreas Hausmann
"""

import sys, os.path, fnmatch, shutil
from tagger import *
from cl import *

_OPTIONS = {
    'help':   {'option':'h','longoption':'help','arg':False,'value':None,
               'action': 'usage',
               'text':"(diese Ausgabe)"},
    'verbose':{'option':'v','longoption':'verbose','arg':False,'value':False,
               'action': 'setTrue',
               'text':None},
    'test':   {'option':'t','longoption':'test','arg':False,'value':False,
               'action': 'setTrue',
               'text':"Testlauf; die Dateien werden nicht kopiert."},
    'liste':  {'option':'l','longoption':'playlist','arg':True,'value':"",
               'action': 'set',
               'text':"erzeuge Playliste (m3u) für xmms. Dateien werden nicht kopiert"},
    'input':  {'option':'i','longoption':'inputpath','arg':True,'value':"./",
               'action': 'set',
               'text':"Pfad, auf den sich die angegebenen Folder/Dateien beziehen."},
    'output': {'option':'o','longoption':'outputpath','arg':True,'value':'/media/usbdisk/mp3',
               'action': 'set',
               'text':["Pfad auf USB-Device.","Default ist /media/usbdisk/mp3"]}
    }

nrFiles = 0
listM3u = {}
write = True

def createFile(name):
    f = file(name,'w')
    f.close()
    
def cp_file(source,dest):
    global nrFiles
    if avOpts.verbose:
        print os.path.basename(source),'-->',os.path.basename(dest)
    try:
        if write and not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))    #Änderung!! mkdir -p
            print 'mkdir',os.path.dirname(dest)
        if avOpts.test:
            createFile(dest)
        elif avOpts.liste:
            pass #print 'Liste',dest
        else:
            shutil.copy(source,dest)
        nrFiles += 1
    except:
        print 'Kann Kopiervorgang nicht durchführen!'
        print source,'-->',dest
    
def dest_file(source):
    #print '###***###',source
    filename = os.path.basename(source)
    outpath = os.path.dirname(os.path.join(avOpts.output,source))
    #print '###***###',outpath
    out = '00-'
    try:
        id3 = ID3v2(os.path.join(avOpts.input,source))
        for frame in id3.frames:
            if frame.fid == 'TRCK':
                out = "%2.2d-" % int(frame.strings[0])
                listM3u[int(frame.strings[0])] = os.path.join(outpath,filename)
                break
    except ID3Exception, e:
        print "%s: ID3v2 exception: %s" % (file,str(e))
    dest = os.path.join(outpath,out+filename)
    #print '###***###',dest
    return dest
    
def do_recurse(fileN):
    inFile = os.path.join(avOpts.input,fileN)
    if os.path.isdir(inFile):
        if avOpts.verbose:
            print inFile,'==>>',os.path.join(avOpts.output,fileN)
        for f in fnmatch.filter(os.listdir(inFile), '*.mp3'):
            do_recurse(os.path.join(fileN, f))
    else:
        dest = dest_file(fileN)
        cp_file(inFile,dest)
        #sys.exit(0)

def testOptions():
    outputpath = avOpts.output
    if write and not os.path.exists(outputpath):
        print write
        print 'Nach %s kann nicht geschrieben werden' % outputpath
        sys.exit(2)
    inputpath = avOpts.input
    if not os.path.exists(inputpath):
        print '%s existiert nicht' % inputpath
        sys.exit(2)

def main():
    global avOpts, nrFiles, write
    avOpts = availableOptions(_OPTIONS)
    cl = commandLine(avOpts, sys.argv[1:])
    #todo
    #cl brauch ich nirgends - hier ist das konzept mit availableOptions noch
    # unausgegoren; es sollte ein Objekt geben (zB optParse)
    if avOpts.verbose:
        print 'Argumente',avOpts.args
        avOpts.optValues(verbose=True)
    if not avOpts.args:         # wenn keine Argumente angegeben wurden
        short_usage(avOpts)     # kommt eine shortusage + Fehlermeldung
        print "Es wurden keine Dateien angegeben!"
        sys.exit(1)
    if avOpts.liste:
        write = False
    testOptions()
    for a in avOpts.args:
        do_recurse(a)
    if avOpts.verbose:
        print 'Es wurden %d Dateien kopiert.' % nrFiles
    if avOpts.liste:
        if avOpts.verbose:
            print 'erzeuge Liste', avOpts.liste
        f = file(avOpts.liste, 'w')
        keys = listM3u.keys()
        keys.sort()
        for i in keys:
            print i, listM3u[i]
            f.write(listM3u[i]+'\n')
        f.close()

def test():
    sys.argv[1:] = './mp3/ha_ich_bins_ich_bins.mp3'
    main()

if __name__ == "__main__":
    main()
