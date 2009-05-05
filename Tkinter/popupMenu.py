#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
Beispiel pulldown.py, Seite 310 (Menu)
aus dem Buch Python 2.x von Uzak."""

from Tkinter import *

def none():
    print "Funktion muss implementiert werden!"

def popup(event):
    menu.post(event.x_root, event.y_root)

root = Tk()
menu = Menu(root) #,tearoff=0)
menu.add_command(label="Kopieren",command=none)
menu.add_command(label="Ausschneiden",command=none)
menu.add_command(label="Einfügen",command=none)
text=Text(root)
text.pack()
text.bind("<Button-3>",popup)
root.mainloop()
