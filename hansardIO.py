#####
## Hansard Analysis Package
## Requires Python 3.3 and BeautifulSoup
## tanya.whyte@mail.utoronto.ca
## Current 2013-07-23
##      hansardIO.py 
##      Fetches/writes/loads HansardDict and Hansard files
##      To do: separate committee proceedings by committee name
#####

import os
import urllib.request, urllib.error, urllib.parse
import http.client
import json
import pickle
import datetime
import copy
import time
import socket

# Error definitions

class HansardImportError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HansardImportDateError(HansardImportError):
    pass

# HansardImport class

class HansardImport(object):
    def __init__(self):
        if os.path.exists(os.path.join(os.getcwd(), "data"))==False:
            os.mkdir(os.path.join(os.getcwd(), "data"))
        else:
            pass
        default_timeout = 12
        socket.setdefaulttimeout(default_timeout)

    def createDir(self, dirName, path=os.getcwd()): # Helper function for creating directories
        dirPath = os.path.join(path, dirName)
        os.mkdir(dirPath)
           
    def scrapeHansardDict(self, dictfilename="HansardDict"):
        '''([filename="HansardDict"])
        Writes the HansardDict.pkl file containing a dict of valid Hansard files by date
        Also creates a data directory if not already present
        '''

        try:
            self.createDir("data")
        except OSError:
            pass

        if os.path.isfile((dictfilename + '.pkl')): # Checks for existing .pkl file
            a = ""
            while True:
                a = input("File already exists.  Replace? y/n ")
                break
            if a == "y": # Overwrites existing .pkl file
                os.remove(dictfilename + '.pkl')
                response = urllib.request.urlopen("http://openparliament.ca/api/hansards/").read()
                myfile = json.loads(response.decode('utf-8'))
                output = open((dictfilename + '.pkl'), 'wb')
                pickle.dump(myfile, output)
                output.close()
                return None
            if a == "n":
                print("No HansardDict scraped.")
                return None
        else: # Creates new .pkl file
            response = urllib.request.urlopen("http://openparliament.ca/api/hansards/").read()
            myfile = json.loads(response.decode('utf-8'))
            output = open((dictfilename + '.pkl'), 'wb')
            pickle.dump(myfile, output)
            output.close()
            return None

    def loadHansardDict(self, dictfilename="HansardDict"):
        '''([filename="HansardDict"])
        Returns the HansardDict in filename.pkl
        '''
        try:
            pkl_file = open((dictfilename + ".pkl"), 'rb')
            myfile = pickle.load(pkl_file)
            pkl_file.close()
            return myfile
        except:
            raise HansardImportError("No .pkl file of that name.")

    def scrapeHansard(self, dateH, dictfilename="HansardDict"):
        ''' dateH = str format yyyy-mm-dd, dictfilename = str local dict file
        Writes the .pkl files for a valid Hansard date in a folder path Data/yyyy-mm-dd/
        Skips over existing files with same path and filename.
        '''

        try:
            activeDict # Test if there is already an activeDict loaded
        except:
            if os.path.isfile((dictfilename + '.pkl')):
                activeDict = self.loadHansardDict(dictfilename) # If not, load a HansardDict if it exists
            else:
                raise HansardImportError("No dictionary .pkl file of that name.")

        validURLS = []
        workingFile = 0
      
        for i in activeDict:
            if i["date"] == dateH:
                validURLS.append(i["api_url"]) # Creates a list of URLs for existing Hansard proceedings on given date

        if validURLS == []: # Checks to see if we are looking at a valid date
            raise HansardImportDateError("Not a valid date.")

        try: # Checks for existing directory for date
            self.createDir(str(dateH), os.path.join(os.getcwd(), "data"))
        except OSError:
            pass
        
    
        for url in validURLS: # Collects Hansard data files for given date
            try:
                workingFile += 1
                skippedExistingFile = 0
                print (url)
                if os.path.isfile(os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + "_Committee" + '.pkl'))) or \
                os.path.isfile(os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + "_House" + '.pkl'))):
                    # Checks for existing .pkl file
                    print ("Skipped existing file.")
                    skippedExistingFile = 1
                    pass
                else: # Creates new .pkl file
                    myfile = 0
                    filenameURL = ""
                    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}
                    req = urllib.request.Request(("http://openparliament.ca" + url),None,headers)
                    response = urllib.request.urlopen(req, timeout = 12).read()
                    myfile = json.loads(response.decode('utf-8'))
                    if (myfile.get("url"))[:11] == "/committees": # Name by Committee or House proceedings
                        filenameURL = "_Committee"
                    else:
                        filenameURL = "_House"
                    output = open((os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + filenameURL + '.pkl'))), 'wb')
                    pickle.dump(myfile, output)
                    output.close()
                if skippedExistingFile == 0:
                    print ("File written.  Waiting 35s.")
                    time.sleep(35)
                    
            except (http.client.IncompleteRead, socket.timeout, urllib.error.URLError):
                print ("An error/timeout occurred!")
                retriesCount = 5  # Set number of retries for error

                def IncompleteReadHandler(workingFile,dateH,url):
                    # Deletes any broken file
                    if os.path.isfile(os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + "_Committee" + '.pkl'))):
                        os.remove(os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + "_Committee" + '.pkl')))
                    elif os.path.isfile(os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + "_House" + '.pkl'))):
                        os.remove(os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + "_House" + '.pkl')))
                    
                    # Now retries request and creates new .pkl file
                    myfile = 0
                    filenameURL = ""
                    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}
                    req = urllib.request.Request(("http://openparliament.ca" + url),None,headers)
                    response = urllib.request.urlopen(req, timeout = 12).read()
                    myfile = json.loads(response.decode('utf-8'))
                    if (myfile.get("url"))[:11] == "/committees":
                        filenameURL = "_Committee"
                    elif (myfile.get("url"))[:8] == "/debates":
                        filenameURL = "_House"
                    else:
                        raise HansardImportError("What happen!!!!!!!!")
                        pass
                    output = open((os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + "_" + str(workingFile) + filenameURL + '.pkl'))), 'wb')
                    pickle.dump(myfile, output)
                    output.close()
                    print ("File written.  Waiting 35s.")
                    time.sleep(35)

                retstr = copy.deepcopy(retriesCount)
                while retriesCount != 0:
                    try:
                        print ("Retrying...")
                        IncompleteReadHandler(workingFile,dateH,url)

                        break
                    except (http.client.IncompleteRead, socket.timeout, urllib.error.URLError):
                        retriesCount -= 1
                        print(("Attempt failed, " + str(retriesCount) + " tries remaining."))
                        time.sleep(35)
                if retriesCount == 0:
                    raise HansardImportError("Error/Timeout failure after " + str(retstr) + " retries.") # Total failure
                        
        print(((str(workingFile)) + " files processed."))
        return None
        

    def fetchHansard(self, dateStart, dateEnd, dictfilename="HansardDict"):
        '''dateStart = str format yyyy-mm-dd, dateEnd = str format yyyy-mm-dd, dictfilename = str local dict file
        Fetches and writes Hansard data from range dateStart to dateEnd (inclusive)
        Skips over existing files with same path and filename, skips over non-existent dates.
        '''

        dateS = datetime.date
        dateE = datetime.date
        
        try:
            dateS = datetime.date(int(dateStart[0:4]), int(dateStart[5:7]), int(dateStart[8:10])) # Convert str to datetime.date objects
            dateE = datetime.date(int(dateEnd[0:4]), int(dateEnd[5:7]), int(dateEnd[8:10]))
        except:
            raise HansardImportError("Invalid date.")

        loopDate = copy.deepcopy(dateS)
        dateStepInt = (dateE - dateS).days
        
        for i in range(dateStepInt+1): # Fetch Hansard files for range of dates

            print((loopDate.isoformat()))
            try:
                self.scrapeHansard(loopDate.isoformat(), dictfilename)
            except HansardImportDateError: # No Hansard on this date!
                print ("No data here!")
                pass
            dateStepInt += 1
            loopDate += datetime.timedelta(days=1)

    def fetchHansardDateList(self, dateList, dictfilename = "HansardDict"):
        '''dateList = list of str format yyyy-mm-dd, dictfilename = str local dict file
        Fetches and writes Hansard data for dates in dateList
        Skips over existing files with same path and filename, skips over non-existent dates.
        '''

        invalidDates = 0
        convertedDateList = []
        for i in dateList: # Convert dateList to datetime.date objects, skips invalid dates
            try:
                convertedDateList.append(datetime.date(int(i[0:4]), int(i[5:7]), int(i[8:10])))
            except:
                invalidDates += 1
                pass
            
        for j in convertedDateList: # Fetch Hansard files for list of dates
            print((j.isoformat()))
            try:
                self.scrapeHansard(j.isoformat(), dictfilename)
            except HansardImportDateError: # No Hansard on this date!
                print ("No data here!")
                pass
             
    def loadHansardFile(self, dateH, trueFilename):
        '''dateH = "yyyy-mm-dd", trueFilename = str real file name of HansardFile
        eg. 2012-12-03_1_Committee.pkl
        Returns a dict of JSON hansard file.
        '''
        try:
            pkl_file = open((os.path.join(os.getcwd(), "data", str(dateH), trueFilename)), 'rb')
            myfile = pickle.load(pkl_file)
            pkl_file.close()
            return myfile
        except (OSError, IOError):
            raise HansardImportError("No .pkl file of that name.")

    def getTrueFilenames(self, dateH, hansardType="House"):
        '''dateH = "yyyy-mm-dd", hansardType = "House" or "Committee"
        Returns list of filenames str for use in loadHansardFile
        '''
        try:
            originalList = os.listdir((os.path.join(os.getcwd(), "data", str(dateH))))
            # Lists files in the date directory
        except OSError:
            raise HansardImportDateError("Invalid date.")

        collectorList = []
        
        if hansardType == "House":
            for i in originalList:
                if "House" in i:
                    collectorList.append(i)
                
        elif hansardType == "Committee":
            for i in originalList:
                if "Committee" in i:
                    collectorList.append(i)
        else:
            raise HansardImportError("Invalid Hansard type (must be House or Committee)")
        
        return collectorList


