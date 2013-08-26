#####
## Processor for JSON Hansard output from openparliament.ca
## Requires Python 3.2
## tanya.whyte@mail.utoronto.ca
## 2013-02-17
##      analysis.py 
##      General analysis classes for both Canada and UK Hansard
#####


import hansardprocess
import parenthansard
import hansardIO
import UKImport
import csv
import os
import copy
import pylab
import textanalysis


class IO(object):
    def __init__(self):
        pass

    def CSVOutput(self, data, keys, filename="SHM.csv"):
        '''Outputs a CSV of raw SHM data according to lst(keys)
        '''
        
        toCSV = []

        f = open(filename, 'w', newline='')
        write = csv.writer(f)
        write.writerow(keys)
        
        for i in data:
            testList = []
            testList.append(i)
            collectList = []
            for field in len(keys):
                collectList.append(i.getData(keys[field]))
            write.writerow(collectList)
            
            
            #dictConstruct = {}
            #testList = []
            #testList.append(i)
            #dictConstruct = dict([("date", i.hansardDate), ("parliament", i.parliament), ("session", i.session), ("oh", len(self.AnalysisProcessor.refineSearch("statement", "oh, oh!", testList)))])
            #toCSV.append(dictConstruct)
        #keys = ['date', 'parliament', 'session', 'oh']
        #f = open(filename, 'wb')
        #dict_writer = csv.DictWriter(f, keys)
        #dict_writer.writeheader()
        #dict_writer.writerows(toCSV)

