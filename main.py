# Imports of the same project
from lib import *

# External imports (misc)
from json import loads, dumps
import os
from shutil import rmtree
from datetime import datetime as dt

# Colors in the terminal
from termcolor import colored
from colorama import init
init()

if True:
	pass


# Variables
VARIABLES = {}
COMMANDS = {} # These are the built-in commands
ADDON_COMMANDS = {}


# CLI functions
print("""
 ___      _______  ___   _  _______  _______  __   __  _______  ___      ___     
|   |    |   _   ||   | | ||       ||       ||  | |  ||       ||   |    |   |    
|   |    |  |_|  ||   |_| ||    ___||  _____||  |_|  ||    ___||   |    |   |    
|   |    |       ||      _||   |___ | |_____ |       ||   |___ |   |    |   |    
|   |___ |       ||     |_ |    ___||_____  ||       ||    ___||   |___ |   |___ 
|       ||   _   ||    _  ||   |___  _____| ||   _   ||   |___ |       ||       |
|_______||__| |__||___| |_||_______||_______||__| |__||_______||_______||_______|
v0.1 (Beta version)
""")


# Builtin commands
def changedir(args):
	if args == []:
		print(os.getcwd())

	else:
		# Path doesn't exist
		if not os.path.isdir(args[0]):
			print(f"The path doesn't exist: '{args[0]}'")

		else:
			os.chdir(args[0])

def listdir(args):
	complexMode = False
	noDir = False
	noFile = False
	targetFolders = [os.getcwd()]

	pars, opts = parseArgs(args)


	# paths specified
	if pars != []:
		targetFolders = pars

	# use the options
	if "help" in opts:
		createHelpText({
			"description":"Shows the content of a directory (if nothing its specified it will show the content of the current working directory.)",
			"usage":{
				"ls <dir>":"Lists the content of <dir>",
				"ls --no-file / --no-dir":"Lists the content of the diretory except for what has been specified",
				"ls --complex":"Shows the content of the folder and creation dates."
			}
		})
		return

	if "no-dir" in opts:
		noDir = True

	if "no-file" in opts:
		noFile = True

	if "complex" in opts:
		complexMode = True

	# Execution time

	for directory in targetFolders:
		if not os.path.isdir(directory):
			print("The path specified doesn't exist: '{directory}'")
			continue
	
		print(f"Showing content of '{directory}'")
		dirElements = os.listdir(directory)
		files = []
		dirs = []

		for element in dirElements:
			if os.path.isdir(os.path.abspath(os.path.join(directory, element))):
				dirs.append(element)

			else:
				files.append(element)

		# im not doing the complexMode yet

		# Dirs
		if files != [] and not noFile:
			print("--------- FILES ---------")
			for file in files:
				if not complexMode: 
					print(f"\t{file}")

				else:# Do the complex mode here
					pass

		if dirs != [] and not noDir:
			print("\n--------- DIRS ----------")
			for folder in dirs:
				if not complexMode: 
					print(f"\t{folder}")

				else:# Do the complex mode here
					pass


def executeConsoleCommand(args):
	pars, opts = parseArgs(args)
	debuggingMode = False

	if "help" in opts or args== []:
		createHelpText({
			"description": "Executes a command in the system's shell.",
			"usage":{
				"x <command> <arg>":"Executes <command> with the args <args>",
				"x <command> \"<command1> <args>\" --all-commands":"Executes <command>, and then <command1> with <args> as arguments.",
			}
		})

	if "debug" in opts:
		debuggingMode = True

	# Join the arguments for x to mix all into one single command to execute
	if not "all-commands" in opts:
		pars = [" ".join(pars)]


	for com in pars:
		print(f"{25*'-'}\nExecuting command '{com}'...\n{25*'-'}") if debuggingMode else None
		startingTime = dt.now().day*24*3600 + dt.now().hour*3600 + dt.now().minute*60 + dt.now().second 
		returnCode = os.system(com)
		endTime = dt.now().day*24*3600 + dt.now().hour*3600 + dt.now().minute*60 + dt.now().second 
		
		print(f"{25*'-'}\nCommand's return code: '{returnCode}'\nCommand's running time: {(endTime-startingTime)//3600}:{(endTime-startingTime)//60}:{(endTime-startingTime)%60}\n{25*'-'}") if debuggingMode else None

