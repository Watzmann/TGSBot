#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
Beispiel toplevel.py, Seite 309 (Menu)
aus dem Buch Python 2.x von Uzak."""

from Tkinter import *

class Beispiel:
    def __init__(self, master):
        self.master = master
        self.menubar = Menu(master)
        self.menubar.add_command(label="Press",command=self.doSomething)
        self.menubar.add_command(label="Quit",command=master.quit)
        master.config(menu=self.menubar)
        self.frame = Frame(master,width=300)
        self.frame.pack()

    def doSomething(self):
        Label(self.frame, text="Noch nicht implementiert ;-)").pack()

root = Tk()
bsp = Beispiel(root)
root.mainloop()
