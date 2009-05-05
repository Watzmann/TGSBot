#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test zu TKinter
Python2.x von Uzak: Kapitel 7: Hello World 3"""

from Tkinter import *

class tkHelloWorld:
    def __init__(self, master):
        self.master = master
        self.label = Label(master, text="Hello in Python/Tkinter!")
        self.label.pack()
        self.bild = PhotoImage(file="/var/install/Python-2.3.5/Mac/OSXResources/app/Resources/English.lproj/Documentation/python.gif")
        self.label2 = Label(master, image=self.bild)
        self.label2.pack()
        self.button = Button(master, text="Beenden", command=master.quit)
        self.button.pack()
        return

root=Tk()
hello = tkHelloWorld(root)
root.mainloop()