class Dates(object):
    def __init__(self, dateStart="1994-01-01", dateEnd="2012-12-31", whichHansard="House"):
		# whichHansard can be House, Committee, or UK
		# this might require some debugging
		
        self.dateStart = dateStart
        self.dateEnd = dateEnd
		self.whichHansard = whichHansard
        self.AnalysisProcessor = hansardprocess.Processor()
        self.yearsList = ["1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", \
        "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
        if whichHansard == "House" or "Committee":
			self.parliamentsList = ["35", "36", "37", "38", "39", "40", "41"]
		elif whichHansard=="UK":
			self.parliamentsList = ["51", "52", "53", "54", "55"]
    
    def NumRecordDays(self, timeFrame):
        '''Return a dict for number of recorded sitting days per year/parliament/session
        Note that session yields the form parliment:session:number (nested dict)
        '''
        if timeFrame not in ["year", "parliament", "session"]:
            raise hansardprocess.ProcessorError("Invalid timeFrame (year/parliament/session).")
            
        daysInSessionPerYear = {}
        daysInSessionPerParliament = {}
        daysInSessionPerSessionPerParliament = {}
        numDays = []
		if self.whichHansard=="House" or "Committee":
			IOObject = hansardIO.HansardImport()
		elif self.whichHansard=="UK":
			IOObject = UKImport.HansardImport()
		activeDict = IOObject.loadHansardDict()
        originalList = []
        newList = []
        filteredList = []

        for j in activeDict: # Makes an unordered list of recorded days without duplicates
            originalList.append(j["date"])
            newList = list(set(originalList))

        if timeFrame == "year":
            for testYear in self.yearsList:
                houseCount = 0
                filteredList = []

                for day in newList:
                    if testYear in day:
                        filteredList.append(day)
                      
                for day in filteredList:
                    try:
						if whichHansard == "House" or "Committee":
						
							for hansardType in ["House"]: # Add committee functionality here
								loadName = IOObject.getTrueFilenames(day, hansardType)
								for fileName in loadName:
									try: 
										hansardDay = IOObject.loadHansardFile(day, fileName)
										if hansardDay["url"][:8] == "/debates": # Checks that the file is not misnamed
											if hansardType == "House":
												houseCount += 1
									except hansardIO.HansardImportDateError:
										pass
						elif whichHansard == "UK":
							loadName = IOObject.getTrueFilenames(day, hansardType="")
								for fileName in loadName:
									try: 
										hansardDay = IOObject.loadHansardFile(day, fileName)
										houseCount += 1
									except hansardIO.HansardImportDateError:
										pass
                        
                    except hansardIO.HansardImportDateError:
                        pass

                daysInSessionPerYear[testYear] = copy.deepcopy(houseCount)
                houseCount = 0

            return daysInSessionPerYear

        if timeFrame == "parliament": # inefficient but works
            for j in self.parliamentsList:
                print (j)
                parliamentsCount = 0
                for day in newList:
                    try:
						if whichHansard == "House" or "Committee":

							for hansardType in ["House"]:
								loadName = IOObject.getTrueFilenames(day, hansardType)
								for fileName in loadName:
									try: 
										hansardDay = IOObject.loadHansardFile(day, fileName)
										if str(hansardDay["parliament"]) == j:
											parliamentsCount += 1
                                
									except hansardIO.HansardImportDateError:
										pass
										
						elif whichHansard == "UK":
							loadName = IOObject.getTrueFilenames(day, hansardType="")
								for fileName in loadName:
									try: 
										hansardDay = IOObject.loadHansardFile(day, fileName)
										if str(hansardDay["parliament"]) == j:
											parliamentsCount += 1
									except hansardIO.HansardImportDateError:
										pass
                            
                    except hansardIO.HansardImportDateError:
                        pass
						
                daysInSessionPerParliament[j] = copy.deepcopy(parliamentsCount)
            return daysInSessionPerParliament

        if timeFrame == "session": # inefficient but works
            for j in self.parliamentsList: 
                print (j)
				if self.whichHansard == "House" or "Parliament":
				
					sessionParlHolder = [0, 0, 0]
					for day in newList:
						try:
							for hansardType in ["House"]:
								loadName = IOObject.getTrueFilenames(day, hansardType)
								for fileName in loadName:
									try: 
										hansardDay = IOObject.loadHansardFile(day, fileName)
										if str(hansardDay["parliament"]) == j:
											if str(hansardDay["session"]) == "1":
												sessionParlHolder[0]+=1
											elif str(hansardDay["session"]) == "2":
												sessionParlHolder[1]+=1
											elif str(hansardDay["session"]) == "3":
												sessionParlHolder[2]+=1
                                
									except hansardIO.HansardImportDateError:
										pass
                            
						except hansardIO.HansardImportDateError:
							pass
					daysInSessionPerSessionPerParliament[j] = dict([("1", copy.deepcopy(sessionParlHolder[0])), ("2", copy.deepcopy(sessionParlHolder[1])), ("3", copy.deepcopy(sessionParlHolder[2]))])

					return daysInSessionPerSessionPerParliament
					
				 elif self.whichHansard == "UK":
					sessionParlHolder= [0, 0, 0, 0, 0]
					for day in newList:
						try:
							loadName = IOObject.getTrueFilenames(day, hansardType)
							for fileName in loadName:
								try: 
									hansardDay = IOObject.loadHansardFile(day, fileName)
									if str(hansardDay["parliament"]) == j:
										if str(hansardDay["session"]) == "1":
											sessionParlHolder[0]+=1
										elif str(hansardDay["session"]) == "2":
											sessionParlHolder[1]+=1
										elif str(hansardDay["session"]) == "3":
											sessionParlHolder[2]+=1
										elif str(hansardDay["session"]) == "4":
											sessionParlHolder[3]+=1
										elif str(hansardDay["session"]) == "5":
											sessionParlHolder[4]+=1
                                
								except hansardIO.HansardImportDateError:
									pass
                            
						except hansardIO.HansardImportDateError:
							pass
					daysInSessionPerSessionPerParliament[j] = dict([("1", copy.deepcopy(sessionParlHolder[0])), ("2", copy.deepcopy(sessionParlHolder[1])), ("3", copy.deepcopy(sessionParlHolder[2])), ("4", copy.deepcopy(sessionParlHolder[3]))), ("5", copy.deepcopy(sessionParlHolder[4])))]

					return daysInSessionPerSessionPerParliament

