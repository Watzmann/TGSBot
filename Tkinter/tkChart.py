#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
Beispiel tkChart.py, Seite 316 (7.8 Beispiele)
aus dem Buch Python 2.x von Uzak."""

from Tkinter import *
from random import randint

class tkChart:
    def __init__(self, master):
        self.master = master
        self.punkte = []
        self.canvas = Canvas(master,width=450,height=450,bg="white")
        self.canvas.pack()
        # X-Achse
        self.canvas.create_line(100,350,400,350,width=1)
        # Y-Achse
        self.canvas.create_line(100,350,100,50,width=1)
        button = Button(master,text="Beenden",command=master.quit)
        button.pack(side=RIGHT)
        button2 = Button(master,text="Neu zeichnen",command=self.repaint)
        button2.pack(side=LEFT)
        self.paint()

    def paint(self,):
        for i in range(11): # Beschriftung X-Achse
            x = 100+(i*30)
            self.canvas.create_line(x,350,x,345,width=1)
            self.canvas.create_text(x,354,text='%d' % (10*i), anchor=N)
        for i in range(11): # Beschriftung Y-Achse
            y = 350-(i*30)
            self.canvas.create_line(100,y,105,y,width=1)
            self.canvas.create_text(96,y,text='%d' % (10*i), anchor=E)
        # 15 Punkte mit Zufallskoordinaten
        data = [([randint(1,100),randint(1,350)]) for a in range(15)]
        #print data
        # Punkte ins Koordinatensystem zeichnen
        for a in range(len(data)):
            x,y = data[a]
            x = 100 + 3*x
            y = 350 - (4*y)/5
            self.punkte.append(self.canvas.create_oval(x-3,y-3,x+3,y+3,
                                    width=1,outline="red",fill="blue"))

    def repaint(self,):
        for a in range(len(self.punkte)):
            self.canvas.delete(self.punkte[a])
        self.paint()

root = Tk()
hello = tkChart(root)
root.mainloop()
