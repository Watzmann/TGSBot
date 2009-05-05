#!/usr/bin/python
# -*- coding: utf-8 -*-
"""arbeitet Seiten eines eingescannten Buches einzeln ab,
liefert einzelne gescannte Seiten mit fortlaufendem Namen.
- die Originalseiten bleiben ungeändert;
- die Parameter für ein Buch sind in einem Dict zusammengefasst.
"""
from scannedBook import Page
import glob, os, string
import sys

MYPROG = sys.argv[0]

#------------------------------------------------------Java-PT
Java_PT_rect_links = ((460,-50),(80,40))
Java_PT_rect_rechts = ((460,-50),(80,40))
Java_PT_page_links = (85,150,920,1480)
Java_PT_page_rechts = (1215,154,2050,1484)
Java_PT_frame_links = (50,50,1050,-8)
Java_PT_frame_rechts = (1170,50,-70,-8)
##Java_PT_frame_links = (50,0,1050,-8)     # für scan0045,48,67
##Java_PT_frame_rechts = (1170,0,-70,-8)   # für scan0045,48,67
Java_PT_control_links = ('xmin','ymin')
Java_PT_control_rechts = ('xmin','ymin')
Java_PT = {
    'title':"Java Performance Tuning; O'Reilly",
    'frames':(Java_PT_frame_links,Java_PT_frame_rechts),
    'cropControls': (Java_PT_control_links,Java_PT_control_rechts),
    'rawPages': (Java_PT_page_links,Java_PT_page_rechts),
    'qs_rects':(Java_PT_rect_links,Java_PT_rect_rechts),
    'ext':'bmp',
    'root':'Java_PT',
    'first':1,
    'numbering':{'offset':4,
                 'length':4,
                 'correct':(2,-3)},
    'margin':(45,45)                        # Margin in pixels
    }
#------------------------------------------------------Python2.x
Python2x_rect_links = ((96,-165),(90,110))  # Position der Seitenzahl
Python2x_rect_rechts = ((1360,-160),(89,110)) # zur QS  (center-xy,dimensions/2-xy)
Python2x_page_links = (300,200,1640,2270)   # Die Dimensionen der linken
Python2x_page_rechts = (1890,200,3250,2270) #   und rechten Seite
Python2x_search_links = (200,100,1740,2370) # Die Start-Frames links
Python2x_search_rechts = (1790,80,3350,2380) #  und rechts
Python2x_control_links = ('xmin','ymax')    # Die zu suchenden Kanten links
Python2x_control_rechts = ('xmax','ymax')   #   und rechts
Python2x = {
    'title':"Python 2.x; bhv",
    'frames':(Python2x_search_links,Python2x_search_rechts),
    'rawPages': (Python2x_page_links,Python2x_page_rechts),
    'qs_rects':(Python2x_rect_links,Python2x_rect_rechts),
    'cropControls': (Python2x_control_links,Python2x_control_rechts),
    'ext':'tif',                            # die Extension von Original und Schnitt
    'root':'Python2x',                      # Basisname für Schnitte
    'first':214,                            # Seitenzahlen starten hier
    'numbering':{'offset':18,               # Regeln für das Berechnen der
                 'length':3,                #   Seitenzahlen aus dem 
                 'correct':(1,0)},          #   OriginalfileNamen
    'margin':(90,90)                        # Margin in pixels
    }
#------------------------------------------------------TeachingYourselfPython
TYP_rect_links = ((75,-55),(35,20))    # Position der Seitenzahl
TYP_rect_rechts = ((36+45,-21-45),(35,20))  # zur QS  (center-xy,dimensions/2-xy)
TYP_page_links = (340,105,1160,1295)   # Die Dimensionen der linken
TYP_page_rechts = (340,105,1160,1295)  #   und rechten Seite
TYP_search_links = (100,390,1000,1670) # Die Start-Frames links
TYP_search_rechts = (290,40,1185,1325) #  und rechts
TYP_control_links = ('xmax','ymax')    # Die zu suchenden Kanten links
TYP_control_rechts = ('xmin','ymax')   #   und rechts
TYP_rechts = {
    'title':"Teaching Yourself Python; Markt und Technik",
    'ext':'bmp',                       # die Extension von Original und Schnitt
    'root':'TYP',                      # Basisname für Schnitte
    'first':0,                         # Seitenzahlen starten hier
    'numbering':None,                  #   OriginalfileNamen beibehalten
    'margin':(45,45),                  # Margin in pixels
    'frames':(None,TYP_search_rechts),
    'rawPages': (None,TYP_page_rechts),
    'qs_rects':(None,TYP_rect_rechts),
    'cropControls': (None,TYP_control_rechts),
    }
TYP_links = {
    'title':"Teaching Yourself Python; Markt und Technik",
    'ext':'bmp',                       # die Extension von Original und Schnitt
    'root':'TYP',                      # Basisname für Schnitte
    'first':0,                         # Seitenzahlen starten hier
    'numbering':None,                  #   OriginalfileNamen beibehalten
    'margin':(45,45),                  # Margin in pixels
    'frames':(TYP_search_links,None),
    'rawPages': (TYP_page_links,None),
    'qs_rects':(TYP_rect_links,None),
    'cropControls': (TYP_control_links,None),
    }