class Plot(object): # Placeholder for generic plotting
    def __init__(self, dateStart="1994-01-01", dateEnd="2012-12-31", whichHansard="House"):
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.AnalysisProcessor = hansardprocess.Processor()
        self.yearsList = ["1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", \
        "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
		if whichHansard == "House" or "Committee":
			self.parliamentsList = ["35", "36", "37", "38", "39", "40", "41"]
		elif whichHansard=="UK":
			self.parliamentsList = ["51", "52", "53", "54", "55"]


# My analysis
         
class SHM(object):
    def __init__(self, dateStart="1994-01-17", dateEnd="2012-12-31"):
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.AnalysisProcessor = hansardprocess.Processor()
        self.yearsList = ["1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", \
        "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
        self.parliamentsList = ["35", "36", "37", "38", "39", "40", "41"]
        self.SessionLookupTable = dict([("35", dict([("1", "0"), ("2", "1")])), ("36", dict([("1", "2"), ("2", "3")])), ("37", dict([("1", "4"), ("2", "5"), ("3", "6")])), \
        ("38", dict([("1", "7")])), ("39", dict([("1", "8"), ("2", "9")])), ("40", dict([("1", "10"), ("2", "11"), ("3", "12")])), ("41", dict([("1", "13")]))])
        self.SessionOutputLookupTable = dict([(0, 351), (1, 352), (2, 361), (3, 362), (4, 371), (5, 372), (6, 373), (7, 381), (8, 391), (9, 392), (10, 401), (11, 402), (12, 403), (13, 411)])
        
    def SHMData(self, v="oh"):
        '''Returns Oh, oh! data analysis list.  v = oh, ah, hear, all
        '''
        TextAnalysisProcess = textanalysis.HansardText()

        if v == "oh":

            raws = self.AnalysisProcessor.gatherRange("statement", "oh, oh", self.dateStart, self.dateEnd)
            raws.extend(self.AnalysisProcessor.gatherRange("statement", "oh! oh", self.dateStart, self.dateEnd))
            raws.extend(self.AnalysisProcessor.gatherRange("statement", "oh. oh", self.dateStart, self.dateEnd))
            raws.extend(self.AnalysisProcessor.gatherRange("statement", "oh oh", self.dateStart, self.dateEnd))

        elif v == "ah":
            raws = []
            for n in ["shame", "withdraw", "liar", "disgrace", "ah, ah", "ah. ah", "ah! ah", "order"]:  
                raws.extend(self.AnalysisProcessor.gatherRange("statement", n, self.dateStart, self.dateEnd))

        elif v == "hear":

            raws = self.AnalysisProcessor.gatherRange("statement", "hear, hear", self.dateStart, self.dateEnd)
            raws.extend(self.AnalysisProcessor.gatherRange("statement", "hear! hear", self.dateStart, self.dateEnd))
            raws.extend(self.AnalysisProcessor.gatherRange("statement", "hear. hear", self.dateStart, self.dateEnd))

        elif v == "all":
            origRaws = []
            raws = []
            valids = TextAnalysisProcess.findSHMStatements()
            print ("SHMData.All:  Valids loaded ("+ (str(len(valids)))+")")
            origRaws.extend(self.AnalysisProcessor.gatherRange("attribution", "Some hon.", self.dateStart, self.dateEnd))
            for instance in origRaws:
                for goodWord in valids:
                    if goodWord == instance.getData("statement"):
                        raws.append(instance)
        
        return raws

    def SHMPerYearWeighted(self, v = "oh"):
        '''Returns a list of weighted SHM for years start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerYear = q.NumRecordDays("year")
        raws = self.SHMData(v)

        print ("SHMData loaded.  Processing (v = " + v + ")")

        output = [0] * 19
        
        for instance in raws:
            workingDate = instance.getData("hansardDate")
            for j in range(len(self.yearsList)):
                if self.yearsList[j] in workingDate:
                    output[j] += 1

        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for k in range(len(self.yearsList)):
            s = (workingList[k])
            d = (recordsPerYear[self.yearsList[k]])
            
            finalOutput.append(s/d)

        return finalOutput
    

    def SHMPerParliamentWeighted(self, v = "oh"):
        '''Returns a list of day weighted SHM for parliament start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerParliament = q.NumRecordDays("parliament")
        raws = self.SHMData(v)

        print ("Data loaded.  Processing.")

        output = [0] * 7
        
        for instance in raws:
            workingParl = str(instance.getData("parliament"))
            for j in range(len(self.parliamentsList)):
                if self.parliamentsList[j] in workingParl:
                    output[j] += 1

        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for k in range(len(self.parliamentsList)):
            s = (workingList[k])
            d = (recordsPerParliament[self.parliamentsList[k]])
            
            finalOutput.append(s/d)

        return finalOutput

    def SHMPerSessionWeighted(self, v="oh"):
        '''Returns a list of day weighted SHM for parliament start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerSession = q.NumRecordDays("session")
        raws = self.SHMData(v)

        print ("Data loaded.  Processing.")

        output = [0] * 14
        
        for instance in raws:
            workingParl = str(instance.getData("parliament"))
            workingSession = str(instance.getData("session"))
           
            code = int(self.SessionLookupTable[workingParl][workingSession])
            output[code] += 1
            
        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for i in range (len(workingList)):
            s = (workingList[i])
            n = str(self.SessionOutputLookupTable[i])
            d = (recordsPerSession[n[0:2]][n[2]])
            finalOutput.append(s/d)

        return finalOutput

    def SHMStatementsPerSessionWeighted(self):
        '''Returns a list of day weighted SHM for parliament start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerSession = q.NumRecordDays("session")
        raws = self.AnalysisProcessor.gatherRange("statement", "", self.dateStart, self.dateEnd)

        print ("Data loaded.  Processing.")

        output = [0] * 14
        
        for instance in raws:
            workingParl = str(instance.getData("parliament"))
            workingSession = str(instance.getData("session"))
           
            code = int(self.SessionLookupTable[workingParl][workingSession])
            output[code] += 1
            
        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for i in range (len(workingList)):
            s = (workingList[i])
            n = str(self.SessionOutputLookupTable[i])
            d = (recordsPerSession[n[0:2]][n[2]])
            finalOutput.append(s/d)

        return finalOutput

    def SHMStatementsPerYearWeighted(self):
        '''Returns a list of weighted all statements for years start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerYear = q.NumRecordDays("year")
        raws = self.AnalysisProcessor.gatherRange("statement", "", self.dateStart, self.dateEnd)

        print ("Statements data loaded.  Processing.")

        output = [0] * 19
        
        for instance in raws:
            workingDate = instance.getData("hansardDate")
            for j in range(len(self.yearsList)):
                if self.yearsList[j] in workingDate:
                    output[j] += 1

        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for k in range(len(self.yearsList)):
            s = (workingList[k])
            d = (recordsPerYear[self.yearsList[k]])
            
            finalOutput.append(s/d)

        return finalOutput

    def SHMStatementsPerParliamentWeighted(self):
        '''Returns a list of day weighted SHM for parliament start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerParliament = q.NumRecordDays("parliament")
        raws = self.AnalysisProcessor.gatherRange("statement", "", self.dateStart, self.dateEnd)

        print ("Data loaded.  Processing.")

        output = [0] * 7
        
        for instance in raws:
            workingParl = str(instance.getData("parliament"))
            for j in range(len(self.parliamentsList)):
                if self.parliamentsList[j] in workingParl:
                    output[j] += 1

        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for k in range(len(self.parliamentsList)):
            s = (workingList[k])
            d = (recordsPerParliament[self.parliamentsList[k]])
            
            finalOutput.append(s/d)

        return finalOutput
           
    def PlotSHMPerYearWeighted(self, title, x_label, y_label):
        """
        Plots!
        """
        x = []
        for year in self.yearsList:
            x.append(int(year))
        pylab.xlim([1993, 2013])
        pylab.xticks(range(1993, 2013))
        pylab.ylim([0.0, 3.5])
        pylab.plot(x, self.SHMPerYearWeighted())
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotStatementsPerYearWeighted(self, title, x_label, y_label):
        """
        Plots!
        """
        x = []
        for year in self.yearsList:
            x.append(int(year))
        pylab.xlim([1993, 2013])
        pylab.xticks(range(1993, 2013))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, self.SHMStatementsPerYearWeighted(), color = "red")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotSHMPerParliamentWeighted(self, title, x_label, y_label):
        """
        Plots!
        """
        x = []
        for p in self.parliamentsList:
            x.append(int(p))
        #pylab.xlim([1993, 2013])
        #pylab.xticks(range(1993, 2013))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, self.SHMPerParliamentWeighted(), color = "blue")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotStatementsPerParliamentWeighted(self, title, x_label, y_label):
        """
        Plots!
        """
        x = []
        for p in self.parliamentsList:
            x.append(int(p))
        #pylab.xlim([1993, 2013])
        #pylab.xticks(range(1993, 2013))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, self.SHMStatementsPerParliamentWeighted(), color = "red")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotSHMPerSessionWeighted(self, title, x_label, y_label):
        """
        Plots!
        """
        x = []
        for p in range(1, 15):
            x.append(int(p))
        #pylab.xlim([1993, 2013])
        pylab.xticks(range(1, 15))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, self.SHMPerSessionWeighted(), color = "blue")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotStatementsPerSessionWeighted(self, title, x_label, y_label):
        """
        Plots!
        """
        x = []
        for p in range(1, 15):
            x.append(int(p))
        #pylab.xlim([1993, 2013])
        pylab.xticks(range(1, 15))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, self.SHMStatementsPerSessionWeighted(), color = "red")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    
    def PlotSHMPerStatementVsSession(self, title="Ohs Per Statement vs Session", x_label="Parliament:Session Scale", y_label="OhsPerStatement"):
        """
        Plots!
        """
        x = []
        for p in range(1, 15):
            x.append(int(p))
        y = []
        statements = self.SHMStatementsPerSessionWeighted()
        ohs = self.SHMPerSessionWeighted()

        for i in range(len(statements)):
            y.append((ohs[i]/statements[i]))
        
        #pylab.xlim([1993, 2013])
        pylab.xticks(range(1, 15))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, y, color = "purple")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotSHMPerStatementVsYear(self, title="Ohs Per Statement vs Year", x_label="Year", y_label="OhsPerStatement"):
        """
        Plots!
        """
        x = []
        for year in self.yearsList:
            x.append(int(year))
        y = []
        statements = self.SHMStatementsPerYearWeighted()
        ohs = self.SHMPerYearWeighted()

        for i in range(len(statements)):
            y.append((ohs[i]/statements[i]))
        
        pylab.xlim([1993, 2013])
        pylab.xticks(range(1993, 2013))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, y, color = "purple")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotSHMMultiplotPerStatement(self, title="Ohs Per Statement, Hears Per Statement, Others Per Statement vs Session", x_label="Parliament:Session Scale", y_label="PerStatement"):
        """
        Plots!
        """
        x = []
        for p in range(1, 15):
            x.append(int(p))
            
        y = []
        statements = self.SHMStatementsPerSessionWeighted()
        ohs = self.SHMPerSessionWeighted(v="oh")

        for i in range(len(statements)):
            y.append((ohs[i]/statements[i]))

        #z = []
        #ohs1 = self.SHMPerSessionWeighted(v="ah")

        #for i in range(len(statements)):
            #z.append((ohs1[i]/statements[i]))

        q = []
        ohs2 = self.SHMPerSessionWeighted(v="hear")

        for i in range(len(statements)):
            q.append((ohs2[i]/statements[i]))


        #pylab.xlim([1993, 2013])
        pylab.xticks(range(1, 15))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, y, color = "purple", label = "Ohs")
        #pylab.plot(x, z, color = "green", label = "Ahs/Others")
        pylab.plot(x, q, color = "red", label = "Hears")
        pylab.legend()
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

