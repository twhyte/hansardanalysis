#####
## Hansard Analysis Package
## Requires Python 3.2
## tanya.whyte@mail.utoronto.ca
## Current 2013-07-23
##      hansardprocess.py
##      Searches and processes Hansard objects
##      To do: implement committees
#####

from parenthansard import *
import datetime
import copy

class ProcessorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Processor(object):
    def __init__(self, hansardType="Canada"): # map of the JSON tree for use in processing
        self.topLevel = ["parliament", "session", "hansardDate", "hansardID"]
        self.midLevel = ["topic", "attribution", "heading", "statement"]
        self.lowLevel = ["politicianName", "memberID", "party", "riding"]
        self.hansardType = hansardType

    def find(self, category, data, hansardDay, cs = "False"):
        '''Returns a list of HansardRaw objects for each instance where data (str) occurs in category (str)
        within one Hansard object.  Optional cs="False" (True) for case sensitivity.
        Permitted categories: parliament, session, hansardDate, hansardID, topic, attribution, heading, statement, politicianName, memberID, party, riding
        '''
        
        findList = []
        
        if category in self.topLevel:
            if cs == "False":
                if (str(data)).lower() in (str(hansardDay.getData(category))).lower():
                    for i in hansardDay.statements:
                        try:
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], i['politician']['name'], i['politician']['member_id'], \
                            i['politician']['party'], i['politician']['riding'], i['text'])
                            findList.append(x)
                        except KeyError: # If no politician data in statement, fill related variables with blank strings
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], "", "", \
                            "", "", i["text"])
                            findList.append(x)
                else:
                    pass
            elif cs == "True":
                if (str(data)) in (str(hansardDay.getData(category))):
                    for i in hansardDay.statements:
                        try:
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], i['politician']['name'], i['politician']['member_id'], \
                            i['politician']['party'], i['politician']['riding'], i['text'])
                            findList.append(x)
                        except KeyError: # If no politician data in statement, fill related variables with blank strings
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], "", "", \
                            "", "", i["text"])
                            findList.append(x)
            
                else:
                    pass

        elif category in self.midLevel:
            if cs == "False":
                if category == "statement":
                    category = "text"
                for i in hansardDay.statements:
                    if (str(data)).lower() in (str(i[category])).lower():
                        try:
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], i['politician']['name'], i['politician']['member_id'], \
                            i['politician']['party'], i['politician']['riding'], i['text'])
                            findList.append(x)
                        except KeyError: # If no politician data in statement, fill related variables with blank strings
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], "", "", \
                            "", "", i["text"])
                            findList.append(x)
                    else:
                         pass
            elif cs == "True":
                if category == "statement":
                    category = "text"
                for i in hansardDay.statements:
                    if (str(data)) in (str(i[category])):
                        try:
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], i['politician']['name'], i['politician']['member_id'], \
                            i['politician']['party'], i['politician']['riding'], i['text'])
                            findList.append(x)
                        except KeyError: # If no politician data in statement, fill related variables with blank strings
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], "", "", \
                            "", "", i["text"])
                            findList.append(x)
                    else:
                         pass

        elif category in self.lowLevel:
            if category == "politicianName":
                newCategory = "name"
            elif category == "memberID":
                newCategory = "member_id"
            else:
                newCategory = category
            if cs == "False":
                for i in hansardDay.statements:
                    try:
                        if (str(data)).lower() in ((str(i['politician'][newCategory])).lower()):
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], i['politician']['name'], i['politician']['member_id'], \
                            i['politician']['party'], i['politician']['riding'], i['text'])
                            findList.append(x)
                        else:
                             pass
                    except KeyError:
                        pass
            elif cs == "True":
                for i in hansardDay.statements:
                    try:
                        if (str(data)) in ((str(i['politician'][newCategory]))):
                            x = HansardRaw(hansardDay.parliament, hansardDay.originalURL, hansardDay.session,\
                            hansardDay.hansardDate, hansardDay.hansardID, i["heading"], i["attribution"], i["time"], \
                            i["topic"], i['url'], i['politician']['name'], i['politician']['member_id'], \
                            i['politician']['party'], i['politician']['riding'], i['text'])
                            findList.append(x)
                        else:
                             pass
                    except KeyError:
                        pass

        else:
            raise ProcessorError("Invalid category.")

        return findList


    def gatherRange(self, category, data, dateStart, dateEnd, cs = "False"):
        '''Returns a list of HansardRaw objects for each instance where data (str) occurs in category (str)
        within inclusive range date1-date2 yyyy-mm-dd of Hansard objects.
        Permitted categories: parliament, session, hansardDate, hansardID, topic, attribution, heading, politicianName, memberID, party, riding
        '''
        
        gather = []

        dateS = datetime.date
        dateE = datetime.date
        
        try:
            dateS = datetime.date(int(dateStart[0:4]), int(dateStart[5:7]), int(dateStart[8:10])) # Convert str to datetime.date objects
            dateE = datetime.date(int(dateEnd[0:4]), int(dateEnd[5:7]), int(dateEnd[8:10]))
        except:
            raise ProcessorError("Invalid date (must be valid yyyy-mm-dd).")

        loopDate = copy.deepcopy(dateS)
        dateStepInt = (dateE - dateS).days
        
        for i in range(dateStepInt+1): # Iterate and find over Hansard files
            result = []
            try:
                if self.hansardType =="Canada":
                    hansardDay = Hansard(hansardDate=str(loopDate.isoformat()), hansardType="House")
                elif self.hansardType=="UK":
                    hansardDay = Hansard(hansardDate=str(loopDate.isoformat()), hansardType="UK")
                    
                    
                result = self.find(category, data, hansardDay, cs)
            except (hansardIO.HansardImportDateError, UKImport.HansardImportDateError, IndexError): # No Hansard on this date!
                pass
            dateStepInt += 1
            loopDate += datetime.timedelta(days=1)
            gather.extend(result)

        return gather

    def gatherList(self, category, data, dateList, cs = "False"):
        '''Returns a list of HansardRaw objects for each instance where data (str) occurs in category (str) within dateList
        Permitted categories: parliament, session, hansardDate, hansardID, topic, attribution, heading, politicianName, memberID, party, riding
        '''
        
        gather = []

        for i in dateList: # Iterate and find over Hansard files
            result = []
            try:
                if self.hansardType=="Canada":
                    hansardDay = Hansard(i)
                elif self.hansardType=="UK":
                    hansardDay = Hansard(i, hansardType="UK")
                result = self.find(category, data, hansardDay, cs)
            except hansardIO.HansardImportDateError: # No Hansard on this date!
                pass
            gather.extend(result)

        return gather

    def refineSearch(self, category, data, rawList, cs = "False"):
        '''Returns a list of HansardRaw objects where data (str) occurs in category (str) within existing list of
        HansardRaw objects.  Optional:  cs="False" (True) for case sensitivity.
        Permitted categories: parliament, session, hansardDate, hansardID, topic, attribution, heading, politicianName, memberID, party, riding, statement
        '''

        gather = []

        if category not in ["parliament", 'session', 'hansardDate', 'hansardID', 'topic', 'attribution', 'heading', 'politicianName', 'memberID', 'party', 'riding', "statement"]:
            raise ProcessorError("Invalid category.")

        if cs == "False":
            for i in rawList:
                if (str(data)).lower() in (str(i.getData(category))).lower():
                    gather.append(i)
        if cs == "True":
            for i in rawList:
                if (str(data)) in (str(i.getData(category))):
                    gather.append(i)

        return gather

