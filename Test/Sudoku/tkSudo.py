#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
Beispiel tkChart.py, Seite 316 (7.8 Beispiele)
aus dem Buch Python 2.x von Uzak."""

from Tkinter import *
from random import randint

class sudokuChart:

    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.old_data = self.game.list_dump()
        self.punkte = []
        self.canvas = Canvas(master,width=450,height=450,bg="white")
        self.canvas.pack()
        self.generate_coord()
        self.grid()
        button = Button(master,text="Beenden",command=master.quit)
        button.pack(side=RIGHT)
        button2 = Button(master,text="Schritt",command=self.repaint)
        button2.pack(side=LEFT)
        self.paint()

    def generate_coord(self,):
        """Create coordinates for all elements in 9x9 grid.
Coordinates are to be kept in this central code to make changes easier.
Coordinates are queried by coord(x,y,kind)"""
        coord = {}
        # the lines in x and y direction
        r = {}
        c = {}
        step = 30
        start = (450 - 9*step)/2
        s = range(start, start+9*step+1, step)
        r['x'] = s
        r['y'] = s
        s = range(start+step/2, start+9*step, step)
        c['x'] = s
        c['y'] = s
        coord['line'] = r
        # the width information
        r = {}
        w = (3,1,1,3,1,1,3,1,1,3)
        r['x'] = w
        r['y'] = w
        coord['width'] = r
        # the central points of the boxes
        coord['center'] = c        
        self.coordinates = coord
        
    def coord(self, x, y, kind):
        if x is not None:
            x_ret = self.coordinates[kind]['x'][x]
        else:
            x_ret = None
        if y is not None:
            y_ret = self.coordinates[kind]['y'][y]
        else:
            y_ret = None
        return x_ret,y_ret

    def full_set_of_coordinates(self):
        return [(a,b) for b in range(9) for a in range(9)]

    def full_set_of_xy_coordinates(self):
        return [self.coord(a[0],a[1],'center') \
                        for a in self.full_set_of_coordinates()]
    
    def grid(self,):
        # Y-Richtung
        step = 30
        start = 100
        y_range = range(start,start+9*step+1,step)
        start = 49
        x_range = range(start+9*step+1,start,-step)
        width = (3,1,1,3,1,1,3,1,1,3)
        # X-Achse
        x,y1 = self.coord(None,0,'line')
        x,y2 = self.coord(None,9,'line')
        for x in range(10):
            # x und y scheinen hier noch vertauscht; das kommt von tkChart.py
            x1,y = self.coord(x,None,'line')
            w,y = self.coord(x,None,'width')
            self.canvas.create_line(y1-1,x1,y2+2,x1,width=w)
        # Y-Achse
##        w = iter(width)
##        for y in y_range:
##            self.canvas.create_line(y,x_range[0],y,50,width=w.next())
        x1,y = self.coord(0,None,'line')
        x2,y = self.coord(9,None,'line')
        for y in range(10):
            # x und y scheinen hier noch vertauscht; das kommt von tkChart.py
            x,y1 = self.coord(None,y,'line')
            x,w = self.coord(None,y,'width')
            self.canvas.create_line(y1,x1,y1,x2,width=w)


    def paint(self,):
        ok = self.game.check()
        if not ok:
            self.game.print_log()
        coord = self.full_set_of_xy_coordinates()
        new_data = self.game.list_dump()
        data = new_data[:]
        for e,i in enumerate(self.old_data):
            if ' ' <> i:
                data[e] = ' '
        nr_data = [([self.old_data[a], coord[a][0], coord[a][1],'blue']) for a in range(81)]
        for e,a in enumerate(data):
            if ' ' == a:
                continue
            nr_data[e] = (a, coord[e][0], coord[e][1], 'red')
        self.old_data = new_data
        #print data
        # Zahlen ins Netz zeichnen
##        for a in range(9):
##            for b in range(9):
##                x,y = self.coord(a,b,'center')
##                self.canvas.create_oval(x-3,y-3,x+3,y+3,
##                                    width=1,outline="red",fill="blue")
        for a in range(len(data)):
            z,x,y,c = nr_data[a]
            #x = 100 + 3*x
            #y = 350 - (4*y)/5
            self.punkte.append(self.canvas.create_text(x,y,
                            text=str(z),width=1,fill=c))

    def repaint(self,):
        self.game.next()
        for a in range(len(self.punkte)):
            self.canvas.delete(self.punkte[a])
        self.paint()

if __name__ == '__main__':
    root = Tk()
    hello = sudokuChart(root)
    root.mainloop()
