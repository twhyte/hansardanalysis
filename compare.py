#####
## Hansard Analysis Package
## Requires Python 3.2
## tanya.whyte@mail.utoronto.ca
## Current 2013-08-20
##      compare.py
##      Comparative analysis and plots
##      
#####

import hansardprocess
import parenthansard
import hansardIO
import UKImport
import csv
import os
import copy
import matplotlib.pyplot as plt
import textanalysis
import datetime
import analysis
from scipy import stats
import numpy as np

##

def dateHelper(dateStr):
    '''Converts a string yyyy-mm-dd into a datetime.date object'''
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

class comparativeAnalysis(object):
    def __init__(self, dateStart="1994-01-17", dateEnd="2012-12-31"):
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.UKProcessor=hansardprocess.Processor(hansardType="UK")
        self.CanProcessor=hansardprocess.Processor()
        self.yearsList = ["1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", \
        "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
        self.CanParliamentsList = ["35", "36", "37", "38", "39", "40", "41"]
        self.CanSessionLookupTable = dict([("35", dict([("1", "0"), ("2", "1")])), ("36", dict([("1", "2"), ("2", "3")])), ("37", dict([("1", "4"), ("2", "5"), ("3", "6")])), \
        ("38", dict([("1", "7")])), ("39", dict([("1", "8"), ("2", "9")])), ("40", dict([("1", "10"), ("2", "11"), ("3", "12")])), ("41", dict([("1", "13")]))])
        self.CanSessionOutputLookupTable = dict([(0, 283), (1, 165), (2, 246), (3, 133), (4, 213), (5, 153), (6, 55), (7, 160), (8, 176), (9, 118), (10, 13), (11, 128), (12, 149), (13, 200)])
        self.UKParliamentsList= ["51", "52", "53", "54", "55"]
        self.UKSessionLookupTable=dict([("51", dict([("2", "0"), ("3", "1"), ("4", "2"), ("5", "3")])), ("52", dict([("1", "4"), ("2", "5"), ("3", "6"), ("4", "7")])), \
        ("53", dict([("1", "8"), ("2", "9"), ("3", "10"), ("4", "11")])), \
        ("54", dict([("1", "12"), ("2", "13"), ("3", "14"), ("4", "15"), ("5", "16")])), ("55", dict([("1", "17"), ("2", "18")]))])
        self.UKSessionOutputLookupTable = dict([(0, 132), (1, 159), (2, 142), (3, 86), (4, 236), (5, 148), (6, 165), (7, 79), (8, 197), (9, 162), (10, 157), \
        (11, 65), (12, 205), (13, 146), (14, 165), (15, 136), (16, 69), (17, 291), (18, 89)])
        self.SHM=analysis.SHM()
        self.SHMUK=analysis.SHMUK()
        self.CanSpeaker=analysis.Speaker()
        self.UKSpeaker=analysis.UKSpeaker()

    def statsCan(self, source, value="all"):
        '''Value can be slope, intercept, r_value, p_value, stderr, all.  Source = House or Speaker'''
        if source=="House":
            y=self.SHM.SHMPerYearWeighted(v="all")
        if source=="Speaker":
            y=self.CanSpeaker.SpeakerPerYearWeighted()
        x=range(len(self.yearsList))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        if value == "slope":
            return slope
        elif value == "intercept":
            return intercept
        elif value=="r_value":
            return r_value
        elif value=="p_value":
            return p_value
        elif value == "stderr":
            return stderr
        else:
            return [slope, intercept, r_value, p_value, std_err]

    def statsCanSession(self, source, value="all"):
        '''Value can be slope, intercept, r_value, p_value, stderr, all.  Source = House or Speaker'''
        if source=="House":
            y=self.SHM.SHMPerSessionWeighted(v="all")
        if source=="Speaker":
            y=self.CanSpeaker.SpeakerPerSessionWeighted()
        x=range(14)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        if value == "slope":
            return slope
        elif value == "intercept":
            return intercept
        elif value=="r_value":
            return r_value
        elif value=="p_value":
            return p_value
        elif value == "stderr":
            return stderr
        else:
            return [slope, intercept, r_value, p_value, std_err]
         
    def statsUK(self, source, value='all'):
        '''Value can be slope, intercept, r_value, p_value, stderr, all.  Source = House or Speaker'''
        if source=="House":
            y=self.SHMUK.SHMUKPerYearWeighted()
        if source=="Speaker":
            y=self.UKSpeaker.SpeakerPerYearWeighted()
        x=range(len(self.yearsList))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        if value == "slope":
            return slope
        elif value == "intercept":
            return intercept
        elif value=="r_value":
            return r_value
        elif value=="p_value":
            return p_value
        elif value == "stderr":
            return stderr
        else:
            return [slope, intercept, r_value, p_value, std_err]

    def statsUKSession(self, source, value='all'):
        '''Value can be slope, intercept, r_value, p_value, stderr, all.  Source = House or Speaker'''
        if source=="House":
            y=self.SHMUK.SHMUKPerSessionWeighted()
        if source=="Speaker":
            y=self.UKSpeaker.SpeakerPerSessionWeighted()
        x=range(19)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        if value == "slope":
            return slope
        elif value == "intercept":
            return intercept
        elif value=="r_value":
            return r_value
        elif value=="p_value":
            return p_value
        elif value == "stderr":
            return stderr
        else:
            return [slope, intercept, r_value, p_value, std_err]

    def plotCanadaYear(self, title="Canadian Parliament:  Average Interruptions and Speaker Orders Per Day, By Year", x_label="Year", y_label="Average Number of Statements"):
        """
        Plots!
        """
        #x = []
        #for year in self.yearsList:
        #    x.append(int(year))
        x=range((len(self.yearsList)))

        y = self.CanSpeaker.SpeakerPerYearWeighted()
        z = self.SHM.SHMPerYearWeighted(v="all")
        ticks = copy.deepcopy(self.yearsList)
        x=range((len(ticks)))

        #plt.xlim([0, 19])
        
        plt.ylim([0.0, 10.0])
        plt.xticks=((np.arange(len(ticks))), ticks)
        plt.plot(x, y, color = "purple", marker='o', label = "Orders")
        plt.plot(x, z, color = "red", marker='o', label = "Interruptions")

        stats = self.statsCan("Speaker")
        n=range(0,20)
        order_fit = []
        for q in x:
            order_fit.append((stats[1])+(stats[0]*q))

        r_sq = (stats[2])**2
        plt.plot(x, order_fit, color='green', linestyle='--', label="Slope: "+str(stats[0]))
        
        #plt.annotate(('r^2 = ' + str(r_sq)))
        #plt.annotate('p_value = '+(str(stats[3])))
        
        stats2 = self.statsCan("House")
        house_fit = []
        for q in x:
            house_fit.append((stats2[1])+(stats2[0]*q))
        r_sq2 = (stats2[2])**2
        plt.plot(x, house_fit, color='orange', linestyle='--', label="Slope: "+str(stats2[0]))
        #plt.annotate(('r^2 = ' + str(r_sq2)), xy=(5,100), xycoords='axes points')
        #plt.annotate('p_value = '+(str(stats2[3])), xy=(5,200), xycoords='axes points') # stopped here--do rounding.
        
        plt.legend()
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()


    def plotUKYear(self, title="UK Parliament:  Average Interruptions and Speaker Orders Per Day, By Year", x_label="Year", y_label="Average Number of Statements"):
        """
        Plots!
        """
        #x = []
        #for year in self.yearsList:
        #    x.append(int(year))
        x=range((len(self.yearsList)))
        ticks = copy.deepcopy(self.yearsList)

        y = self.UKSpeaker.SpeakerPerYearWeighted()
        z = self.SHMUK.SHMUKPerYearWeighted()

        #plt.xlim([0, 20])
        #plt.xticks(arange(19), self.yearsList)
        plt.ylim([0.0, 12.0])
        plt.xticks=((range(len(ticks))), ticks)
        plt.plot(x, y, color = "purple", marker='o', label = "Orders")
        plt.plot(x, z, color = "red", marker='o', label = "Interruptions")

        stats = self.statsUK("Speaker")
        n=range(0,20)
        order_fit = []
        for q in x:
            order_fit.append((stats[1])+(stats[0]*q))

        r_sq = (stats[2])**2
        plt.plot(x, order_fit, color='green', linestyle='--', label="Slope: "+str(stats[0]))
        
        #plt.annotate(('r^2 = ' + str(r_sq)))
        #plt.annotate('p_value = '+(str(stats[3])))
        
        stats2 = self.statsUK("House")
        house_fit = []
        for q in x:
            house_fit.append((stats2[1])+(stats2[0]*q))
        r_sq2 = (stats2[2])**2
        plt.plot(x, house_fit, color='orange', linestyle='--', label="Slope: "+str(stats2[0]))
        
        #plt.annotate(('r^2 = ' + str(r_sq2)), xy=(5,100), xycoords='axes points')
        #plt.annotate('p_value = '+(str(stats2[3])), xy=(5,200), xycoords='axes points') # stopped here--do rounding.
        
        plt.legend()
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()

    def plotCanadaSession(self, title="Canadian Parliament:  Average Interruptions and Speaker Orders Per Day, By Session", x_label="Session", y_label="Average Number of Statements"):

        x = []
        for p in range(1, 15):
            x.append(int(p))
        plt.xticks(x)
        plt.ylim([0.0, 10.0])

        y = self.CanSpeaker.SpeakerPerSessionWeighted()
        z = self.SHM.SHMPerSessionWeighted(v="all")

        stats = self.statsCanSession("Speaker")
        n=range(0,14)
        order_fit = []
        for q in x:
            order_fit.append((stats[1])+(stats[0]*q))

        r_sq = (stats[2])**2
        plt.plot(x, order_fit, color='green', linestyle='--', label="Slope: "+str(stats[0]))
        
        #plt.annotate(('r^2 = ' + str(r_sq)))
        #plt.annotate('p_value = '+(str(stats[3])))
        
        stats2 = self.statsCanSession("House")
        house_fit = []
        for q in x:
            house_fit.append((stats2[1])+(stats2[0]*q))
        r_sq2 = (stats2[2])**2
        plt.plot(x, house_fit, color='orange', linestyle='--', label="Slope: "+str(stats2[0]))
        #plt.annotate(('r^2 = ' + str(r_sq2)), xy=(5,100), xycoords='axes points')
        #plt.annotate('p_value = '+(str(stats2[3])), xy=(5,200), xycoords='axes points') # stopped here--do rounding. 
        
        plt.plot(x, y, color = "purple", linestyle='--', marker='o', label = "Orders")
        plt.plot(x, z, color = "blue", linestyle='--', marker='o', label = "Interruptions")
        plt.legend()
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()

    def plotUKSession(self, title="UK Parliament:  Average Interruptions and Speaker Orders Per Day, By Session", x_label="Session", y_label="Average Number of Statements"):

        x = []
        for p in range(0, 2):
            x.append(int(p))
        plt.xticks(range(1, 21))
        plt.ylim([0.0, 15.0])

        y = self.UKSpeaker.SpeakerPerSessionWeighted()
        z = self.SHMUK.SHMUKPerSessionWeighted()

        stats = self.statsUKSession("Speaker")
        n=range(0,20)
        order_fit = []
        for q in x:
            order_fit.append((stats[1])+(stats[0]*q))

        r_sq = (stats[2])**2
        plt.plot(x, order_fit, color='green', linestyle='--', label="Slope: "+str(stats[0]))
        
        #plt.annotate(('r^2 = ' + str(r_sq)))
        #plt.annotate('p_value = '+(str(stats[3])))
        
        stats2 = self.statsUKSession("House")
        house_fit = []
        for q in x:
            house_fit.append((stats2[1])+(stats2[0]*q))
        r_sq2 = (stats2[2])**2
        plt.plot(x, house_fit, color='orange', linestyle='--', label="Slope: "+str(stats2[0]))
        #plt.annotate(('r^2 = ' + str(r_sq2)), xy=(5,100), xycoords='axes points')
        #plt.annotate('p_value = '+(str(stats2[3])), xy=(5,200), xycoords='axes points') # stopped here--do rounding. 
        
        plt.plot(x, y, color = "purple", linestyle='--', marker='o', label = "Orders")
        plt.plot(x, z, color = "blue", linestyle='--', marker='o', label = "Interruptions")
        plt.legend()
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()

    def plotComparativeInterruptions(self, title="UK Parliament and Canadian Parliament:  Average Interruptions Per Day, By Year", x_label="Year", y_label="Average Number of Interruptions"):
        x = []
        for year in self.yearsList:
            x.append(int(year))

        y = self.SHM.SHMPerYearWeighted(v="all")
        z = self.SHMUK.SHMUKPerYearWeighted()

        plt.xlim([1993, 2013])
        plt.xticks(range(1993, 2013))
        plt.ylim([0.0, 10.0])
        plt.plot(x, y, color = "red", linestyle='--', marker='o', label = "Canada")
        plt.plot(x, z, color = "blue", linestyle='--', marker='o', label = "UK")
        plt.legend()
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()

    def plotComparativeSpeaker(self, title="UK Parliament and Canadian Parliament:  Average Speaker Order Statements Per Day, By Year", x_label="Year", y_label="Average Number of Order Statements"):
        x = []
        for year in self.yearsList:
            x.append(int(year))

        y = self.CanSpeaker.SpeakerPerYearWeighted()
        z = self.UKSpeaker.SpeakerPerYearWeighted()

        plt.xlim([1993, 2013])
        plt.xticks(range(1993, 2013))
        plt.ylim([0.0, 10.0])
        plt.plot(x, y, color = "red", linestyle='--', marker='o', label = "Canada")
        plt.plot(x, z, color = "blue", linestyle='--', marker='o', label = "UK")
        plt.legend()
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()

    def allStats(self, export = "no"):
        '''Calculates all statistics for final analysis'''

        finalOutput = {}

        # stats for base relationships
        # Canada - Interruption and Order by year
        canBaseYearHouse=self.statsCan("House")
        canBaseYearSpeaker=self.statsCan("Speaker")
        
        # Canada - Interruption and Order by session
        canBaseSessionHouse=self.statsCanSession("House")
        canBaseSessionSpeaker=self.statsCanSession("Speaker")

        # UK - Interruption and Order by year
        UKBaseYearHouse=self.statsUK("House")
        UKBaseYearSpeaker=self.statsUK("Speaker")

        # UK - Interruption and Order by session
        UKBaseSessionHouse=self.statsUKSession("House")
        UKBaseSessionSpeaker=self.statsUKSession("Speaker")

        print("Base stats calculated.")

        # stats for cross-relationship interruptions/orders
        # Canada, by year
        x=self.SHM.SHMPerYearWeighted(v="all")
        y=self.CanSpeaker.SpeakerPerYearWeighted()
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        crossCanadaYear = copy.deepcopy([slope, intercept, r_value, p_value, std_err])
        
        # Canada, by session
        x=self.SHM.SHMPerSessionWeighted(v="all")
        y=self.CanSpeaker.SpeakerPerSessionWeighted()
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        crossCanadaSession = copy.deepcopy([slope, intercept, r_value, p_value, std_err])
        
        # UK, by year
        x=self.SHMUK.SHMUKPerYearWeighted()
        y=self.UKSpeaker.SpeakerPerYearWeighted()
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        crossUKYear = copy.deepcopy([slope, intercept, r_value, p_value, std_err])
        
        # UK, by session
        x=self.SHMUK.SHMUKPerSessionWeighted()
        y=self.UKSpeaker.SpeakerPerSessionWeighted()
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        crossUKSession = copy.deepcopy([slope, intercept, r_value, p_value, std_err])

        print("Cross stats calculated.")

        # stats for cross-relationship interruptions/orders within speakers' domains
        # first need parameters for speaker tenure in both countries
        canSpeakerList = [(dict([("name", "Gilbert Parent"),("startDate", "1994-01-01"),("endDate", "2001-01-28"), ('ratio', [])])), \
        (dict([("name", "Peter Milliken"),("startDate", "2001-01-29"),("endDate", "2011-06-02"), ('ratio', [])])), \
        (dict([("name", "Andrew Scheer"),("startDate", "2011-06-03"),("endDate", "2012-12-31"), ('ratio', [])]))]
        UKSpeakerList = [(dict([("name", "Betty Boothroyd"),("startDate", "1994-01-01"),("endDate", "2000-10-23")])), \
        (dict([("name", "Michael Martin"),("startDate", "2000-10-24"),("endDate", "2009-05-19")])), \
        (dict([("name", "John Bercow"),("startDate", "2009-05-20"),("endDate", "2012-12-31")]))]

        # Canada
        daysInSessionPerSpeakerCan={}
        statPerSpeakerBinCan={}
        
        interList = self.SHM.SHMPerSessionWeighted()
        orderList = self.CanSpeaker.SpeakerPerSessionWeighted()
        speakersCrossDictCan = {}
        
        for i in range(4):
            canSpeakerList[0]["ratio"].append(interList[i]/orderList[i])

        for i in range(4,13):
            canSpeakerList[1]["ratio"].append(interList[i]/orderList[i])

        canSpeakerList[0]["numsessions"]=4
        canSpeakerList[1]["numsessions"]=9
        canSpeakerList[2]['ratio']=([(interList[-1]/orderList[-1])])
        canSpeakerList[2]["numsessions"]=1

        finalList = []
        gathernames = ["Gilbert Parent"]*4
        gathernames.extend(["Peter Milliken"]*9)
        gathernames.append("Andrew Scheer")
            
        for speaker in range(3):
            for n in range(len(canSpeakerList[speaker]["ratio"])):
                finalList.append(canSpeakerList[speaker]["ratio"][n])
        z_scores=(stats.zscore(finalList))*2
        pvals = stats.norm.sf(z_scores)
        speaker_p_values = dict(zip(gathernames, pvals))
        
##        #UK (old code--needs lots of fixing!)
##        IOObject = UKImport.HansardImport()
##        activeDict = IOObject.loadHansardDict()
##        daysInSessionPerSpeakerUK={}
##        statPerSpeakerBinUK={}
##        
##        originalList = []
##        newList = []
##        filteredList = []
##        
##        for j in activeDict: # Makes an unordered list of recorded days without duplicates
##            dateStr = j["date"]
##            workingDateObject = dateHelper(dateStr)
##            if datetime.date(1994, 1, 1)<workingDateObject<datetime.date(2012, 12, 31):
##                originalList.append(j["date"])
##                newList = list(set(originalList))
##            else:
##                pass
##            
##        for speaker in UKSpeakerList: # How many days per session per speaker bin?
##            testSpeakerStart = dateHelper(speaker["startDate"])
##            testSpeakerEnd = dateHelper(speaker["endDate"])
##            houseCount = 0
##
##            for day in newList:
##                try:
##                    loadName = IOObject.getTrueFilenames(day)
##                    for fileName in loadName:
##                        hansardDay = IOObject.loadHansardFile(day, fileName)
##                        houseCount += 1
##                        
##                except UKImport.HansardImportDateError:
##                    pass
##                                        
##            speakerName = speaker["name"]
##            daysInSessionPerSpeakerUK[(copy.deepcopy(speakerName))] = copy.deepcopy(houseCount)
##            
##            rawsObj=analysis.SHMUK(dateStart=(speaker["startDate"]), dateEnd = (speaker["endDate"]))
##            raws = rawsObj.SHMUKData()
##            SHMUkRaws = len(raws)
##            rawsObj=analysis.UKSpeaker(dateStart=(speaker["startDate"]), dateEnd = (speaker["endDate"]))
##            raws = rawsObj.SpeakerData()
##            UKSpeakerRaws=len(raws)
##            
##            slope, intercept, r_value, p_value, std_err = stats.linregress(UKSpeakerRaws/houseCount,SHMUKRaws/houseCount)
##            statPerSpeakerBinUK[(copy.deepcopy(speakerName))] = [slope, intercept, r_value, p_value, std_err]
##            houseCount = 0
##
##        print ("Speaker domain stats calculated.")
##
##        # stats for comparison between speaker domains
##
##        # Canada and UK Together
##        gather = []
##        gathernames = []
##        for key in list(statPerSpeakerBinCan.keys()):
##            gather.append(statPerSpeakerBinCan[key])
##            gathernames.append(key)
##        for key in list(statPerSpeakerBinUK.keys()):
##            gather.append(statPerSpeakerBinUK[key])
##            gathernames.append(key)
##        pvals = scipy.stats.norm.sf(scipy.stats.zscore(gather))*2
##        speaker_p_values = dict(zip(gathernames, pvals))
##        
##
##        # Canada Vs. UK
##        gather1 = []
##        gather2=[]
##        for key in list(statPerSpeakerBinCan.keys()):
##            gather1.append(statPerSpeakerBinCan[key])
##        for key in list(statPerSpeakerBinUK.keys()):
##            gather2.append(statPerSpeakerBinUK[key])
##        t, prob = stats.ttest_ind(gather1, gather2)
##        speakersTTest = copy.deepcopy([t, prob])

        print ("Speaker domain comparison stats calculated.")
    
        if export == "yes":
            with open('data.csv', 'w', newline='', encoding='utf8') as f:
                writer = csv.writer(f)
                writer.writerows([canBaseYearHouse,canBaseYearSpeaker,UKBaseYearHouse,UKBaseYearSpeaker,\
                canBaseSessionHouse,canBaseSessionSpeaker,UKBaseSessionHouse,UKBaseSessionSpeaker,crossCanadaSession,\
                crossCanadaYear, crossUKSession, crossUKYear, pvals, z_scores])

        print ("canBaseYearHouse= ", canBaseYearHouse)
        print ("canBaseYearSpeaker= ", canBaseYearSpeaker)
        print ("UKBaseYearHouse= ", UKBaseYearHouse)
        print ("UKBaseYearSpeaker= ", UKBaseYearSpeaker)
        print ("canBaseSessionHouse= ", canBaseSessionHouse)
        print ("canBaseSessionSpeaker= ", canBaseSessionSpeaker)
        print ("UKBaseSessionHouse= ", UKBaseSessionHouse)
        print ("UKBaseSessionSpeaker= ", UKBaseSessionSpeaker)
        print ("crossCanadaSession= ", crossCanadaSession)
        print ("crossCanadaYear= ", crossCanadaYear)
        print ("crossUKSession= ", crossUKSession)
        print ("crossUKYear= ", crossUKYear)
        #print ("statPerSpeakerBinCan", statPerSpeakerBinCan)
        #print ("statPerSpeakerBinUK", statPerSpeakerBinUK)
        print ("speaker_p_values", pvals)
        print('speaker z scores = ', z_scores)
        #print ("speakersTTest", speakersTTest)
        
        


         
