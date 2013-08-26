#####
## Hansard Analysis Package
## Requires Python 3.2
## tanya.whyte@mail.utoronto.ca
## Current 2013-07-23
## 
##      UKImport.py 
##      Converts UK Commons XML archives to HansardIO standard
#####

import os
from bs4 import BeautifulSoup
import json
import pickle
import datetime
import copy
import time
import datetime
from toJSON import parseXML

# Error definitions

class HansardImportError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HansardImportDateError(HansardImportError):
    pass

# UK Translation class - writes and loads dictionaries necessary for translating UK Hansard
# data to the standard imposed by Canadian Hansard data from openparliament.ca

class UKTranslator (object):
    def __init__(self):
        pass

    def makeUKTranslationFile(self):
        '''Creates and writes a file UKTranslationData.pkl
        Contains parliament and session data, politicians, etc.
        '''

        # For the moment, we only go back as far as 1994 here for simplicity's sake
        # eg. Old records have nasty duplicates that would need to be dealt with

        # "dates" provides information about parliament/session beginning and end dates
        # source: http://www.parliament.uk/about/faqs/house-of-commons-faqs/business-faq-page/recess-dates/recess/

        datesDict = {'1994':[{'51':{'2':[datetime.date(1993,11,18), datetime.date(1994,11,3)], '3':[datetime.date(1994,11,16), datetime.date(1995,11,8)]}}], \
                     '1995':[{'51':{'3':[datetime.date(1994,11,16), datetime.date(1995,11,8)], '4':[datetime.date(1995,11,15), datetime.date(1996,10,7)]}}], \
                     '1996':[{'51':{'4':[datetime.date(1995,11,15), datetime.date(1996,10,7)], '5':[datetime.date(1996,10,23), datetime.date(1997,3,21)]}}], \
                     '1997':[{'51':{'5':[datetime.date(1996,10,23), datetime.date(1997,3,21)]}}, {'52':{'1':[datetime.date(1997,5,14), datetime.date(1998,11,19)]}}], \
                     '1998':[{'52':{'1':[datetime.date(1997,5,14), datetime.date(1998,11,19)], '2':[datetime.date(1998,11,24), datetime.date(1999,11,11)]}}], \
                     '1999':[{'52':{'2':[datetime.date(1998,11,24), datetime.date(1999,11,11)], '3':[datetime.date(1999,11,24), datetime.date(2000,11,30)]}}], \
                     '2000':[{'52':{'3':[datetime.date(1999,11,24), datetime.date(2000,11,30)], '4':[datetime.date(2000,12,6), datetime.date(2001,5,3)]}}], \
                     '2001':[{'52':{'4':[datetime.date(2000,12,6), datetime.date(2001,5,3)]}}, {'53':{'1':[datetime.date(2001,6,20), datetime.date(2002,11,7)]}}], \
                     '2002':[{'53':{'1':[datetime.date(2001,6,20), datetime.date(2002,11,7)], '2':[datetime.date(2002,11,13), datetime.date(2003,11,20)]}}], \
                     '2003':[{'53':{'2':[datetime.date(2002,11,13), datetime.date(2003,11,20)], '3':[datetime.date(2003,11,26), datetime.date(2004,11,18)]}}], \
                     '2004':[{'53':{'3':[datetime.date(2003,11,26), datetime.date(2004,11,18)], '4':[datetime.date(2004,11,23), datetime.date(2005,5,7)]}}], \
                     '2005':[{'53':{'4':[datetime.date(2004,11,23), datetime.date(2005,5,7)]}}, {'54':{'1':[datetime.date(2005,5,17), datetime.date(2006,11,8)]}}], \
                     '2006':[{'54':{'1':[datetime.date(2005,5,17), datetime.date(2006,11,8)], '2':[datetime.date(2006,11,15), datetime.date(2007,10,30)]}}], \
                     '2007':[{'54':{'2':[datetime.date(2006,11,15), datetime.date(2007,10,30)], '3':[datetime.date(2007,11,6), datetime.date(2008,11,26)]}}], \
                     '2008':[{'54':{'3':[datetime.date(2007,11,6), datetime.date(2008,11,26)], '4':[datetime.date(2008,12,3), datetime.date(2009,11,12)]}}], \
                     '2009':[{'54':{'4':[datetime.date(2008,12,3), datetime.date(2009,11,12)], '5':[datetime.date(2009,11,18), datetime.date(2010,4,12)]}}], \
                     '2010':[{'54':{'5':[datetime.date(2009,11,18), datetime.date(2010,4,12)]}}, {'55':{'1':[datetime.date(2010,5,25), datetime.date(2012,5,1)]}}], \
                     '2011':[{'55':{'1':[datetime.date(2010,5,25), datetime.date(2012,5,1)]}}], \
                     '2012':[{'55':{'1':[datetime.date(2010,5,25), datetime.date(2012,5,1)], '2':[datetime.date(2012,5,9), datetime.date(2013,4,25)]}}]}
        
        # "names" relies on a copy of the file "all-members.xml" in working directory from http://ukparse.kforge.net/svn/parlparse/members/all-members.xml

        namesDict = {}
        
        try:
            f = "all-members.xml"
            j = parseXML(f)
            k = json.loads(j)
                
        except:
            raise HansardImportError("No all-members.xml file present.")

        working=k["publicwhip"]["member"]

        for member in working:
            endDate = member["todate"]
            endDateObject = datetime.date(int(endDate[0:4]), 1, 1)
            if endDateObject.year < 1994:
                pass
                # Ignoring this person because they left Commons before 1994
            else:
                firstName = member["firstname"]
                lastName = member["lastname"]
                fullName = firstName + " " + lastName
                riding = member["constituency"]
                party = member["party"]
                startDate = member["fromdate"]

                if fullName in namesDict:
                    # A person with this name already exists--check to see if we have a duplicate
                    # We assume that there will be no two people with the same name in the same riding who aren't duplicates
                    #####This doesn't work properly--I'll leave duplicates in for the moment#####
                    
                    for listMember in namesDict[fullName]:
                        if riding in listMember:
                            pass
                            # this person seems to be a duplicate
                        else:
                            # this person is a new member with a shared name but different riding -- add them
                            ridingDict = {"fullName":fullName, "firstName":firstName, "lastName":lastName, "riding":riding, "party":party, "startDate":startDate, "endDate":endDate}
                            namesDict[fullName].append({riding:copy.deepcopy(ridingDict)})
                            print (fullName+" has another instance")
                        
                else:
                    # This fullname doesn't exist yet, create it
                    ridingDict = {"fullName":fullName, "firstName":firstName, "lastName":lastName, "riding":riding, "party":party, "startDate":startDate, "endDate":endDate}
                    print ("Added" + " " + fullName)
                    namesDict[fullName] = [{riding:copy.deepcopy(ridingDict)}]
  
        # "parliamentData" is a placeholder for anything else that needs to be added in future

        # now we write the translation file

        final = {"names":(copy.deepcopy(namesDict)), "dates":(copy.deepcopy(datesDict))}
        output = open(('UKTranslationData.pkl'), 'wb')
        pickle.dump(final, output)
        
    def loadUKTranslationFile(self, filename="UKTranslationData.pkl"):
        '''Loads a file UKSessionData.pkl
        Contains parliament and session data, politicians, etc.
        Needed for convertUKHansardFile()
        '''
        try:
            pkl_file = open((filename), 'rb')
            myfile = pickle.load(pkl_file)
            pkl_file.close()
            return myfile
        except (OSError, IOError):
            raise HansardImportError("No .pkl file of that name.")

    def convertDateToUKParlSess(self, dateStr, parlsess): # TEST ME
        '''Returns either the parliament or the session information for a given date
        dateStr == yyyy-mm-dd string format, parlsess = Parliament or Session in str format
        Note that we return null if parliament isn't in session at the time (this problem is not handled here)'''
    
        TransFile = self.loadUKTranslationFile()
        workingYear = dateStr[0:4]
        if dateStr[5] == "0":
            workingMonth = dateStr[6]
        else:
            workingMonth = dateStr[5:7]
        if dateStr[8] == '0':
            workingDay = dateStr[9]
        else:
            workingDay = dateStr[8:10]

        workingDateObject = datetime.date(int(workingYear), int(workingMonth), int(workingDay))

        if parlsess == "Parliament":
            workingYearList = TransFile['dates'][workingYear]
            if len(workingYearList) == 1: # there is only one parliament in this year, so return it
                return list(workingYearList[0].keys())[0]
            else:
                for yearParl in workingYearList: # for dict in list of dicts, each dict has a key of the parliament
                    for workingParliament in list(yearParl.keys()):
                        for workingSession in list(yearParl[workingParliament].keys()):
                            testStart = yearParl[workingParliament][workingSession][0]
                            testEnd = yearParl[workingParliament][workingSession][1]
                            if testStart <= workingDateObject <= testEnd:
                                return workingParliament
                            else:
                                pass

        elif parlsess == "Session": ######################### TEST ME
            workingYearList = TransFile['dates'][workingYear]
				for yearParl in workingYearList: # for dict in list of dicts, each dict has a key of the parliament
                    for workingParliament in list(yearParl.keys()):
                        for workingSession in list(yearParl[workingParliament].keys()):
                            testStart = yearParl[workingParliament][workingSession][0]
                            testEnd = yearParl[workingParliament][workingSession][1]
                            if testStart <= workingDateObject <= testEnd:
                                return workingSession
    
        else:
            raise HansardImportError("Invalid--Choose Parliament or Session")

    def convertUKName(self, memberName, dateStr, parrid): #################### TEST ME
        '''Returns either the parliament or the session information for a given date
        memberName = "Lastname Firstname", dateStr == yyyy-mm-dd string format, parrid = Party or Riding in str format'''
        
        TransFile = self.loadUKTranslationFile()
		
		workingYear = dateStr[0:4]
        if dateStr[5] == "0":
            workingMonth = dateStr[6]
        else:
            workingMonth = dateStr[5:7]
        if dateStr[8] == '0':
            workingDay = dateStr[9]
        else:
            workingDay = dateStr[8:10]

        workingDateObject = datetime.date(int(workingYear), int(workingMonth), int(workingDay))
		
        if parrid == "Party":
            workingNameDict = TransFile['names']
			try:
				memberInfo = workingNameDict[memberName]
				if len(memberInfo) == 1: # only one person with this name; return their info
					return memberInfo[0]["party"]
				else: # more than one person with this name (or some kind of duplicate record exists) so check date
					for personInstance in memberInfo:
						testStart = personInstance[startDate]
						testEnd = personInstance[endDate]
						if testStart <= workingDateObject <= testEnd:
							return personInstance["party"]
					
			except KeyError:
				raise HansardImportError("Invalid--Name Doesn't Exist in UK Names")
			
        elif parrid == "Riding":
			workingNameDict = TransFile['names']
			try:
				memberInfo = workingNameDict[memberName]
				if len(memberInfo) == 1: # only one person with this name; return their info
					return memberInfo[0]["party"]
				else: # more than one person with this name (or some kind of duplicate record exists) so check date
					for personInstance in memberInfo:
						testStart = personInstance[startDate]
						testEnd = personInstance[endDate]
						if testStart <= workingDateObject <= testEnd:
							return personInstance["riding"]
							
			except KeyError:
				raise HansardImportError("Invalid--Name Doesn't Exist in UK Names")
			
			
        else:
            raise HansardImportError("Invalid--Choose Party or Riding")

    