class Speaker(object):
    def __init__(self, dateStart="1994-01-17", dateEnd="2012-12-31"):
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.AnalysisProcessor = hansardprocess.Processor()
        self.yearsList = ["1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", \
        "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
        self.parliamentsList = ["35", "36", "37", "38", "39", "40", "41"]
        self.SessionLookupTable = dict([("35", dict([("1", "0"), ("2", "1")])), ("36", dict([("1", "2"), ("2", "3")])), ("37", dict([("1", "4"), ("2", "5"), ("3", "6")])), \
        ("38", dict([("1", "7")])), ("39", dict([("1", "8"), ("2", "9")])), ("40", dict([("1", "10"), ("2", "11"), ("3", "12")])), ("41", dict([("1", "13")]))])
        self.SessionOutputLookupTable = dict([(0, 351), (1, 352), (2, 361), (3, 362), (4, 371), (5, 372), (6, 373), (7, 381), (8, 391), (9, 392), (10, 401), (11, 402), (12, 403), (13, 411)])
        self.SHMAnalysis = SHM()

    def SpeakerData(self, v="Order"):
        '''Returns Speaker data analysis list.  v = oh, ah, hear
        '''

        if v == "Order":

            
            listCleaned = []
            raws = self.AnalysisProcessor.gatherRange("statement", "Order, ", self.dateStart, self.dateEnd, cs = "True")
            raws.extend(self.AnalysisProcessor.gatherRange("statement", "Order. ", self.dateStart, self.dateEnd, cs = "True"))

            for i in raws:
                if "Standing Order" in i.getData("statement"):
                    pass
                else:
                    listCleaned.append(i)

        return listCleaned

    def SpeakerPerYearWeighted(self):
        '''Returns a list of weighted SHM for years start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerYear = q.NumRecordDays("year")
        raws = self.SpeakerData()

        print ("Speaker data loaded.  Processing.")

        output = [0] * 19
        
        for instance in raws:
            workingDate = instance.getData("hansardDate")
            for j in range(len(self.yearsList)):
                if self.yearsList[j] in workingDate:
                    output[j] += 1

        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for k in range(len(self.yearsList)):
            s = (workingList[k])
            d = (recordsPerYear[self.yearsList[k]])
            
            finalOutput.append(s/d)

        return finalOutput

    def SpeakerStatementsPerYearWeighted(self):
        '''Returns a list of weighted all statements for years start to end, suitable for plotting
        '''
        q = Dates()
        recordsPerYear = q.NumRecordDays("year")
        raws = self.AnalysisProcessor.gatherRange("statement", "", self.dateStart, self.dateEnd)

        print ("Data loaded.  Processing.")

        output = [0] * 19
        
        for instance in raws:
            workingDate = instance.getData("hansardDate")
            for j in range(len(self.yearsList)):
                if self.yearsList[j] in workingDate:
                    output[j] += 1

        workingList = copy.deepcopy(output)
        finalOutput = []
        
        for k in range(len(self.yearsList)):
            s = (workingList[k])
            d = (recordsPerYear[self.yearsList[k]])
            
            finalOutput.append(s/d)

        return finalOutput

    def PlotSpeakerPerStatementVsYear(self, title="Speaker: Order Per Statement vs Year", x_label="Year", y_label="OrdersPerStatement"):
        """
        Plots!
        """
        x = []
        for year in self.yearsList:
            x.append(int(year))
        y = []
        statements = self.SpeakerStatementsPerYearWeighted()
        ohs = self.SpeakerPerYearWeighted()

        for i in range(len(statements)):
            y.append((ohs[i]/statements[i]))
        
        pylab.xlim([1993, 2013])
        pylab.xticks(range(1993, 2013))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, y, color = "purple")
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()

    def PlotSHMSpeakerPerStatementVsYear(self, title="Interruptions Per Statement, Speaker: Order per Statement vs Year", x_label="Year", y_label="PerStatement"):
        """
        Plots!
        """
        x = []
        for year in self.yearsList:
            x.append(int(year))

        y = []
        statements = self.SpeakerStatementsPerYearWeighted()
        ohs = self.SpeakerPerYearWeighted()
            
        z = []
        ohs2 = self.SHMAnalysis.SHMPerYearWeighted(v="all")

        for i in range(len(statements)):
            y.append((ohs[i]/statements[i]))
            z.append((ohs2[i]/statements[i]))

        pylab.xlim([1993, 2013])
        pylab.xticks(range(1993, 2013))
        #pylab.ylim([0.0, 3.5])
        pylab.plot(x, y, color = "purple", linestyle='--', marker='o', label = "Orders")
        pylab.plot(x, z, color = "green", linestyle='--', marker='o', label = "Interruptions")
        #pylab.plot(x, q, color = "red", label = "Hears")
        pylab.legend()
        pylab.title(title)
        pylab.xlabel(x_label)
        pylab.ylabel(y_label)
        pylab.show()
    

    
    
class standsUp(object):
	def __init__(self):
		# write me!
        pass
                    
                    
            
class compare(object):
	def __init__(self):
		# write me!
        pass

    
