# -*- coding: utf-8 -*-
import sys

__author__ = 'taojun'
import re
from threading import Thread
from datetime import datetime
import os
from Tkinter import *
import tkFileDialog

DEFAULT_DIR = 'D:/TestTools/Logs/'

TASK = 'Task'
COMPLETED = 'Completed'
ERROR = 'ERROR'


class LogCal(Frame):
    def __init__(self, master=None):

        Frame.__init__(self, master)
        self.grid()
        self.master.title("Log Analyzer")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        
        self.root = master
        self.files = []
        self.date = ''
        self.count = 0
        self.error = 0
        self.record = []
        self.date_from = 0
        self.date_to = 0
        self.dt_delta = 0
        self.rps = 0

        self.createWidgets()

    def createWidgets(self):


        self.FROM = Label(self, text='From: ' + str(self.date_from), bg="black", fg="white")
        self.FROM.grid(row = 0, column = 1, rowspan = 3, columnspan = 2, sticky = W+E+N+S)
        self.FROM.pack(fill=BOTH)

        self.To = Label(self, text='To: ' + str(self.date_to), bg="black", fg="white")
        self.To.pack(fill=BOTH)

        self.Error = Label(self, text='Errors number: ' + str(self.error), bg="white", fg="red")
        self.Error.pack(fill=BOTH)

        self.Count = Label(self, text='Completed requests number: ' + str(self.count), bg="red", fg="white")
        self.Count.pack(fill=BOTH)

        self.Seconds = Label(self, text='Total seconds: ' + str(self.dt_delta), bg="red", fg="white")
        self.Seconds.pack(fill=BOTH)

        self.Result = Label(self, text='Request per second: ' + '%.2f' % self.rps + ' r/s', bg="red", fg="white")
        self.Result.pack(fill=BOTH)


        self.Open = Button(self, text='Open', command=self.callback)
        self.Open.pack(side=RIGHT, fill=X)

        self.Run = Button(self, text='Run', command=self.run)
        self.Run.pack(side=RIGHT , fill=X)

        self.listb  = Listbox(self) 
        self.listb.pack(side = RIGHT, fill=BOTH, expand=5)

        self._initListbox()

    def _refreshList(self):

        self.date = ''
        self.count = 0
        self.error = 0
        self.record = []
        self.date_from = 0
        self.date_to = 0
        self.dt_delta = 0
        self.rps = 0
        self._updateFiles()

    def _initListbox(self):
        list_dirs = os.walk(DEFAULT_DIR)
        for root, dirs, files in list_dirs:
            for f in files:
                log = os.path.join(root, f)  
                self.listb.insert(0,log)
                self.files.append(log)

    def refresh(self):

        self.FROM.configure(text='From: ' + str(self.date_from))
        self.To.configure(text='To: ' + str(self.date_to))
        self.Error.configure(text='Errors number: ' + str(self.error))
        self.Count.configure(text='Completed requests number: ' + str(self.count))
        self.Seconds.configure(text='Total seconds: ' + str(self.dt_delta))
        self.Result.configure(text='Request per second: ' + '%.2f' % self.rps + ' r/s')
        self.root.after(1500, self.refresh)

    def _updateFiles(self):
        self.listb.delete(0, END)
        for f in self.files:
            self.listb.insert(0,f)

    def _logCheck(self, rootDir):
        if self.files:
            for f in self.files:
                print f
                self._processLog(f)
        else:
            return False

    def _processLog(self, file):
        try:
            log = open(file, 'r')
            lines = log.readlines()
            for line in lines:
                line = line.split()
                if ERROR in line:
                    self.error = self.error + 1
                elif len(line) > 5:
                    if line[4] and line[5] and TASK in line[4] and COMPLETED in line[5]:
                        self.count = self.count + 1
                        self.date = line[0] + ' ' + line[1]
                        self.record.append({
                            "datetime": datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S,%f")
                        })
        except IOError:
            print('Log File Error!')
            return False
        finally:
            log.close()

    def _rpsCal(self):

        if self.record:
            record = sorted(self.record, key=lambda x: x["datetime"])
            self.date_from = record[0]['datetime']
            self.date_to = record[-1]['datetime']
            self.dt_delta = (self.date_to - self.date_from).total_seconds()
            self.rps = self.count / self.dt_delta
            print
            print('From: ' + str(self.date_from))
            print('To  : ' + str(self.date_to))
            print('Total seconds: ' + str(self.dt_delta) + 's')
            print('Completed requests number: ' + str(self.count))
            print('Errors number: ' + str(self.error))
            print('Request per second: ' + str("%.2f" % self.rps) + 'r/s')

    def _selectFiles(self):

        filez = tkFileDialog.askopenfilenames(parent=self.root, title='Choose a file',initialdir = DEFAULT_DIR)
        self.files = self.root.tk.splitlist(filez)

    def logCheck(self):
        if len(sys.argv) < 1:
            self._logCheck(sys.argv[1])
        else:
            self._logCheck(DEFAULT_DIR)
        self._rpsCal()

    def callback(self):
        self._refreshList()
        self._selectFiles()
        self._updateFiles()

    def run(self):

        self._refreshList()
        self.thread = Thread(target=self.logCheck)
        self.thread.start()
        self.refresh()

    
root = Tk()
app = LogCal(master=root)
app.mainloop()
root.destroy()
