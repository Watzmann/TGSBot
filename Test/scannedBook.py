#!/usr/bin/python
# -*- coding: utf-8 -*-

import Image
import ImageDraw
import sys

class Box:
    """rechteckiges Objekt mit (xmin,ymin,xmax,ymax)"""
    def __init__(self,coord):
        """coord ist Tupel mit 4 Elementen"""
        self.coords = coord
        self.xmin,self.ymin,self.xmax,self.ymax = coord
        return
    def copy(self,):
        """return a copy of Box"""
        return Box(self.coordinates())
    def addMargin(self,xdim,ydim):
        """add a margin of Dimensions xdim,ydim in place;
box borders are kept in order"""
        xmin = self.xmin - xdim
        xmax = self.xmax + xdim
        if xmin > xmax: xmin,xmax = xmax,xmin
        ymin = self.ymin - ydim
        ymax = self.ymax + ydim
        if ymin > ymax: ymin,ymax = ymax,ymin
        self.setCoordinates(xmin,ymin,xmax,ymax)
        return
    def crop(self,limits):
        """crop box to the limiting box 'limits' in place"""
        xmin = max(self.xmin,limits.xmin)
        xmax = min(self.xmax,limits.xmax)
        ymin = max(self.ymin,limits.ymin)
        ymax = min(self.ymax,limits.ymax)
        self.setCoordinates(xmin,ymin,xmax,ymax)
        return self
    def xdim(self,):
        return self.xmax-self.xmin
    def ydim(self,):
        return self.ymax-self.ymin
    def dimensions(self,):
        return self.xdim(),self.ydim()
    def setCoordinates(self,xmin,ymin,xmax,ymax):
        self.coords = (xmin,ymin,xmax,ymax)
        self.xmin,self.ymin,self.xmax,self.ymax = self.coords
        return
    def coordinates(self,):
        return self.coords
    def name(self,name):
        self.boxName = name
    def __str__(self,):
        name = getattr(self,'boxName','')
        if name:
            name = "'%s': " % (name,)
        return '%s%d,%d %d,%d' % ((name,)+self.coordinates())
    def __eq__(self,box):
        b1,b2,b3,b4 = box.coordinates()
        c1,c2,c3,c4 = self.coordinates()
        if b1 != c1: return False
        if b2 != c2: return False
        if b3 != c3: return False
        if b4 != c4: return False
        return True            
    def __ne__(self,box):
        b1,b2,b3,b4 = self.box()
        c1,c2,c3,c4 = self.coordinates()
        if b1 != c1: return True
        if b2 != c2: return True
        if b3 != c3: return True
        if b4 != c4: return True
        return False            
    
class Page:
    minormax = {-1:'max',1:'min'}
    upperThresh = .95        # Unterschreiten heißt Schrift o.Ä.
    lowerThresh = .005       # Unterschreiten heißt leer oder
    hitThresh = 3            #   leichte Verschmutzung (schwarz=0)
    log = {}
    log['listo_head']='xstart,xstop,xstep,dim,hit,xret,s/255,yall,yall-s/255,LowerThresh,UpperThresh'
    def __init__(self,fn):
        self.image = Image.open(fn)
        im = self.image
        self.outname = im.filename
        self.outformat = im.format
        self.X,self.Y = im.size
        self.format = im.format
        self.innerBoundsReach = -200
        self.fullPage = Box((0,0,self.X,self.Y))
        self.rawPage = None
        self.writtenPage = None
        self.margin = (90,90) #45
        self.marginPage = None
        return

    def setMargin(self,xMarg,yMarg):
        self.margin = (xMarg,yMarg)
        return

    def pageWithMargin(self,box):
        xdim,ydim = self.margin
        mb = box.copy()
        mb.addMargin(xdim,ydim)
        mb.crop(self.fullPage)
        return mb
    
    def setThresholdValues(self,lower,upper):
        self.lowerThresh = lower
        self.upperThresh = upper

    def setThresholds(self,box):
        X = box.xmax - box.xmin
        Y = box.ymax - box.ymin
        self.XloThr = X * self.lowerThresh
        self.XupThr = X * self.upperThresh
        self.YloThr = Y * self.lowerThresh
        self.YupThr = Y * self.upperThresh
