from termcolor import colored
import os
from msvcrt import getch
import win32api as w
import win32con as wc
def createLogMessage(msg):
	print(colored("[ LOG ] ", "green") + f"{msg}")

def createWarningMessage(msg):
	print(colored(f"[ WARNING ] ", "yellow") +  f"{msg}")

def createErrorMessage(msg):
	print(colored(f"[ ERROR ] ", "red") + f"{msg}")


def createHelpText(template):
	# Displays a help message from a template 
	# template sample{"description":..., "usage":{"com --par option":...}}


	# The purpose of this function its nothing but to create an standard format of help messages, easy to change all at the same time
	# Description
	print(f"Command's description: {template['description']}")
	if template["usage"] != []:
		print(f"\nUsage:")
		for example in template["usage"]:
			print("\t" + example)
			print("\t\t" + template["usage"][example]+ "\n")

def createBoxTitle(msg):
	print(f"========== {msg} ==========")

def parseData(data):
	defaultVals = {"True":True, "False":False, "None":None, "$cwd$":os.getcwd()}
	
	if data in defaultVals:
		data = defaultVals[data]
	
	else:
		# integer
		try:
			data = int(data)
		except ValueError:
			pass
			
	return data
	


	
	
def waitForKey(key):
	while True:
		char = getch().decode("utf-8")
		if char.lower() == key.lower():
			break

		else:
			continue

def askYesNo(msg="Are you sure?: ", affirmation="y", negative="n", displayOption=True):
	while True:
		response = input(msg + (f"[{affirmation.upper()}/{negative.upper()}]" if displayOption else ""))
		if affirmation.lower() == response.lower():
			return True

		elif negative.lower() == response.lower():
			return False

		else:
			continue

def parseArgs(target):
	pars = [] # Essential
	opts = {} # Change behaviour of the command

	for i in target:
		if i.startswith("--"):

			if ":" in i:
				opts[i[2:i.index(":")]] = i[i.index(":")+1:]

			else:
				opts[i[2:]] = None

		else:
			pars.append(i)

	return pars, opts


def parseSyntax(target):
	foo = ""

	target += " "
	result = []
	quoteStatus = False

	if type(target) != str:
		raise Exception("A string was expected.")

	for char in target:

		# Element transition
		if char == " " and not quoteStatus:
			if foo == "":
				continue

			result.append(foo)
			foo = ""
			continue

		# Quotes
		if char == "\"":
			if quoteStatus:
				quoteStatus = False
				continue

			else:
				quoteStatus = True
				continue

		else:
			foo += char
			continue

	return result

def getFileAttribs(targetFile):
	targetAttribs = w.GetFileAttributes(targetFile)

	attribs = {
	wc.FILE_ATTRIBUTE_DIRECTORY:"D",
	wc.FILE_ATTRIBUTE_ARCHIVE:"A",
	wc.FILE_ATTRIBUTE_HIDDEN:"H",
	wc.FILE_ATTRIBUTE_SYSTEM:"S",
	wc.FILE_ATTRIBUTE_READONLY:"R"
	}
	result = ""
	for a in attribs:
		if a & targetAttribs:
			result += attribs[a]
		
		else:
			result += "-"
													
	return result

	
class table:
	def __init__(self, rowTitles:list):
		self.rowTitles = rowTitles
		self.content = []
		
		
	def printTable(self):
		# Print the titles of the rows
		
		# Turn all rows into string lists
		for row in range(len(self.content)):
			for col in range(len(self.content[row])):
				self.content[row][col] = str(self.content[row][col])
		print(self.content)
		
		# Contains the width of each column
		widths = []
		for col_title in range(len(self.rowTitles)):
			colWidth = len(self.rowTitles[col_title])
			for col in self.content[col_title]:
				if len(col) > colWidth:
					colWidth = len(col)
			widths.append(colWidth)
			
		print(widths)
		print(self.content)
		
		# THINGS TO FIX HERE
		
	def addContent(self, newContent:list):
		# Adds a row of content
		# The length of the list must be as long as the rowTitles length
		
		if len(newContent) != len(self.rowTitles):
			raise ValueError(f"The new row must contain '{len(self.rowTitles)}', instead, the new content had a length of '{len(self.rowTitles)}'")
			
		else:
			self.content.append(newContent)
	

		


if __name__ == "__main__":
	createBoxTitle(f"This script its designed to be a library and be imported by 'main.py'.")
	
	test = table(["Name", "Age", "Class"])
	test.addContent(["Folgue", 18, "4th B"])
	test.addContent(["Carls", 19, "5th B"])
	test.printTable()
	