def touchFile(args):
	pars, opts = parseArgs(args)
	overwriteMode = False

	if "help" in opts or pars == []:
		createHelpText({
			"description":"Creates empty files with the names specified.",
			"usage":{
				"touch <file1> <file2>":"Creates <file1> and <file2>",
				"touch <file> --overwrite": "Creates <file>, and in case that it already exists, it overwrites it without asking."
			}
		})

	if "overwrite"  in opts:
		overwriteMode = True

	# Execution
	for file in pars:
		if not overwriteMode and os.path.isfile(file):
			createErrorMessage(f"The file '{file}' already exists. Use '--overwrite' to overwrite it.")
			continue

		else:
			try:
				open(file, "w").write("")

			except Exception as e:
				print(f"Couldn't create file '{file}' due to the following error: \n'{e}'")


def readFile(args):
	pars, opts = parseArgs(args)
	pauseMode = False

	if "help" in opts or pars == []:
		createHelpText({
			"description":"Shows the content of a file.",
			"usage":{
				"read <file>":"Displays the content of <file> on the screen.",
				"read <file> --pause": "Displays the content of <file> on the screen doing pauses every time that the screen its filled.",
			}
		})

	if "pause" in opts:
		pauseMode = True


	for file in pars:        
		# The file doesn't exist
		if not os.path.isfile(file):
			createErrorMessage("This file doesn't exist: '{file}'")

		else:
			print(f"{20*'-'} START OF FILE '{file}'")


			# Print the content
			if pauseMode:
				h = os.get_terminal_size()[1] 
				content = open(file, "r").read().split("\n")
				for index, line in enumerate(content):
					if index % (len(content) //(len(content) // h)) == 0:
						print(f"(Page {0 if index == 0 else  index // h}/{len(content)// h})<Enter>:", end="")
						waitForKey("\r")
						print(" "*len(f"(Page {0 if index == 0 else  index // h}/{len(content)// h})<Enter>:"), end="\r")
						print("\r" + line)
						continue

					else:
						print(line)




			else:
				print(open(file, "r").read()) if open(file, "r").read() != "" else print(colored("This file is empty.", "red"))

			print(f"\n{20*'-'} END OF FILE '{file}'")


def createDirectory(args):
	pars, opts = parseArgs(args)
	recursiveMode = False

	if "help" in opts or pars == []:
		createHelpText({
			"description":"Creates the directory specified in the arguments.",
			"usage":{
				"mkdir <directory>":"Creates <directory>",
				"mkdir <directory> --no-warning":"Tries to create <directory> and in case that it already exist the command will quit without displaying an error.",
				"mkdir \"<directory0>/<directory1>/<directory2>\" --recursive":"Creates the directory <directory2> and its parents."
			}
		})

	if "recursive" in opts:
		recursiveMode = True


	# Loop through all the paths specified
	for target in pars:
		parsedPath = target.replace("\\", "/")

		# Recursive mode takes a different execution path than normal way
		if recursiveMode: 
			parsedPath = parsedPath.replace("\\", "/").split("/")


			pathsToCreate = []
			foo = []
			for i, p in enumerate(parsedPath): # Go through each individual path
				for x in range(i+1): # append to foo the folders to create the "paths to create"
					foo.append(parsedPath[x])

				if not os.path.isdir("/".join(foo)): # check if it exists, if it doesnt it will be added as a parsedpath	
					pathsToCreate.append(foo)

				foo = []# Reset the foo var

			for z in pathsToCreate:
				os.mkdir("/".join(z))
			return 

		# Path already exists
		elif  os.path.isdir(parsedPath):
			if "no-warning" in opts: # Do not display the error or try to create the path
				continue

			else:
				createErrorMessage(f"The directory already exists: {target}, avoid this error with '--no-warning'")
				return

		else:
			try:
				os.mkdir(target)
			except FileNotFoundError:
				createErrorMessage("The system cannot find the path, try using '--recursive'.")
			



def removeDirectory(args):
	pars, opts = parseArgs(args)
	noWarningMode = False
	noEmptyMode = False

	if "help" in opts or pars == []:
		createHelpText({
			"description":"Removes the directory specified in the arguments.",
			"usage":{
				"rmdir <directory>":"Creates <directory>",
				"rmdir <directory> --no-warning":"Tries to remove <directory> and in case that it doesn't exist the command will quit without displaying an error.",
				"rmdir <directory> --no-empty":"Removes the directory even if its not empty."
			}
		})

	if "no-warning" in opts:
		noWarningMode = True

	if "no-empty" in opts:
		noEmptyMode = True

	# Loop through the paths specified
	for path in pars:

		# Path doesn't exist
		if not os.path.isdir(path):
			if noWarningMode:
				continue

			else:
				createErrorMessage(f"The directory doesn't exist: {path}, avoid this error with '--no-warning'")

		else:
			# Path not empty
			if os.listdir(path) != []:
				if noEmptyMode:
					rmtree(path)
				
				else:
					createErrorMessage(f"The directory ('{path}')its not empty.")

			else:
				os.rmdir(path)


def removeFile(args):
	pars, opts = parseArgs(args)

	if "help" in opts:
		createHelpText({
			"description":"Removes an specified file",
			"usage":{
				"remove <file1> <file2>":"Removes <file1> and <file2>",
				"remove --no-warning <file1>": "Removes <file1>"
			}
		})

	for file in pars:
		if not os.path.isfile(file):
			if "no-warning" in opts:
				continue

			else:
				createErrorMessage(f"The file specified ('{file}') cannot be removed since it doesn't exist.")

		else:
			try:
				os.remove(file)

			except IOError as e:
				createErrorMessage(f"The file '{file}' cannot be removed, probably because of permission issues.")




def printWorkingDirectory(args):
	pars, opts = parseArgs(args)

	if "help" in opts:
		createHelpText({
			"description":"Shows information about the current working directory.",
			"usage":{
				"pwd":"Prints current directory.",
				"pwd <directory>":"Prints information about <directory>",
				"pwd --print-drive":"Prints the current drive."
			}
		})

	elif "print-drive" in opts:
		print("Current drive: " + os.getcwd().replace("\\", "/").split("/")[0])

	elif pars != []:
		# Paths specified
		for p in pars:
			createBoxTitle(f"Information about '{p}'")
			print("\tPath existance:")
			print(f"\t\t{os.path.exists(p)}")
			print("\n\tParsed path:")
			for i in p.replace("\\", "/").split("/"):
				print(f"\t\t{i}")

	else:
		print(os.getcwd())



		

# update the COMMANDS variable
#       alias -- function
COMMANDS["ls"] = listdir
COMMANDS["cd"] = changedir
COMMANDS["x"]  = executeConsoleCommand
COMMANDS["touch"] = touchFile
COMMANDS["read"] = readFile
COMMANDS["mkdir"] = createDirectory
COMMANDS["rmdir"] = removeDirectory
COMMANDS["pwd"] = printWorkingDirectory
COMMANDS["remove"] = removeFile


def main():
	while True:
		try:
			userinput = parseSyntax(input(f"{os.getcwd()}# "))
		except KeyboardInterrupt:
			exit("Shell closed manually.")

		# No input into the console
		if userinput == []:
			continue

		# Decide what to do with the input
		else:
			command = userinput[0]
			args = [] if len(userinput) == 0 else userinput[1:]

			if command not in COMMANDS and command not in ADDON_COMMANDS:
				print(f"'{command}' its not related to any command.")

			else:
				if command in COMMANDS:
					try:
						COMMANDS[command](args)
					except Exception as e:
						createErrorMessage(f"Exception triggered in built-in command.\nException: '{e}'")
				else:
					try:
						ADDONS_COMMANDS[command](args)
					except Exception as e:
						createErrorMessage(f"Exception triggered in addon's command.\nException: '{e}'")




if __name__ == '__main__':
	main()    

