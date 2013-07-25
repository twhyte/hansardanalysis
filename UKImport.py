#####
## Hansard Analysis Package
## Requires Python 3.3 and BeautifulSoup
## tanya.whyte@mail.utoronto.ca
## Current 2013-07-23
## 2013-07-23
##      ukimport.py 
##      Converts UK Commons XML archives to HansardIO standard
#####

import os
from bs4 import BeautifulSoup
import json
import pickle
import datetime
import copy
import time

# Error definitions

class HansardImportError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HansardImportDateError(UKImportError):
    pass


# UKImport class

class HansardImport(object):
    def __init__(self):
        if os.path.exists(os.path.join(os.getcwd(), "data"))==False:
            os.mkdir(os.path.join(os.getcwd(), "data"))
        else:
            pass
        
    def createDir(self, dirName, path=os.getcwd()): # Helper function for creating directories
        dirPath = os.path.join(path, dirName)
        os.mkdir(dirPath)

    def strip(self,untrusted_html):
        """Strips out all tags"""
        soup = BeautifulSoup(untrusted_html)
        safe_html = ''.join(soup.find_all(text=True))
        return safe_html

    def dictify(self, dictString):
        '''Turn UK hansard stripped string into a HansardDict-style dict object'''
        doneYet = False
        dicted = []
        datesList = []
        while not doneYet:
            n = dictString.find('.xml')
            if n == -1:
                doneYet = True
            else:
                if 's' not in dictString[(n-11):(n-1)]:
                    datesList.append(dictString[(n-11):(n-1)])
                    print((dictString[(n-11):(n-1)]))
                else:
                    datesList.append(dictString[(n-10):(n)])
                    print((dictString[(n-10):(n)]))
                dictString = dictString.replace('.xml', '', 1)
        datesList = set(datesList)
        for date in datesList:
            dicted.append(dict([('date', str(date))]))
        return dicted
        
     
    def scrapeHansardDict(self, dictfilename="UKDict"):
        '''([filename="UKDict"])
        Scrapes the UKDict from ukparse.kforge.net
        Writes HansardDict-type file containing a dict of valid UK files by date
        Also creates a data directory if not already present
        '''

        try:
            self.createDir("data_uk")
        except OSError:
            pass

        if os.path.isfile((dictfilename + '.pkl')): # Checks for existing .pkl file
            a = ""
            while True:
                a = input("File already exists.  Replace? y/n ")
                break
            if a == "y": # Overwrites existing .pkl file
                os.remove(dictfilename + '.pkl')
                WORDS = []
                for word in urllib.request.urlopen("http://ukparse.kforge.net/parldata/scrapedxml/debates/").readlines():
                    WORDS.append(word.strip().decode('utf-8'))
                raw = ''.join(WORDS)
                stripped = self.strip(raw)
                final = self.dictify(stripped)
                output = open((dictfilename + '.pkl'), 'wb')
                pickle.dump(final, output)
                output.close()
                return None
            if a == "n":
                print("No UKDict scraped.")
                return None
        else: # Creates new .pkl file
            WORDS = []
            for word in urllib.request.urlopen("http://ukparse.kforge.net/parldata/scrapedxml/debates/").readlines():
                WORDS.append(word.strip().decode('utf-8'))
            raw = ''.join(WORDS)
            stripped = self.strip(raw)
            final = self.dictify(stripped)
            output = open((dictfilename + '.pkl'), 'wb')
            pickle.dump(final, output)
            output.close()
            return None

    def loadHansardDict(self, dictfilename="UKDict"):
        '''([filename="UKDict"])
        Returns the UKDict in filename.pkl
        '''
        try:
            pkl_file = open((dictfilename + ".pkl"), 'rb')
            myfile = pickle.load(pkl_file)
            pkl_file.close()
            return myfile
        except:
            raise HansardImportError("No .pkl file of that name.")

    def convertUKHansardFile(self, dateH, dictfilename="UKDict"):
        ''' dateH = str format yyyy-mm-dd, dictfilename = str local dict file
        Writes the .pkl file for a valid Hansard date in a folder path Data/yyyy-mm-dd/
        Works with raw xml dump downloaded from ukparse.kforge.net/parldata/scrapedxml/debates/
        Skips over existing files with same path and filename.
        '''

        try:
            activeDict # Test if there is already an activeDict loaded
        except:
            if os.path.isfile((dictfilename + '.pkl')):
                activeDict = self.loadUKDict(dictfilename) # If not, load a UKDict if it exists
            else:
                raise HansardImportError("No dictionary .pkl file of that name.")

        validFiles = []

        for i in activeDict:
            if i["date"] == dateH:
                validFiles.append(i["date"]) # Creates a working list of all UK hansard dates

        if validFiles == []: # Checks to see if we are looking at a valid date
            raise UKImportDateError("Not a valid date.")

        try: # Checks for existing directory for date
            self.createDir(str(dateH), os.path.join(os.getcwd(), "data"))
        except OSError:
            pass

        for validDate in validFiles: # Converts the most recent (ie. correct and up to date) Hansard file to standard format
                                    # Also organizes along same filesystem standard

            if os.path.isfile(os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + '.pkl'))):
                # Checks for existing .pkl file
                print ("Skipped existing file.")
            else: # Creates new .pkl file
                
                ################ Convert here!
                
                output = open((os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + '.pkl'))), 'wb')
                pickle.dump(myfile, output)
                output.close()
                        
        print(((str(workingFile)) + " files processed."))
        return None
        

    def convertUKHansardRange(self, dateStart, dateEnd, dictfilename="UKDict"):
        '''dateStart = str format yyyy-mm-dd, dateEnd = str format yyyy-mm-dd, dictfilename = str local dict file
        Converts to JSON HansardRaw standard and writes the .pkl files between start and end in a folder path Data/yyyy-mm-dd/
        Works with raw xml dump downloaded from ukparse.kforge.net/parldata/scrapedxml/debates/
        Skips over existing files with same path and filename.
        '''

        dateS = datetime.date
        dateE = datetime.date
        
        try:
            dateS = datetime.date(int(dateStart[0:4]), int(dateStart[5:7]), int(dateStart[8:10])) # Convert str to datetime.date objects
            dateE = datetime.date(int(dateEnd[0:4]), int(dateEnd[5:7]), int(dateEnd[8:10]))
        except:
            raise HansardImportDateError("Invalid date.")

        loopDate = copy.deepcopy(dateS)
        dateStepInt = (dateE - dateS).days
        
        for i in range(dateStepInt+1): # Convert UKHansard files for range of dates

            print((loopDate.isoformat()))
            try:
                self.convertUKHansardFile(loopDate.isoformat(), dictfilename)
            except HansardImportDateError: # No Hansard on this date!
                print ("No data here!")
                pass
            dateStepInt += 1
            loopDate += datetime.timedelta(days=1)
             
    def loadHansardFile(self, dateH, trueFilename):
        '''dateH = "yyyy-mm-dd", trueFilename = str real file name of HansardFile
        eg. 2012-12-03.pkl
        Returns a dict of JSON hansard file.
        '''
        try:
            pkl_file = open((os.path.join(os.getcwd(), "data", str(dateH), trueFilename)), 'rb')
            myfile = pickle.load(pkl_file)
            pkl_file.close()
            return myfile
        except (OSError, IOError):
            raise HansardImportError("No .pkl file of that name.")

    def getTrueFilenames(self, dateH):
        '''dateH = "yyyy-mm-dd", hansardType = "House" or "Committee"
        Returns list of filenames str for use in loadHansardFile
        '''
        try:
            originalList = os.listdir((os.path.join(os.getcwd(), "data", str(dateH))))
            # Lists files in the date directory
        except OSError:
            raise HansardImportDateError("Invalid date.")

        return originalList