##        print 'Thresholds: %d %d %d %d' % (self.XloThr,self.XupThr,self.YloThr,self.YupThr)
##        print 'in Zahlen :) %.3f %.3f' % (self.lowerThresh,self.upperThresh)
        return
    
    def getLowerThresh (self,dim):
        if dim == 'x':
            ret = self.YloThr
        else:
            ret = self.XloThr
        return ret

    def getUpperThresh (self,dim):
        if dim == 'x':
            ret = self.YupThr
        else:
            ret = self.XupThr
        return ret

    def hitWritten (self,count,dim):
        """ist wahr, wenn count zwischen lower und upper thresh liegt"""
        hit = (count >= self.getLowerThresh(dim)) and (count <= self.getUpperThresh(dim))
        return hit

    def relCoord(self,n,a,A):
        if n == 0:
            return a
        if n > 0:
            return n
        else:
            return max((0,A+n))

    def qsCrop(self,qsBox):
        xmin = self.relCoord(qsBox[0],0,self.X)
        xmax = self.relCoord(qsBox[2],self.X-1,self.X)
        ymin = self.relCoord(qsBox[1],0,self.Y)
        ymax = self.relCoord(qsBox[3],self.Y-1,self.Y)
        box = (xmin,ymin,xmax,ymax)
        #print 'qsCrop box:',box
        ret = self.image.crop(box)
        return ret

    def setRawPage(self,raw):
        """zusammen mit cropControl wird erreicht, dass nur 2 Seiten gesucht werden
müssen und der Rest berechnet werden kann"""
        self.rawPage = Box(raw)
        
    def setCropControl(self,control):
        """cropControl (z.B. ('xmin','ymin')) dient simpleCrop zur Vereinfachung;
es werden nur 2 Schnitte gesucht; es werden die Schnitte mit der höheren
Genauigkeit gewählt, die anderen Kanten kommen aus den Dimensionen der
Seiten (Vorgabe)"""
        self.cropControl = control

    def simpleCrop(self,frame=(0,0,-1,-1)):
        """führt den eigentlichen Schnitt durch;
frame ist der Startrahmen für die Suche nach dem Satzspiegel; innerBounds
sind (derzeit) fest in Page konfiguriert. Jede Schnittlinie wird durch
listo() gesucht, aus den Koordinaten wird die Box writtenPage (Satzspiegel)
gebaut.
Die Box writtenPage wird zurückgegeben, um eventuell ge'print'et zu werden.
"""
        startCoord = (self.relCoord(frame[0],0,self.X),
                      self.relCoord(frame[1],0,self.Y),
                      self.relCoord(frame[2],self.X-1,self.X),
                      self.relCoord(frame[3],self.Y-1,self.Y))
        start = Box(startCoord)
        start.name('start Box')
        ib = start.copy()    # inner Bounds
        ib.name('inner Bounds')
        ib.addMargin(self.innerBoundsReach,self.innerBoundsReach)
##        print start
##        print ib
        self.log['listo'] = []
        self.setThresholds(start)
        res = {}
        # das kann noch schöner werden ;)
        # erst werden die Schnitte (laut cropControl) gesucht
        if 'xmin' in self.cropControl:
            res['xmin'] = self.listo(start.xmin,ib.xmin,1,
                                             start.ymin,start.ymax,'x')
        if 'xmax' in self.cropControl:
            res['xmax'] = self.listo(start.xmax,ib.xmax,-1,
                                             start.ymin,start.ymax,'x')
        if 'ymin' in self.cropControl:
            res['ymin'] = self.listo(start.ymin,ib.ymin,1,
                                             start.xmin,start.xmax,'y')
        if 'ymax' in self.cropControl:
            res['ymax'] = self.listo(start.ymax,ib.ymax,-1,
                                             start.xmin,start.xmax,'y')
        # dann werden die verbleibenden Schnitte mit den bekannten
        #   Dimensionen der Seite berechnet
        xdim,ydim = self.rawPage.dimensions()
        if 'xmin' not in self.cropControl:
            res['xmin'] = res['xmax'] - xdim
        if 'xmax' not in self.cropControl:
            res['xmax'] = res['xmin'] + xdim
        if 'ymin' not in self.cropControl:
            res['ymin'] = res['ymax'] - ydim
        if 'ymax' not in self.cropControl:
            res['ymax'] = res['ymin'] + ydim
        self.writtenPage = Box((res['xmin'],res['ymin'],
                                res['xmax'],res['ymax']))
        self.writtenPage.name('written Page')
        #print self.writtenPage
        self.marginPage = self.pageWithMargin(self.writtenPage)
        return self.writtenPage

    def listo (self,xstart,xstop,xstep,ymin,ymax,dim):
        # listo comes from 'Little Histo'
        """gibt den linken/rechten Rand der beschriebenen Seite zurück (für dim='x');
entsprechend den oberen/unteren (für dim='y');"""
        #print 'listo:',xstart,xstop,xstep,ymin,ymax,dim
        xret = xstart
        yall = ymax + 1 - ymin
        hit = 0
        for x in range (xstart,xstop,xstep):
            s = 0
# den folgenden if-else-Teil kann man wahrscheinlich beschleunigen durch:
#   Histogramm und nach Summe von 0,255 schauen
            if dim == 'x':
                for y in range(ymin,ymax+1):
                    s += self.image.getpixel((x,y))
            else:
                for y in range(ymin,ymax+1):
                    s += self.image.getpixel((y,x))
            if self.hitWritten(yall-s/255,dim):
                                  # s/255 korrigiert die Pixelfarbe 'weiß'
                hit += 1
