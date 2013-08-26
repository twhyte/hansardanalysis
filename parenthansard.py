#####
## Hansard Analysis Package
## Requires Python 3.2
## tanya.whyte@mail.utoronto.ca
## Current 2013-07-23
##      parenthansard.py 
##      Creates parent Hansard objects
##      To do: implement Canadian committees
#####

import hansardIO
import UKImport

class Hansard(object):
    '''hansardDate = str format yyyy-mm-dd, hansardType = "House" or "Committee" or "UK"
        optional: committee = str of committee name, eg. "Agriculture", not implemented
    '''
    def __init__(self, hansardDate, hansardType = "House", committee = ""): 
        if hansardType == "House" or "Committee":
			self.IOObject = hansardIO.HansardImport()
		else:
			self.IOObject = UKImport.HansardImport()
		
        self.hansardDate = hansardDate
        self.hansardType = hansardType
        self.committee = "" # committees not implemented!
        loadName = self.IOObject.getTrueFilenames(self.hansardDate, self.hansardType)
        loadDict = self.IOObject.loadHansardFile(self.hansardDate, loadName[0])
        self.parliament = loadDict["parliament"]
        self.statements = loadDict["statements"]
        self.originalURL = loadDict["original_url"]
        self.URL = loadDict["url"]
        self.session = loadDict["session"]
        self.hansardID = loadDict["id"]
        
    def __str__(self):
        return str(self.hansardDate) + " " + str(self.hansardType) + str(self.committee)

    def getData(self, variable): # helper for returning some variables
        '''Returns the value of self."variable"
        '''
        if variable == "parliament":
            return self.parliament
        elif variable == "statements":
            return self.statements
        elif variable == "originalURL":
            return self.originalURL
        elif variable == "URL":
            return self.URL
        elif variable == "session":
            return self.session
        elif variable == "hansardID":
            return self.hansardID
        elif variable == "hansardDate":
            return self.hansardDate


class HansardRaw(object):
    def __init__(self, parliament, originalURL, session, hansardDate, hansardID, heading, attribution, statementTime, topic, statementURL, politicianName, memberID, party, riding, statement):
        self.parliament = parliament
        self.originalURL = originalURL
        self.session = session
        self.hansardDate = hansardDate
        self.hansardID = hansardID
        self.heading = heading
        self.attribution = attribution
        self.statementTime = statementTime
        self.topic = topic
        self.statementURL = statementURL
        self.politicianName = politicianName
        self.memberID = memberID
        self.party = party
        self.riding = riding
        self.statement = statement

    def __str__(self):
        print(("parliament: " + str(self.parliament) + "\n" + "originalURL: " + self.originalURL))
        print(("session: " + str(self.session) + "\n" + "hansardDate: " + self.hansardDate))
        print(("hansardID: " + str(self.hansardID) + "\n" + "attribution: " + self.attribution))
        print(("statementTime: " + self.statementTime + "\n" + "topic: " + self.topic))
        print(("statementURL: " + self.statementURL + "\n" + "politicianName: " + self.politicianName))
        print(("memberID: " + str(self.memberID) + "\n" + "party: " + self.party))
        print(("riding: " + self.riding + "\n" + "statement: " + "\n" + self.statement))
        return ""

    def getData(self, variable): # helper for returning some variables
        if variable == "parliament":
            return self.parliament
        elif variable == "heading":
            return self.heading
        elif variable == "originalURL":
            return self.originalURL
        elif variable == "URL":
            return self.URL
        elif variable == "session":
            return self.session
        elif variable == "hansardID":
            return self.hansardID
        elif variable == "hansardDate":
            return self.hansardDate
        elif variable == "attribution":
            return self.attribution
        elif variable == "statementTime":
            return self.statementTime
        elif variable == "topic":
            return self.topic
        elif variable == "statementURL":
            return self.statementURL
        elif variable == "politicianName":
            return self.politicianName
        elif variable == "memberID":
            return self.memberID
        elif variable == "party":
            return self.party
        elif variable == "riding":
            return self.riding
        elif variable == "statement":
            return self.statement
        