# HansardImport class

class HansardImport(object):
    def __init__(self):
        if os.path.exists(os.path.join(os.getcwd(), "data"))==False:
            os.mkdir(os.path.join(os.getcwd(), "data"))
        else:
            pass

        self.translator = UKTranslator()
        
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
            raise HansardImportDateError("Not a valid date.")

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
                
                # Convert here!
                workingHansardLog = {}
				
				workingHansardLog["parliament"] = self.translator.convertDateToUKParlSess(dateH, "Parliament")
				workingHansardLog["hansardDate"] = dateH
				workingHansardLog["hansardID"] = None
				workingHansardLog["session"] = self.translator.convertDateToUKParlSess(dateH, "Session")
				workingHansardLog["URL"] = None
				workingHansardLog["originalURL"] = None
				
				# convert statements to JSON-style standard
				
				workingStatements = [] 
				# left off here!!!!!###################################
				
				workingHansardLog["statements"] = copy.deepcopy("workingStatements")
				
				
                
                output = open((os.path.join(os.getcwd(), "data", str(dateH), (str(dateH) + '.pkl'))), 'wb')
                pickle.dump(workingHansardLog, output)
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

    def getTrueFilenames(self, dateH, hansardType=""):
        '''dateH = "yyyy-mm-dd"
        Returns list of filenames str for use in loadHansardFile
        '''
        try:
            originalList = os.listdir((os.path.join(os.getcwd(), "data", str(dateH))))
            # Lists files in the date directory
        except OSError:
            raise HansardImportDateError("Invalid date.")

        return originalList


