# -*- coding: utf-8 -*-
import sys

__author__ = 'taojun'
import re
from threading import Thread
from datetime import datetime
import os
from Tkinter import *

logs_path = '/TestTools/Logs/'


class LogCal(Frame):
    def __init__(self, master=None):

        Frame.__init__(self, master)

        self.pack()
        self.root = master
        self.date = ''
        self.count = 0
        self.record = []
        self.date_from = 0
        self.date_to = 0
        self.dt_delta = 0
        self.rps = 0

        self.run()

    def createWidgets(self):

        self.FROM = Label(self, text='From: ' + str(self.date_from), bg="white", fg="black")
        self.FROM.pack(fill=X)

        self.To = Label(self, text='To: ' + str(self.date_to), bg="white", fg="black")
        self.To.pack(fill=X)

        self.Count = Label(self, text='Total request number: ' + str(self.count), bg="red", fg="white")
        self.Count.pack(fill=X)

        self.Seconds = Label(self, text='Total seconds: ' + str(self.dt_delta), bg="red", fg="white")
        self.Seconds.pack(fill=X)

        self.Result = Label(self, text='Request per second: ' + '%.2f' % self.rps + ' r/s', bg="red", fg="white")
        self.Result.pack(fill=X)

    def refresh(self):
        self.FROM.configure(text='From: ' + str(self.date_from))
        self.To.configure(text='To: ' + str(self.date_to))
        self.Seconds.configure(text='Total request number: ' + str(self.count))
        self.Count.configure(text='Total seconds: ' + str(self.dt_delta))
        self.Result.configure(text='Request per second: ' + '%.2f' % self.rps + ' r/s')
        self.root.after(1500, self.refresh)

    def _logCheck(self, rootDir):

        TASK = 'Task'
        COMPLETED = 'Completed'

        list_dirs = os.walk(rootDir)
        for root, dirs, files in list_dirs:
            for f in files:
                log_file = os.path.join(root, f)
                print(log_file)
                try:
                    log = open(log_file, 'r')
                    lines = log.readlines()
                    for line in lines:
                        line = line.split()
                        if len(line) > 5:
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

        record = sorted(self.record, key=lambda x: x["datetime"])
        self.date_from = record[0]['datetime']
        self.date_to = record[-1]['datetime']
        self.dt_delta = (self.date_to - self.date_from).total_seconds()
        self.rps = self.count / self.dt_delta
        print
        print('From: ' + str(self.date_from))
        print('To  : ' + str(self.date_to))
        print('Total seconds: ' + str(self.dt_delta) + 's')
        print('Total request number: ' + str(self.count))
        print('Request per second: ' + str("%.2f" % self.rps) + 'r/s')

    def logCheck(self):
        if len(sys.argv) < 1:
            self._logCheck(sys.argv[1])
        else:
            self._logCheck(logs_path)
        self._rpsCal()

    def run(self):

        self.thread = Thread(target=self.logCheck)
        self.thread.start()
        self.createWidgets()
        self.refresh()


if __name__ == '__main__':
    root = Tk()
    app = LogCal(master=root)
    app.master.title('LogAnalyzer')
    app.mainloop()
    root.destroy()