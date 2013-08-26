#####
## Processor for JSON Hansard output from openparliament.ca
## Requires Python 3.2
## tanya.whyte@mail.utoronto.ca
## 2013-07-27
##      textanalysis.py 
##      Text analysis classes
#####

import hansardprocess
import parenthansard
import hansardIO
#import analysis
import UKImport

class HansardText(object):
    def __init__(self, dateStart="1994-01-17", dateEnd="2012-12-31", whichHansard="House"):
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.Process = hansardprocess.Processor()
        self.yearsList = ["1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", \
        "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
		self.whichHansard = whichHansard
		if self.whichHansard == "House" or "Committee":
		
			self.parliamentsList = ["35", "36", "37", "38", "39", "40", "41"]
			self.SessionLookupTable = dict([("35", dict([("1", "0"), ("2", "1")])), ("36", dict([("1", "2"), ("2", "3")])), ("37", dict([("1", "4"), ("2", "5"), ("3", "6")])), \
			("38", dict([("1", "7")])), ("39", dict([("1", "8"), ("2", "9")])), ("40", dict([("1", "10"), ("2", "11"), ("3", "12")])), ("41", dict([("1", "13")]))])
			self.SessionOutputLookupTable = dict([(0, 351), (1, 352), (2, 361), (3, 362), (4, 371), (5, 372), (6, 373), (7, 381), (8, 391), (9, 392), (10, 401), (11, 402), (12, 403), (13, 411)])
        elif self.whichHansard == "UK":
			self.parliamentsList = ["51", "52", "53", "54", "55"]

    def findSHMStatements(self):
        '''Returns a list of all the kinds of things Members say, cleaned up
        '''
    
        raws = self.Process.gatherRange("attribution", "Some hon.", self.dateStart, self.dateEnd)
        outputList = []
        cleanedList = []
        urlsList = []

        print ("Members statements loaded.  Processing.")
        
        for words in raws:
            if words.getData("statement") in outputList:
                pass
            else:
                outputList.append(words.getData("statement"))

        for i in outputList:
            badCount = 0
            for j in ["agreed", "no", "yes", "yea", "nay", "clause", "mace", "passed", "motion", "speaker", "translation", "bill", "english", "conclusion", "\n"]:
                if j in i.lower():
                    badCount += 1
            if badCount == 0:
                cleanedList.append(i)
            
        return cleanedList

    def findSpeakerStatements(self):
        '''Returns a list of all the kinds of things the Speakers say, cleaned up
        '''
    
        raws = self.Process.gatherRange("attribution", "Speaker", self.dateStart, self.dateEnd)
        outputList = []
        cleanedList = []
        urlsList = []
        outputList2 = []

        print ("Data loaded.  Processing.")

        outputList2 = self.Process.refineSearch("statement", "Order.", raws, cs = "True")
        outputList2.extend(self.Process.refineSearch("statement", "Order,", raws, cs = "True"))

        for words in outputList2:
            if words.getData("statement") in outputList:
                pass
            else:
                outputList.append(words.getData("statement"))

        for i in outputList:
            badCount = 0
            for j in ["Standing Order"]:
                if j in i.lower():
                    badCount += 1
            if badCount == 0:
                cleanedList.append(i)
            
        return cleanedList

    #def checkSHMs(self):
        #'''For visually checking variant SHMData outputs
        #'''
        #x = analysis.SHM()
        #testList = x.SHMData()
        

    
    

    
