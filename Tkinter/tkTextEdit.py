#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
Beispiel tkTextEdit.py, Seite 319 (Menu)
aus dem Buch Python 2.x von Uzak."""

from Tkinter import *
import tkFileDialog
import tkFont
import sys
from tkMessageBox import showinfo

class tkTextEditor:
    def __init__(self, master):
        self.stumps()
        master.title("tkTextEditor")
        self.master = master
        self.file = None
        self.scrollbar = Scrollbar(master)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text = Text(master, yscrollcommand=self.scrollbar.set,
                                bg="white", font="courier 10")
        self.text.pack()
        self.scrollbar.config(command=self.text.yview)
        self.s = StringVar()
        statusBar = Label(master, textvariable=self.s,
                                      bd=1, relief=SUNKEN, anchor=W)
        statusBar.pack(side=BOTTOM, fill=X)
        menubar = Menu(master)
        self.menubar = menubar
        filemenu = Menu(menubar)
        filemenu.add_command(label="Neu",command=self.newfile)
        filemenu.add_command(label="Öffnen",command=self.openfile)
        filemenu.add_separator()
        filemenu.add_command(label="Speichern",command=self.savefile)
        filemenu.add_command(label="Speichern als",command=self.savefileas)
        filemenu.add_separator()
        filemenu.add_command(label="Beenden",command=self.quit)
        menubar.add_cascade(label="Datei",menu=filemenu)
        menubar.add_command(label="Skript ausführen", command=self.run)
        helpmenu = Menu(menubar)
        helpmenu.add_command(label="Info",command=self.about)
        menubar.add_cascade(label="?",menu=helpmenu)
        master.config(menu=self.menubar)
        master.bind("<Control-d>", self.quit)
        master.bind("<Control-s>", self.savefile)
        master.bind("<Control-o>", self.openfile)
        self.newfile()

    def settitle(self, title):
        self.s.set(title)

    def about(self,):
        showinfo("Info","tkTextEditor für Python 0.1\n\
                                    \n(c)vmi-Buch\nMartin Uzak")

    def newfile(self, event=None):
        self.text.delete(1.0, END)
        self.settitle("*new*")

    def savefile(self, event=None):
        if not self.file:
            self.savefileas()
        if self.file.mode == 'w':
            self.file.write(self.text.get(1.0, END))
            self.file.flush()
        elif self.file.mode == 'r':
            file = self.file.name
            self.file = open(file, 'w')
            self.savefile()

    def savefileas(self,):
        self.file = tkFileDialog.asksaveasfile()
        if self.file:
            self.savefile()
            self.settitle(self.file.name)

    def openfile(self, even=None):
        self.file = tkFileDialog.askopenfile()
        if self.file:
            self.newfile()
            self.text.insert(INSERT,self.file.read())
            self.settitle(self.file.name)

##    def run(self, event=None):
##        thread.start_new_thread(os.system, {("python "+self.file.name),})

    def quit(self, event=None):
        self.master.quit()

    def todo(self):
        print "Funktion muss implementiert werden!"

    def stumps(self):
        #self.savefile = self.todo
        #self.savefileas = self.todo
        #self.openfile = self.todo
        self.run = self.todo
        #self.quit = self.todo
        #self.newfile = self.todo
        #self.about = self.todo

root = Tk()
editor = tkTextEditor(root)
root.mainloop()
