# -*- coding: utf-8 -*-
__author__ = 'taojun'

from threading import Thread,Lock
from datetime import datetime
import os
from Tkinter import *
import tkFileDialog

DEFAULT_DIR = 'D:/TestTools/Logs/'

TASK = 'Task'
COMPLETED = 'Completed'
ERROR = 'ERROR'

class UI(Frame):

    def __init__(self, master=None):

        Frame.__init__(self, master)
        self.root = master

        self.grid()
        self.master.title("Log Analyzer")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self._createWidgets()

    def _createWidgets(self):

        self.FROM = Label(self, text='From: ', bg="black", fg="white")
        self.FROM.grid(row = 0, column = 1, rowspan = 3, columnspan = 2, sticky = W+E+N+S)
        self.FROM.pack(fill=BOTH)

        self.To = Label(self, text='To: ', bg="black", fg="white")
        self.To.pack(fill=BOTH)

        self.Error = Label(self, text='Errors number: ', bg="red", fg="white")
        self.Error.pack(fill=BOTH)

        self.Count = Label(self, text='Completed requests number: ', bg="red", fg="white")
        self.Count.pack(fill=BOTH)

        self.Seconds = Label(self, text='Total seconds: ', bg="red", fg="white")
        self.Seconds.pack(fill=BOTH)

        self.Result = Label(self, text='Request per second: '+ ' r/s', bg="red", fg="white")
        self.Result.pack(fill=BOTH)

        self.Open = Button(self, text='Open')
        self.Open.pack(side=RIGHT, fill=X)

        self.Run = Button(self, text='Run')
        self.Run.pack(side=RIGHT , fill=X)

        self.listb  = Listbox(self)
        self.listb.pack(side = RIGHT, fill=BOTH, expand=5)

class Controller(Thread):

    def __init__(self, lock, view = UI):

        self.lock = lock
        self.view = view

        self.files = []
        self.date = ''
        self.count = 0
        self.error = 0
        self.record = []
        self.date_from = 0
        self.date_to = 0
        self.dt_delta = 0
        self.rps = 0

        self._updateWidgets()
        self._initListbox()

    def _updateWidgets(self):

        self.view.FROM.configure(text='From: ' + str(self.date_from))
        self.view.To.configure(text='To: ' + str(self.date_to))
        self.view.Error.configure(text='Errors number: ' + str(self.error))
        self.view.Count.configure(text='Completed requests number: ' + str(self.count))
        self.view.Seconds.configure(text='Total seconds: ' + str(self.dt_delta))
        self.view.Result.configure(text='Request per second: ' + '%.2f' % self.rps + ' r/s')
        self.view.Open.configure(command=self.callback)
        self.view.Run.configure(command=self.run)

    def _reset(self):

        self._resetList()
        self._updateFiles()

    def _resetList(self):

        self.date = ''
        self.count = 0
        self.error = 0
        self.record = []
        self.date_from = 0
        self.date_to = 0
        self.dt_delta = 0
        self.rps = 0

    def _initListbox(self):

        list_dirs = os.walk(DEFAULT_DIR)
        for root, dirs, files in list_dirs:
            for f in files:
                log = os.path.join(root, f)
                self.view.listb.insert(0,log)
                self.files.append(log)

    def _refresh(self):

        self._updateWidgets()
        self.view.after(1500, self._refresh)

    def _updateFiles(self):

        self.view.listb.delete(0, END)
        for f in self.files:
            self.view.listb.insert(0,f)

    def _onButton(self):

        self.view.Run.configure(stat='active')
        self.view.Open.configure(stat='active')

    def _offButton(self):

        self.view.Run.configure(stat='disable')
        self.view.Open.configure(stat='disable')

    def _processLog(self, file):

        self.lock.acquire()
        self._offButton()

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
            self.lock.release()
            self._onButton()

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

        filez = tkFileDialog.askopenfilenames(parent=self.view.root, title='Choose a file',initialdir = DEFAULT_DIR)
        self.files = self.view.tk.splitlist(filez)

    def _logCheck(self, rootDir=None):

        if self.files:
            for f in self.files:
                print f
                self._processLog(f)
        else:
            return False

    def logCheck(self):

        if len(sys.argv) < 1:
            self._logCheck(sys.argv[1])
        else:
            self._logCheck(DEFAULT_DIR)

        self._rpsCal()

    def callback(self):

        self._reset()
        self._selectFiles()
        self._updateFiles()

    def run(self):

        self._reset()
        self.thread = Thread(target=self.logCheck)
        self.thread.start()
        self._refresh()


root = Tk()
ui = UI(root)
lock = Lock()
app = Controller(lock, view = ui)
app.view.mainloop()