### Correction functions!  For debugging purposes only.

import hansardprocess
import parenthansard
import hansardIO
import copy

def findBrokens():
    '''Returns names of misnamed Hansard files
    '''
    yearsList = ["1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", \
        "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012"]
    
    IOObject = hansardIO.HansardImport()
    activeDict = IOObject.loadHansardDict()

    originalList = []
    newList = []

    yearsDict = {}

    committeeNamesList = []
    
    
    for j in activeDict:
        originalList.append(j["date"])
        newList = list(set(originalList))
        filteredList = []

    for testYear in yearsList:

        houseCount = 0
        filteredList = []

        for day in newList:
            if testYear in day:
                filteredList.append(day)

        print (testYear)
                
        for day in filteredList:
            try:
                for hansardType in ["House", "Committee"]:
                    loadName = IOObject.getTrueFilenames(day, hansardType)
                    for fileName in loadName:
                        try: 
                            hansardDay = IOObject.loadHansardFile(day, fileName)

                            if hansardDay["url"][:11] == "/committees":
                                if hansardType == "Committee":
                                    committeeNamesList.append(hansardDay["url"][12:22])
                                else:
                                    print ("mismatch " + hansardDay["url"])
                            elif hansardDay["url"][:8] == "/debates":
                                if hansardType == "House":
                                    houseCount += 1
                                else:
                                    print ("mismatch " + hansardDay["url"])
                            else:
                                print ("wtf")
                                print (hansardDay["url"])

                        except hansardIO.HansardImportDateError:
                            print (hansardDay["url"])
                            pass
                
            except hansardIO.HansardImportDateError:
                print (hansardDay["url"])
                pass

        yearsDict[testYear] = [copy.deepcopy(houseCount), filteredList]
        houseCount = 0

    print (list(set(committeeNamesList)))
    return yearsDict

                

    


#def committeeRename(self, dateH):
   # '''Renames committee .pkl files to reflect committee name (4-letter abbreviation code)
   # Temp function for after when directories get fixed
   # '''
   # try:
   #     activeDict # Test if there is already an activeDict loaded
   # except:
   #     if os.path.isfile(("HansardDict" + '.pkl')):
   #     activeDict = self.loadHansardDict("HansardDict")
   # for i in activeDict:
    #    if i["date"] == dateH:
            
