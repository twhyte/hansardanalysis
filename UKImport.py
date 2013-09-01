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
import re
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

    def dateObjectifier(self, dateStr):
        '''Converts a yyyy-mm-dd to a datetime.date object'''

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
        return workingDateObject

        
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
                     '1996':[{'51':{'4':[datetime.date(1995,11,15), datetime.date(1996,10,7)], '5':[datetime.date(1996,10,14), datetime.date(1997,3,21)]}}], \
                     '1997':[{'51':{'5':[datetime.date(1996,10,23), datetime.date(1997,3,21)]}}, {'52':{'1':[datetime.date(1997,5,1), datetime.date(1998,11,19)]}}], \
                     '1998':[{'52':{'1':[datetime.date(1997,5,1), datetime.date(1998,11,19)], '2':[datetime.date(1998,11,24), datetime.date(1999,11,11)]}}], \
                     '1999':[{'52':{'2':[datetime.date(1998,11,24), datetime.date(1999,11,11)], '3':[datetime.date(1999,11,17), datetime.date(2000,11,30)]}}], \
                     '2000':[{'52':{'3':[datetime.date(1999,11,17), datetime.date(2000,11,30)], '4':[datetime.date(2000,12,6), datetime.date(2001,5,11)]}}], \
                     '2001':[{'52':{'4':[datetime.date(2000,12,6), datetime.date(2001,5,11)]}}, {'53':{'1':[datetime.date(2001,6,13), datetime.date(2002,11,7)]}}], \
                     '2002':[{'53':{'1':[datetime.date(2001,6,13), datetime.date(2002,11,7)], '2':[datetime.date(2002,11,13), datetime.date(2003,11,20)]}}], \
                     '2003':[{'53':{'2':[datetime.date(2002,11,13), datetime.date(2003,11,20)], '3':[datetime.date(2003,11,26), datetime.date(2004,11,18)]}}], \
                     '2004':[{'53':{'3':[datetime.date(2003,11,26), datetime.date(2004,11,18)], '4':[datetime.date(2004,11,23), datetime.date(2005,4,7)]}}], \
                     '2005':[{'53':{'4':[datetime.date(2004,11,23), datetime.date(2005,4,7)]}}, {'54':{'1':[datetime.date(2005,5,11), datetime.date(2006,11,8)]}}], \
                     '2006':[{'54':{'1':[datetime.date(2005,5,11), datetime.date(2006,11,8)], '2':[datetime.date(2006,11,15), datetime.date(2007,10,30)]}}], \
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
        print(len(working))

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
                memberID = member["id"]
                party = member["party"]
                startDate = member["fromdate"]

                if memberID in namesDict:
                    # A person with this name already exists--check to see if we have a duplicate
                    # We assume that there will be no two people with the same name in the same riding who aren't duplicates
                    # This doesn't work properly, but since these only show up in very old data it's fine for now
                    
                    for listMember in namesDict[memberID]:
                        if riding in listMember:
                            pass
                            # this person seems to be a duplicate
                        else:
                            # this person is a new member with a shared name but different riding -- add them
                            ridingDict = {"fullName":fullName, "memberID": memberID, "firstName":firstName, "lastName":lastName, "riding":riding, "party":party, "startDate":startDate, "endDate":endDate}
                            namesDict[memberID].append({riding:copy.deepcopy(ridingDict)})
                            print (fullName+" has another instance")
                        
                else:
                    # This fullname doesn't exist yet, create it
                    ridingDict = {"fullName":fullName, "firstName":firstName, "memberID": memberID, "lastName":lastName, "riding":riding, "party":party, "startDate":startDate, "endDate":endDate}
                    print ("Added" + " " + memberID)
                    namesDict[memberID] = [{riding:copy.deepcopy(ridingDict)}]
  
        # "parliamentData" is a placeholder for anything else that needs to be added in future

        #names2010 dict--unfortunately, there are two allmembers files!!!
        names2010Dict = {}
        
        try:
            f = "all-members-2010.xml"
            j = parseXML(f)
            k = json.loads(j)
                
        except:
            raise HansardImportError("No all-members-2010.xml file present.")

        working=k["publicwhip"]["member"]
        print(len(working))

        for member in working:
            endDate = member["todate"]
            endDateObject = datetime.date(2013, 1, 1)
            firstName = member["firstname"]
            lastName = member["lastname"]
            fullName = firstName + " " + lastName
            riding = member["constituency"]
            memberID = member["id"]
            party = member["party"]
            startDate = member["fromdate"]
            ridingDict = {"fullName":fullName, "firstName":firstName, "memberID": memberID, "lastName":lastName, "riding":riding, "party":party, "startDate":startDate, "endDate":endDate}
            print ("Added" + " " + memberID)
            names2010Dict[memberID] = [{riding:copy.deepcopy(ridingDict)}]
        

        # now we write the translation file

        final = {"names":(copy.deepcopy(namesDict)), "dates":(copy.deepcopy(datesDict)), "names2010":(copy.deepcopy(names2010Dict))}
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

    def convertDateToUKParlSess(self, dateStr, parlsess):
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

        elif parlsess == "Session": 
            workingYearList = TransFile['dates'][workingYear]
            for yearParl in workingYearList:  # for dict in list of dicts, each dict has a key of the parliament
                for workingParliament in list(yearParl.keys()):
                    for workingSession in list(yearParl[workingParliament].keys()):
                        testStart = yearParl[workingParliament][workingSession][0]
                        testEnd = yearParl[workingParliament][workingSession][1]
                        if testStart <= workingDateObject <= testEnd:
                            return workingSession
    
        else:
            raise HansardImportError("Invalid--Choose Parliament or Session")

    def convertUKName(self, dateStr, memberID, parrid):
        '''Returns either the party or riding information for a given date
        memberID is a string, dateStr == yyyy-mm-dd string format, parrid = Party or Riding or Fullname in str format
        Returns None if they weren't in Parliament on dateStr
        '''
        
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

        if memberID == "unknown":
            return "unknown"
        if memberID =="uk.org.publicwhip/royal/-1": #The Queen!
            if parrid == "Party":
                return ""
            elif parrid == "Riding":
                return ""
            elif parrid == "Fullname":
                return "The Queen"
            
        if parrid == "Party":
            if memberID[25]=="4" and len(memberID)==30: ##it's a post-2010 instance
                workingNameDict = TransFile['names2010']
            else:
                workingNameDict = TransFile['names']
            try:
                memberInfo = workingNameDict[memberID]
                if len(memberInfo) == 1: # only one person with this ID; return their info
                    return memberInfo[0][(list(memberInfo[0].keys())[0])]["party"]
                
                else: # more than one person with this name (or some kind of duplicate record exists) so check date
                    for personInstance in range(len(memberInfo)):
                        testStart =  self.dateObjectifier(memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["startDate"])
                        testEnd = self.dateObjectifier(memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["endDate"])

                        if testStart <= workingDateObject <= testEnd:
                            return memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["party"]
                        
            except KeyError:
                raise HansardImportError("Invalid--ID Doesn't Exist in UK Names")
			
        elif parrid == "Riding":
            if memberID[25]=="4" and len(memberID)==30: #it's a post-2010 instance
                workingNameDict = TransFile['names2010']
            else:
                workingNameDict = TransFile['names']
            try:
                memberInfo = workingNameDict[memberID]
                if len(memberInfo) == 1: # only one person with this name; return their info
                    return memberInfo[0][(list(memberInfo[0].keys())[0])]["riding"]
                
                else: # more than one person with this name (or some kind of duplicate record exists) so check date
                    for personInstance in range(len(memberInfo)):
                        testStart =  self.dateObjectifier(memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["startDate"])
                        testEnd = self.dateObjectifier(memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["endDate"])
                        if testStart <= workingDateObject <= testEnd:
                            return memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["riding"]
                        
            except KeyError:
                raise HansardImportError("Invalid--ID Doesn't Exist in UK Names")
			
        elif parrid == "Fullname":
            if memberID[25]=="4" and len(memberID)==30: #it's a post-2010 instance
                workingNameDict = TransFile['names2010']
            else:
                workingNameDict = TransFile['names']
            try:
                memberInfo = workingNameDict[memberID]
                if len(memberInfo) == 1: # only one person with this name; return their info
                    return memberInfo[0][(list(memberInfo[0].keys())[0])]["fullName"]
                
                else: # more than one person with this name (or some kind of duplicate record exists) so check date
                    for personInstance in range(len(memberInfo)):
                        testStart =  self.dateObjectifier(memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["startDate"])
                        testEnd = self.dateObjectifier(memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["endDate"])
                        if testStart <= workingDateObject <= testEnd:
                            return memberInfo[personInstance][(list(memberInfo[personInstance].keys())[0])]["fullName"]

            except KeyError:
                raise HansardImportError("Invalid--ID Doesn't Exist in UK Names")
        else:
            raise HansardImportError("Invalid--Choose Party or Riding or Fullname")

        
    