#------------------------------------------------------BeraterGuide04
BeraterGuide_rect_0 = ((130,-50),(80,40))
BeraterGuide_rect_1 = ((-115,-45),(80,40))
BeraterGuide_frame_0 = (175,425,1380,2280)
BeraterGuide_frame_1 = (420,20,1680,1890)


# ----------------------------------------------------------------------------
# HIER DAS BUCH EINSTELLEN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# set BOOK (Dict) Das ist das einzige, was gesetzt werden muss.
# Der Rest sollte von alleine laufen

book = TYP_links

# ----------------------------------------------------------------------------
# der restliche Code muss nicht mehr konfiguriert werden

def makeTmpDir(name):
    path = name
    if not os.path.exists(path):
        print "%s: creating directory '%s'" % (MYPROG,path)
        os.mkdir(path)
    return path

class Filename:
    """liefert fortlaufende Filenamen (.next()) nach einem Schema"""
    fmt = '%s%04d.%s'
    def __init__(self,root,ext,first,rules,format=''):
        self.root = root
        self.ext = ext
        self.cur = first
        self.rules = rules
        if format: self.fmt = format
    def next(self,):
        if self.rules is None:
            name = self.name
        else:
            name = self.fmt % (self.root,self.cur,self.ext)
            self.cur += 1
        return name
    def resetFromRules(self,name):
        if self.rules is None:
            self.name = name
            return self.name
        offset = self.rules['offset']
        length = self.rules['length']
        fac,step = self.rules['correct']
        n = int(name[offset:offset+length])
        self.cur = n * fac + step
        return self.cur

class qsConf:

    valid = True

    def __init__(self,rect,dir):
        if rect is None:
            self.valid = False
            return
        center,dims = rect
        #print 'in qsConf.__init__:' ,center,dims
        self.box = self.qsBox(center,dims)
        self.dir = makeTmpDir(dir)
        #print 'in qsConf.__init__: %s %s'% (dir,self.dir)

    def qsBox (self,center,dims):
        xmin = center[0] - dims[0]
        xmax = center[0] + dims[0]
        ymin = center[1] - dims[1]
        ymax = center[1] + dims[1]      #pruefen, ob das positiv werden kann!!
        return (xmin,ymin,xmax,ymax)

    def getBox (self):
        #print 'getBox:', self.box
        return self.box

    def getDir (self):
        return self.dir

    def info (self):
        if self.valid:
            print 'info qsConf: %d,%d %d,%d   -> %s' % \
                            (self.getBox() + (self.getDir(),))

class dirSetup:

    def __init__(self,source,dest):
        self.src = source
        self.dst = makeTmpDir(dest)

    def getSource (self):
        return self.src

    def getDest (self):
        return self.dst

    def info (self):
        print 'info dirSetup: %s -> %s' % (self.getSource(),self.getDest())

class ProcSP:           # prepSP: process Scanned Pages

    def __init__(self,filename,dirs,qs=None):
        self.file = filename
        self.source = filename
        self.dirs = dirs
        self.page = Page(self.source)
        print self.page.info()+',,',
        self.fullPage = self.page.getImg()

    def cropAndFlush (self,frames=((0,0,0,0),),margin=None):
        page = self.page
        if margin:
            x,y = margin
            page.setMargin(x,y)
        fname.resetFromRules(self.file)
        for frame,raw,crop,qs in zip(frames,rawPages,cropControls,qsRects):
            #print frame          # Original wird für jede Seite neu geladen
            if frame is None:
                continue
            page.setImg(self.fullPage)
            page.setCropControl(crop)
            page.setRawPage(raw)
            im = page.simpleCrop(frame)
            print self.printLog(self.page.log['listo'])+',,',
            im = page.crop()
            page.setImg(im)
            self.file = fname.next()
            dest = os.path.join(self.dirs.getDest(),self.file)
            page.flush(dest)
            self.qsPageNumbers(qs)
        print
    
    def qsPageNumbers (self,qs):
        #print '#####',qs.getBox()
        im = self.page.qsCrop(qs.getBox())
        self.page.setImg(im)
        #page.info()
        dest = os.path.join(qs.getDir(),self.file)
        dest = string.join(dest.split('.')[:-1])+'.pbm'
        self.page.flush(dest,'PPM')
        return
    
    def printLog(self,l):
        """unterstützt die Ausgabe in eine csv-Datei"""
        s = l[0]
        for i in l[1:]:
            s += ',,' + i
        return s


# -------------------------------------------

print book['title']

# set QS
qsl,qsr = book['qs_rects']
qsRects = (qsConf(qsl,'qs'),qsConf(qsr,'qs'))
qsRects[0].info()
qsRects[1].info()

# set DIRS
dirs = dirSetup('.','cropped')
dirs.info()

# set FRAMES
frames = book['frames']
rawPages = book['rawPages']
cropControls = book['cropControls']
print frames

pics = glob.glob('*.'+book['ext'])
fname = Filename(book['root'],book['ext'],book['first'],book['numbering'])
margin = book['margin']
print Page.log['listo_head']

for p in pics:
    sp = ProcSP(p,dirs)
    sp.cropAndFlush(frames,margin)
    #break
    
