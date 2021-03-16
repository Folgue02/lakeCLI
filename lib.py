from termcolor import colored
import os
from msvcrt import getch

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
	print("+-"+ "-"*len(msg)+ "-+")
	print(f"| {msg} |")
	print("+-"+ "-"*len(msg)+ "-+")

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



if __name__ == "__main__":
	createBoxTitle("PURE SHIT")
	createBoxTitle("text")
	createBoxTitle("")
	waitForKey("e")
	print("done")