# HansardImport class

class HansardImport(object):
    def __init__(self):
        if os.path.exists(os.path.join(os.getcwd(), "data_uk"))==False:
            os.mkdir(os.path.join(os.getcwd(), "data_uk"))
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

    def strip_friend(self, text):
        '''Quick regex hack to remove honfriend class phrase tags so that all speech text is properly processed'''
    
        p = re.compile(r'<phrase class="honfriend".*?>.*?>')
        return p.sub('', text)

    def strip_date(self, text):
        '''Quick regex hack to remove date class phrase tags so that all speech text is properly processed'''
    
        p = re.compile(r'<phrase class="date".*?>.*?>')
        return p.sub('', text)

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
        Writes the .pkl file for a valid Hansard date in a folder path data_uk/yyyy-mm-dd/
        Works with raw xml dump downloaded from ukparse.kforge.net/parldata/scrapedxml/debates/
        Skips over existing files with same path and filename.
        Note that only select data is converted:  speech text, politician, party, riding, time
        '''

        try:
            activeDict # Test if there is already an activeDict loaded
        except:
            if os.path.isfile((dictfilename + '.pkl')):
                activeDict = self.loadHansardDict(dictfilename) # If not, load a UKDict if it exists
            else:
                raise HansardImportError("No dictionary .pkl file of that name.")

        validFiles = []

        for i in activeDict:
            if i["date"] == dateH:
                validFiles.append(i["date"]) # Creates a working list of all UK hansard dates

        if validFiles == []: # Checks to see if we are looking at a valid date
            raise HansardImportDateError("Not a valid date.")

        try: # Checks for existing directory for date
            self.createDir(str(dateH), os.path.join(os.getcwd(), "data_uk"))
        except OSError:
            pass

        for validDate in validFiles: # Converts the most recent (ie. correct and up to date) Hansard file to standard format
                                    # Also organizes along same filesystem standard

            if os.path.isfile(os.path.join(os.getcwd(), "data_uk", str(dateH), (str(dateH) + '.pkl'))):
                # Checks for existing .pkl file
                print ("Skipped existing file.")
            else: # Creates new .pkl file
                
                # Convert here!
                
                if os.path.isfile((os.path.join(os.getcwd(), "data_uk_raw", "debates"+validDate+".xml"))):
                    f = (os.path.join(os.getcwd(), "data_uk_raw", "debates"+validDate+".xml"))
                else:
                    f = (os.path.join(os.getcwd(), "data_uk_raw", "debates"+validDate+"a"+".xml"))
                
                # strip encoding information to make lxml happy

                lines = open(f, 'r', encoding = "iso-8859-1").readlines()
                lines[0] = '<?xml version="1.0"?>\n'
                file = open(f, 'w', encoding = "iso-8859-1")
                for line in lines:
                    file.write(line)
                file.close()

##                lines = open(f, 'r').readlines()
##                stripHolder = []
##                for q in lines:
##                    r = q.replace("<i>", "") # strips italics tags
##                    s = r.replace("</i>", "")
##                    t = self.strip_friend(s) # strips honfriend class phrases
##                    stripHolder.append(t)
##                file = open(f, 'w')
##                for line in stripHolder: 
##                    file.write(line)
                
                # checks if we read the most current file; if not, finds it
                
                j = parseXML(f)
                k = json.loads(j)

                for scrapeversion in ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']:
                    try:
                        f = (os.path.join(os.getcwd(), "data_uk_raw", "debates"+validDate+scrapeversion+".xml"))
                        lines = open(f, 'r', encoding = "iso-8859-1").readlines()
                        lines[0] = '<?xml version="1.0"?>\n'
                        stripHolder = []
                        for q in lines:
                            n = q.replace("</i >", "")
                            r = n.replace("<i>", "") # strips italics tags
                            s = r.replace("</i>", "")
                            t = self.strip_friend(s)
                            u = self.strip_date(t) # strips bad class phrases
                            stripHolder.append(u)
                        file = open(f, 'w', encoding = "iso-8859-1")
                        for line in stripHolder: 
                            file.write(line)
                        file.close()
                        j = parseXML(f)
                        k = json.loads(j)
                        if (k["publicwhip"]["latest"]) == "no":
                            pass
                        else:
                            print ("Loaded scrapeversion "+scrapeversion)
                            break
                    except IOError:
                        pass
                    


                # constructs Hansard JSON information

                workingHansardLog = {}
                workingHansardLog["parliament"] = self.translator.convertDateToUKParlSess(dateH, "Parliament")
                workingHansardLog["date"] = dateH
                workingHansardLog["id"] = ""
                workingHansardLog["session"] = self.translator.convertDateToUKParlSess(dateH, "Session")
                workingHansardLog["url"] = ""
                workingHansardLog["original_url"] = ""

                workingStatements = []

                if k["publicwhip"]["latest"]=="ignore": # some procedural recordings in the data (eg. swearing in of a new government) must be handled here with a manual flag
                    workingSpeech = {}
                    workingSpeech["time"] = ""
                    workingSpeech["heading"]= ""
                    workingSpeech["topic"]= ""
                    workingSpeech["url"]=""
                    workingSpeech["attribution"]=""
                    workingSpeech["text"]=""
                    workingStatements=[workingSpeech]
                    workingHansardLog["statements"] = copy.deepcopy(workingStatements)
                    output = open((os.path.join(os.getcwd(), "data_uk", str(dateH), (str(dateH) + '.pkl'))), 'wb')
                    pickle.dump(workingHansardLog, output)
                    output.close() # writes a dummy file
                    return None
                    
                    
            
                for speechNumber in range(len(k["publicwhip"]["speech"])):
                    workingSpeech = {}
 
                    if "nospeaker" in list(k["publicwhip"]["speech"][speechNumber].keys()) or "speakername" not in list(k["publicwhip"]["speech"][speechNumber].keys()):
                        pass
                    
                    else:
                        speechTime = copy.deepcopy(k["publicwhip"]["speech"][speechNumber]["time"])
                        workingSpeech["time"] = speechTime
                        workingSpeech["heading"]= ""
                        workingSpeech["topic"]= ""
                        try: 
                            workingSpeech["url"]= copy.deepcopy(k["publicwhip"]["speech"][speechNumber]["url"])
                        except KeyError:
                            workingSpeech["url"]=""
                        
                        # politician data
                        speakerName = copy.deepcopy(k["publicwhip"]["speech"][speechNumber]["speakername"])
                        speakerID =  copy.deepcopy(k["publicwhip"]["speech"][speechNumber]["speakerid"])

                        workingSpeech["attribution"]=speakerName
                        
                        if speakerName in ["Several hon. Members", "Hon. Members", "Speaker", "Mr. Speaker", "Madam Speaker", "Mr. Deputy Speaker", "Madam Deputy Speaker", "unknown"]:
                            pass
                        else:
                            workingSpeech["politician"] = {}
                            workingSpeech["politician"]["name"]=self.translator.convertUKName(str(dateH), speakerID, "Fullname")
                            workingSpeech['politician']['riding']=self.translator.convertUKName(str(dateH), speakerID, "Riding")
                            workingSpeech['politician']['party']=self.translator.convertUKName(str(dateH), speakerID, "Party")
                            workingSpeech['politician']['member_id']=""
                            workingSpeech['politician']['id']=speakerID
                            workingSpeech["politician"]["url"] = ""
                        
                        # text of speech
                        # note that using toJSON as a workaround for lxml/unicode issues (bug as of July 2013) creates problems here when more than one
                        # "honourable friend" phrase is referenced in a given speech
                        # xml parsing of speeches should be rewritten once this bug is addressed
                        # for the moment, honfriend class phrase tags are simply stripped before processing
                        
                        gather = []
                        try:
                            speechRaw = copy.deepcopy(k["publicwhip"]["speech"][speechNumber]["p"])
                        except KeyError:
                            print (k["publicwhip"]["speech"][speechNumber])

                        if isinstance(speechRaw, list):
                            for speechComponentNumber in range(len(speechRaw)):
                                try:
                                    gather.append(speechRaw[speechComponentNumber]["$t"])
                                except KeyError:
                                    try:
                                        gather.append(speechRaw[speechComponentNumber]["phrase"]["$t"])
                                    except TypeError:
                                        try:
                                            gather.append(speechRaw[speechComponentNumber]['phrase'][0]["$t"])
                                            gather.append(speechRaw[speechComponentNumber]['phrase'][1]["$t"])
                                        except:
                                            print ("KeyError 3")
                                    except KeyError:
                                        print (speechRaw[speechComponentNumber])
                                        print("KeyError4")
                                        
                        elif isinstance(speechRaw, dict):
                            try:
                                gather.append(speechRaw["$t"])
                            except KeyError:
                                try:
                                    gather.append(speechRaw["phrase"]["$t"])
                                except KeyError:
                                    print (speechRaw)
                                    print(speechRaw.keys())
                                

                        workingSpeech["text"] = "".join(gather)
                        workingStatements.append(copy.deepcopy(workingSpeech))

                workingHansardLog["statements"] = copy.deepcopy(workingStatements)

               # return workingHansardLog # for testing
            
                output = open((os.path.join(os.getcwd(), "data_uk", str(dateH), (str(dateH) + '.pkl'))), 'wb')
                pickle.dump(workingHansardLog, output)
                output.close()
                        
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
            pkl_file = open((os.path.join(os.getcwd(), "data_uk", dateH, trueFilename)), 'rb')
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
            originalList = os.listdir((os.path.join(os.getcwd(), "data_uk", str(dateH))))
            # Lists files in the date directory
        except OSError:
            raise HansardImportDateError("Invalid date.")

        return originalList


