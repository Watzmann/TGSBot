#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
Beispie tkFly.py, Seite 304
aus dem Buch Python 2.x von Uzak."""

from Tkinter import *
import random, thread, time

class tkFly:
    def __init__(self, master):
        self.master = master
        self.canvas = Canvas(master,width=450,
                             height=450,bg="white")
        self.canvas.pack()
        img = '/home/hausmann.remote/Bilder/AHa.Doc/STE/STE-Logo-198x121.gif'
        self.photo = PhotoImage(file=img)
        self.canvas.create_image(225,210,anchor=CENTER,image=self.photo)
        self.canvas.create_text(225,20,text="Das ist Python")
        self.c1 = self.canvas.create_rectangle(2,2,20,20,fill="red")
        self.c2 = self.canvas.create_oval(2,2,20,20,fill="blue")
        self.button = Button(master,text="Beenden",command=self.master.quit)
        self.button.pack()
        thread.start_new_thread(self.run,())

    def run(self):
        while 1:
            time.sleep(.05)
            for a in "c1","c2":
                x = random.randint(1,400)
                y = random.randint(1,280)
                self.canvas.coords(eval("self."+a),x,y,x+20,y+20)

root = Tk()
hello = tkFly(root)
root.mainloop()
