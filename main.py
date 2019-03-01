#!/usr/bin/python3

import tkinter
import tkinter.ttk
from tkinter import messagebox
import sqlite3
import webbrowser
import datetime

class RootC:
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.title("City Database")
        self.root.geometry("640x480")
        
        self.menubar = tkinter.Menu(self.root)
        self.root.config(menu=self.menubar)
  
        self.fileMenu = tkinter.Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="Exit", command=lambda: self.quitProgram())
  
        self.helpMenu = tkinter.Menu(self.menubar, tearoff=0)
        self.helpMenu.add_command(label="About", command=lambda: self.helpAbout())
        self.helpMenu.add_command(label="License", command=lambda: self.helpLicense())
        
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.menubar.add_cascade(label="Help", menu=self.helpMenu)
    
    def quitProgram(self):
        self.root.quit()
    
    def helpAbout(self):
        msgBox = messagebox.showinfo("City Database | About", "Search for a city and show it on Google Maps\n\nSee license in Help > License\n\nErik Persson © 2019")
    
    def helpLicense(self):
        LicenseC()

class ApplicationC(RootC):
    def __init__(self, root):
        super().__init__(root)
        self.lat : float = 0.0
        self.lon : float = 0.0
        
        self.appMainFrame = tkinter.ttk.Frame(self.root)
        self.appMainFrame.grid(row=0, column=0, sticky=tkinter.W)
        
        self.notebook = tkinter.ttk.Notebook(self.appMainFrame)
        self.notebook.grid(row=0, column=0, sticky=tkinter.W)
        
        self.logText = tkinter.Text(self.appMainFrame, state="disabled", bg="#000000", fg="#ffffff")
        self.logText.grid(row=1, column=0)
        
        self.searchTab = tkinter.ttk.Frame(self.notebook)
        self.searchTab.grid(row=0, column=0, sticky=tkinter.W)
        self.searchMainFrame = tkinter.ttk.Frame(self.searchTab)
        self.searchMainFrame.grid(row=0, column=0, sticky=tkinter.W)
        self.searchCityLabel = tkinter.Label(self.searchMainFrame, text="City:")
        self.searchCityLabel.grid(row=0, column=0, sticky=tkinter.E)
        self.searchCityEntry = tkinter.Entry(self.searchMainFrame)
        self.searchCityEntry.grid(row=0, column=1, sticky=tkinter.W)
        self.searchCityGoogleMapsButton = tkinter.ttk.Button(self.searchMainFrame, text="Show", command=lambda: self.findCityInDatabase())
        self.searchCityGoogleMapsButton.grid(row=0, column=2, sticky=tkinter.W)
        
        self.insertTab = tkinter.ttk.Frame(self.notebook)
        self.insertTab.grid(row=0, column=0, sticky=tkinter.W)
        self.insertMainFrame = tkinter.ttk.Frame(self.insertTab)
        self.insertMainFrame.grid(row=0, column=0, sticky=tkinter.W)
        self.insertCityLabel = tkinter.Label(self.insertMainFrame, text="City:")
        self.insertCityLabel.grid(row=0, column=0, sticky=tkinter.E)
        self.insertCityEntry = tkinter.Entry(self.insertMainFrame)
        self.insertCityEntry.grid(row=0, column=1, sticky=tkinter.W)
        self.insertCityButton = tkinter.ttk.Button(self.insertMainFrame, text="Save", command=lambda: self.insertValidation())
        self.insertCityButton.grid(row=0, column=2, sticky=tkinter.W)
        self.insertLatLabel = tkinter.Label(self.insertMainFrame, text="Latitude:")
        self.insertLatLabel.grid(row=1, column=0, sticky=tkinter.E)
        self.insertLatEntry = tkinter.Entry(self.insertMainFrame)
        self.insertLatEntry.grid(row=1, column=1, sticky=tkinter.W)
        self.insertLonLabel = tkinter.Label(self.insertMainFrame, text="Longitude:")
        self.insertLonLabel.grid(row=2, column=0, sticky=tkinter.E)
        self.insertLonEntry = tkinter.Entry(self.insertMainFrame)
        self.insertLonEntry.grid(row=2, column=1, sticky=tkinter.W)
        
        self.updateDelete = tkinter.ttk.Frame(self.notebook)
        self.updateDelete.grid(row=0, column=0, sticky=tkinter.W)
        
        self.notebook.add(self.searchTab, text="Search")
        self.notebook.add(self.insertTab, text="Insert")
        self.notebook.add(self.updateDelete, text="Update/Delete")
    
    def findCityInDatabase(self):
        logMsg = "[%s]\n" % (datetime.datetime.now())
        db = sqlite3.connect("./cities.db")
        cursor = db.cursor()
        cursor.execute("SELECT name, lat, lon FROM city WHERE name IS '%s' COLLATE NOCASE;" % self.searchCityEntry.get())
        query = cursor.fetchall()
        if len(query) == 0:
            logMsg += "\"%s\" was not found in the database!\nUnable to open Google Maps in the Default Web Browser.\n" % (self.searchCityEntry.get())
            cursor.execute("SELECT name FROM city WHERE name LIKE '%%%s%%' COLLATE NOCASE;" % self.searchCityEntry.get())
            query = cursor.fetchall()
            maybe = []
            if len(query) == 0:
                logMsg += "\n"
            else:
                for row in query:
                    maybe.append("\"%s\"" % row[0])
                logMsg += "Did you mean %s?\n\n" % (' or '.join(maybe))
        else:
            for row in query:
                self.lat = row[1]
                self.lon = row[2]
            logMsg += "\"%s\" was found in the database.\nOpening Google Maps in the Default Web Browser.\n\n" % (row[0])
            self.showCityOnGoogleMaps(self.lat, self.lon)
        self.printLogMessage(logMsg)
    
    def showCityOnGoogleMaps(self, lat : float, lon : float):
        url = "http://maps.google.com/?q=%.2f,%.2f" % (lat, lon)
        webbrowser.open(url)
    
    def insertValidation(self):
        logMsg = "[%s]\n"  % (datetime.datetime.now())
        goodCity = True
        goodLat = False
        goodLon = False
        if len(self.insertCityEntry.get()) == 0:
            logMsg += "Invalid City input! City cannot be empty.\n"
            goodCity = False
        else:
            db = sqlite3.connect("./cities.db")
            cursor = db.cursor()
            cursor.execute("SELECT name FROM city;")
            query = cursor.fetchall()
            for row in query:
                if row[0].lower() == self.insertCityEntry.get().lower():
                    logMsg += "Invalid City input! \"%s\" already exists.\n" % (row[0])
                    goodCity = False
        try:
            self.lat = float(self.insertLatEntry.get().replace(",", "."))
            goodLat = True
        except ValueError:
            logMsg += "Invalid Latitude input! Enter a number (1 or 1.0 or 1,0).\n"
        try:
            self.lon = float(self.insertLonEntry.get().replace(",", "."))
            goodLon = True
        except ValueError:
            logMsg += "Invalid Longitude input! Enter a number (1 or 1.0 or 1,0).\n"
        if goodCity and goodLat and goodLon:
            self.insertCityEntry.configure(bg="White")
            self.insertLatEntry.configure(bg="White")
            self.insertLonEntry.configure(bg="White")
            self.addCityToDatabase(self.insertCityEntry.get(), self.lat, self.lon)
            logMsg += "\"%s\" added to the database with Latitude %.2f and Longitude %.2f.\n" % (self.insertCityEntry.get(), self.lat, self.lon)
        else:
            if not goodCity:
                self.insertCityEntry.configure(bg="Pink")
            else:
                self.insertCityEntry.configure(bg="White")
            if not goodLat:
                self.insertLatEntry.configure(bg="Pink")
            else:
                self.insertLatEntry.configure(bg="White")
            if not goodLon:
                self.insertLonEntry.configure(bg="Pink")
            else:
                self.insertLonEntry.configure(bg="White")
        logMsg += "\n"
        self.printLogMessage(logMsg)
    
    def addCityToDatabase(self, name : str, lat : float, lon : float):
        db = sqlite3.connect("cities.db")
        cursor = db.cursor()
        cursor.execute("INSERT INTO city (name, lat, lon) VALUES ('%s', %.2f, %.2f);" % (name, lat, lon))
        db.commit()
    
    def printLogMessage(self, logMsg):
        print(logMsg)
        
        with open("log.txt", 'a') as logFile:
            logFile.write(logMsg)
        
        self.logText.configure(state="normal")
        self.logText.insert(1.0, logMsg)
        self.logText.configure(state="disabled")

class LicenseC:
    def __init__(self):
        super().__init__()
        self.mitLicense = """
The MIT License (MIT)

Copyright (c) 2019 Erik Persson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
        self.licenseWindow = tkinter.Toplevel()
        self.licenseWindow.title("City Database | License")
        self.licenseFrame = tkinter.ttk.Frame(self.licenseWindow)
        self.licenseFrame.grid(row=0, column=0, sticky=tkinter.W)
        self.licenseText = tkinter.Text(self.licenseFrame, bg="#ffffff", fg="#0000ff")
        self.licenseText.insert(1.0, self.mitLicense)
        self.licenseText.configure(state="disabled")
        self.licenseText.grid(row=0, column=0, sticky=tkinter.W)
        self.licenseButton = tkinter.ttk.Button(self.licenseFrame, text="OK", command=lambda: self.licenseWindow.destroy())
        self.licenseButton.grid(row=1, column=0)

def main():
    root = tkinter.Tk()
    app = ApplicationC(root)
    root.mainloop()

if __name__ == '__main__':
    main()