##                print 'scanning [%d,%d] in %s: %dx %d %d/%d >%d< [%d,%d]' % \
##                            (xstart,xstop,dim,hit,x,s/255,yall,yall-s/255,
##                                        int(self.getLowerThresh(dim)),
##                                         int(self.getUpperThresh(dim)))
                if hit >= self.hitThresh:
                    xret = x - hit*xstep
                    break
            else:
                hit = max(0,hit-1)
        log = '%d,%d,%d,%s,%d,%d,%d,%d,%d,%d,%d' % \
                (xstart,xstop,xstep,dim,hit,xret,s/255,yall,yall-s/255,
                int(self.getLowerThresh(dim)),int(self.getUpperThresh(dim)))
        self.log['listo'].append(log)
        return xret

    def showBox(self,box,fullImage=None):
        """Zeichnet die Seite mit der gewünschten Box;
ist fullImage != None, so werden die Linien durchgezogen."""
        xmin,ymin,xmax,ymax = box.xmin,box.ymin,box.xmax,box.ymax
        if fullImage:
            Xmin,Xmax = fullImage.xmin,fullImage.xmax
            Ymin,Ymax = fullImage.ymin,fullImage.ymax
        else:
            Xmin,Xmax,Ymin,Ymax = box.xmin,box.xmax,box.ymin,box.ymax
        draw = ImageDraw.Draw(self.image)
        # vertical lines
        draw.line((xmin,Ymin)+(xmin,Ymax),fill=0)
        draw.line((xmin+1,Ymin)+(xmin+1,Ymax),fill=0)
        draw.line((xmax,Ymin)+(xmax,Ymax),fill=0)
        draw.line((xmax-1,Ymin)+(xmax-1,Ymax),fill=0)
        # horizontal lines        
        draw.line((Xmin,ymin)+(Xmax,ymin),fill=0)
        draw.line((Xmin,ymin+1)+(Xmax,ymin+1),fill=0)
        draw.line((Xmin,ymax)+(Xmax,ymax),fill=0)
        draw.line((Xmin,ymax-1)+(Xmax,ymax-1),fill=0)

    def show(self,):
        self.image.show()

    def crop(self,box=None):
        """crop image to box-Dimensions (default self.margin/writtenPage)"""
        if not box:
            if not self.marginPage is None:
                box = self.marginPage
            elif not self.writtenPage is None:
                box = self.writtenPage
            else:
                return None
        return self.image.crop(box.coordinates())

    def setImg (self,img):
        self.image = img
        self.X,self.Y = img.size
        self.xmin,self.xmax = 200,self.X-200
        self.ymin,self.ymax = 200,self.Y-200

    def getImg (self):
        return self.image

    def info(self,):
        fname = getattr(self.image,'filename','cropped')
        return '%s,%d,%d' % ((fname,)+self.image.size)

    def flush(self,name='',format=''):
        """schreibt das derzeitige Bild in Datei <name>"""
        # ist self.outname eigentlich gesetzt?????????
        # muss eventuell name gesetzt sein??????
        # das ist noch nicht befriedigend gelöst
        if len(name) > 0:
            self.outname = name
        if len(format) > 0:
            self.outformat = format
        self.image.save(self.outname,self.outformat)
        self.log['flush'] = '-> %s: %d,%d' % ((self.outname,)+self.image.size)
        return

def string2tuple(string,fun=int):
    """macht aus einer string-Eingabe ein Frame-Tupel"""
    #print frame
    a = string.strip('()').split(',')
    return tuple([fun(i) for i in a])

def testBox():
    """test-Routine für Klasse Box"""
    success = True
    try:
        box = Box((10,10,50,50))
        box.name('test-box')
        print 'testing with',box
        test = "box selber"
        assert box.coordinates() == (10,10,50,50)
        cbox = box.copy()
        test = "box.copy()"
        assert cbox == box
        test = "box.coordinates()"
        assert cbox.coordinates() == box.coordinates()
        test = "box.crop()"
        cr = Box((5,5,45,45))
        assert cbox.crop(cr).coordinates() == (10,10,45,45)
    except AssertionError:
        print "Fuck this shit!",test
        success = False
    return success

if __name__ == '__main__':
    if not testBox():       # kleiner eingebauter Test
        sys.exit(1)
    filename = sys.argv[1]
    try:
        page=Page(filename) # Seite anlegen
    except:
        print "Can't find", file
        sys.exit(2)
    if len(sys.argv) > 2:   # if given: start frame for scanning
        frame = string2tuple(sys.argv[2])
    else:
        frame = (0,0,0,0)
    if len(sys.argv) > 3:   # if given: thresholds (lower,upper)
        l,u = string2tuple(sys.argv[3],float)
        page.setThresholdValues(l,u)
    print page.info(),
    page.setCropControl(('xmin','ymax'))
    page.setRawPage((300,200,1640,2270))
    img = page.simpleCrop(frame)
    print img,page.log['listo']
    if True:
        page.showBox(page.writtenPage,fullImage=page.fullPage)
        page.showBox(page.marginPage)
        page.show()
    if True:
        img = page.crop()
        page.setImg(img)
        print '  ::  ',page.info(),
        page.flush('testbild.bmp')
    else:
        print

