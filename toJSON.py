#toJSON
#======

# A python parser from XML to JSON
# Cloned from https://github.com/cwandrews/toJSON


from lxml import objectify
try: import simplejson as json
except ImportError: import json

# This follows google's rules for conversion of XML to JSON

def iterNodes(node, parentDict):
	nodeDict = {}
	try:
		nodeDict.update(node.attrib)
	except AttributeError:
		pass
	if node.text != None:
		nodeDict['$t'] = node.text
	
	for i in node.iterchildren():
		childDict = {}
		newDict = {}
		newDict = iterNodes(i, childDict)
		newList = []
		if i.tag in nodeDict:
			try:
				nodeDict[i.tag].append(newDict[i.tag])
			except:
				newList.append(nodeDict[i.tag])
				nodeDict[i.tag] = newList
				nodeDict[i.tag].append(newDict[i.tag])
		else:
			nodeDict.update(newDict)
	tagList = node.tag.split(':')
	namespace = '$'.join(tagList)
	parentDict[namespace] = nodeDict
	return parentDict

def parseXML(xmlFile):
	with open(xmlFile) as f:
		xml = f.read()

	root = objectify.fromstring(xml)
	
	emptyDict = {}
	parsedDict = iterNodes(root, emptyDict)
	return json.dumps(parsedDict)
