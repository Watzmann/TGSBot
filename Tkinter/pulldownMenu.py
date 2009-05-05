#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
Beispiel pulldown.py, Seite 310 (Menu)
aus dem Buch Python 2.x von Uzak."""

from Tkinter import *

class tkTextEditor:
    def __init__(self, master):
        self.master = master
        self.scrollbar = Scrollbar(master)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text = Text(master, yscrollcommand=self.scrollbar.set)
        self.text.pack()
        menubar = Menu(master)
        self.menubar = menubar
        filemenu = Menu(menubar)
        filemenu.add_command(label="Neu",command=self.todo)
        filemenu.add_command(label="Öffnen",command=self.todo)
        filemenu.add_separator()
        filemenu.add_command(label="Speichern",command=self.todo)
        filemenu.add_command(label="Speichern als",command=self.todo)
        filemenu.add_separator()
        filemenu.add_command(label="Beenden",command=self.todo)
        menubar.add_cascade(label="Datei",menu=filemenu)
        helpmenu = Menu(menubar)
        helpmenu.add_command(label="Info",command=self.todo)
        menubar.add_cascade(label="?",menu=helpmenu)
        master.config(menu=self.menubar)

    def todo(self):
        print "Funktion muss implementiert werden!"

root = Tk()
editor = tkTextEditor(root)
root.mainloop()
