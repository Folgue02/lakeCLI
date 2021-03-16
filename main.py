# Imports of the same project

from lib import *

# External imports (misc)
from json import loads, dumps, JSONDecodeError
import os
import subprocess
from shutil import rmtree
from datetime import datetime as dt
from getpass import getuser
import sys
import traceback
from time import ctime
# Colors in the terminal
from termcolor import colored
from colorama import init
init()

# Tables
from prettytable import PrettyTable as pt


# Header
__version__ = 0.5

# Variables
VARIABLES = {}
COMMANDS = {} # These are the built-in commands
ADDON_COMMANDS = {"addons":{}}
ADDON_DIRECTORY = f"C:\\Users\\{getuser()}\\.lakeShellAddons"
ADDON_FILE = f"C:\\Users\\{getuser()}\\.lakeShellAddons\\.addon_config.json"



# CLI functions
print(f"""
    __          __       _____ __         ____
   / /   ____ _/ /_____ / ___// /_  ___  / / /
  / /   / __ `/ //_/ _ \\\\__ \\/ __ \\/ _ \\/ / / 
 / /___/ /_/ /  < /  __/__/ / / / /  __/ / /  
/_____/\\__,_/_/|_|\\___/____/_/ /_/\\___/_/_/                                                
v{__version__}
""")


# Execute a line
def executeLine(line):
	userinput = parseSyntax(line)

	# No input into the console
	if userinput == []:
		pass

	elif userinput[0].startswith("#"):
		pass


	# Decide what to do with the input
	else:

		command = userinput[0]
		args = [] if len(userinput) == 0 else userinput[1:]

		# The command doesn't exist
		if command not in COMMANDS and command not in ADDON_COMMANDS["addons"]:
			print(f"'{command}' its not related to any command.")

		else:
			# Builtin command
			if command in COMMANDS:
				try:
					COMMANDS[command](args)
				except Exception as e:
					createErrorMessage(f"Exception triggered in built-in command.\nException: '{e}'")

			# Addon commands
			else:
				try:
					# Executes the command in the folder of the addon.
					os.system(os.path.join(ADDON_DIRECTORY, command, ADDON_COMMANDS["addons"][command]["entryFile"]) + " " + " ".join(args))

				except Exception as e:
					createErrorMessage(f"Exception triggered in addon's command.\nException: '{e}'")

	
	

#builtin commands
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
				"ls --no-file / --no-dir":"Lists the content of the diretory except for what has been specified"
			}
		})
		return

	if "no-dir" in opts:
		noDir = True

	if "no-file" in opts:
		noFile = True

	# Execution time
	for directory in targetFolders:
		if not os.path.isdir(directory):
			createErrorMessage(f"The path specified doesn't exist: '{directory}'")
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
			p = pt()
			p.field_names = ["File name", "File size", "Creation date"]
			for f in files:
				p.add_row([f, f"{os.path.getsize(os.path.join(directory, f)) / 1000000} KB", ctime(os.path.getctime(os.path.join(directory, f)))])
			
			print(p)

			
		if dirs != [] and not noDir:
			print("\n--------- DIRS ----------")
			
			p = pt()
			p.field_names = ["Directory name", "Number of elements", "Creation date"]
			for d in dirs:
				p.add_row([d, len(os.listdir(d)), ctime(os.path.getctime(os.path.join(directory, d)))])
															
			print(p)
																
def executeConsoleCommand(args):
	pars, opts = parseArgs(args)
	debuggingMode = False

	if "help" in opts or args== []:
		createHelpText({
			"description": "Executes a command in the system's shell.",
			"usage":{
				"x <command> <arg>":"Executes <command> with the args <args>",
				"x <command> \"<command1> <args>\" --all-commands":"Executes <command>, and then <command1> with <args> as arguments.",
				"x <command> --debug":"Executes the command in debugging mode."
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
		try:
			returnCode = os.system(com)
		except KeyboardInterrupt:
			returnCode = 1

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
				# In case that the file is smaller than the screen

				if len(content)// h == 0:
					print(open(file, "r").read())
					print(f"\n{20*'-'} END OF FILE '{file}'")
					return

				for index, line in enumerate(content):


					if index % (len(content) //(len(content) // h)) == 0: 
						print(f"(Page {0 if index == 0 else index // h}/{len(content)// h})<Enter>:", end="")
						waitForKey("\r") # Press enter
						print(" "*len(f"(Page {0 if index == 0 else  index // h}/{len(content)// h})<Enter>:"), end="\r")# clean the line
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


def refreshAddons(args):
	# This function reads the addon configuration file
	global ADDON_COMMANDS
	if not os.path.isfile(ADDON_FILE):
		createErrorMessage(f"The addon configuration file doesn't exist. '{ADDON_FILE}'")
		print(f"Creating an empty version of it...")
		
		# The directory doesn't exist either
		if not os.path.isdir(ADDON_DIRECTORY):
			os.mkdir(ADDON_DIRECTORY)
			print("The addons directory wasn't found, so it will be created as well.")

		open(ADDON_FILE, "w").write("{\"addons\":{}}") # Empty file

	else:
		try:
			print(f"Reading addon configuration file in location {ADDON_FILE}...")
			ADDON_COMMANDS = loads(open(ADDON_FILE, "r").read())
			print(f"Addon configuration updated.")

		except JSONDecodeError:
			createErrorMessage("The configuration file its corrupted.")

			if askYesNo("Do you want to clear the addon configuration file?"):
				open(ADDON_FILE, "w").write("{}")


def printWorkingDirectory(args):
	pars, opts = parseArgs(args)

	if "help" in opts:
		createHelpText({
			"description":"Shows information about the current working directory or the ones specified.",
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

			# It's not a path
			if not "/" in p and not "\\" in p and not os.path.isdir(p):
				print("\n\tThis doesn't look like a path.")

	else:
		print(os.getcwd())

def addonTools(args):
	pars, opts = parseArgs(args)

	if not "tool" in opts or "help" in opts:
		createHelpText({
			"description":"Tool for addons management.",
			"usage":{
				"addontool --tool:install <installfile>":"Installs the addon specified in the install file.",
				"addontool --tool:remove <addon>":"Removes the <addon> from the installed addons (includes its installation folder).",
				"addontool --tool:list":"Lists the installed addons.",
				"addontool --tool:help <addon>":"Shows the help of the addon specified."
			}
		})
		return 

	createLogMessage("Importing addon tools module...")
	try:
		import addontool
	except Exception as e:
		createErrorMessage("Cannot import the install module due to the following reason:")
		createErrorMessage(e)
		return
	createLogMessage(f"* Addon tools manager version detected: '{addontool.__version__}'")


	# Select the tool

	if "install" == opts["tool"]:
		if pars == []:
			createErrorMessage("You must specify at least one file to install.")
			return

		else:
			for f in pars:
				createBoxTitle(f"Starting installation for install file '{f}'")
				addontool.install(ADDON_FILE, f)
	# list
	elif "list" == opts["tool"]:
		addontool.list(ADDON_FILE)

	# remove
	elif "uninstall" == opts["tool"] or "remove" == opts["tool"]:
		if pars == []:
			createErrorMessage("You must specify an addon to uninstall.")

		else:
			for p in pars:
				addontool.uninstall(ADDON_FILE, p)

	elif "help" == opts["tool"]:
		if pars == []:
			createErrorMessage("You must specify the addon.")
		
		else:
			addontool.getHelp(ADDON_FILE, pars[0])
				
	else:
		createErrorMessage(f"Unknown tool: '{opts['tool']}'")

	del addontool


def runScript(args):
	pars, opts = parseArgs(args)

	if pars == [] or "help" in opts:
		createHelpText({
			"description":"Executes a script file.",
			"usage":{
				"run <scriptfile>":"Runs <scriptfile>"
			}
		})

	else:
		if not os.path.isfile(pars[0]):
			createErrorMessage(f"The specified file to execute doesn't exist. ('{pars[0]}')")

		else:
			# Read the file
			for line in open(pars[0], "r").read().split("\n"):
				executeLine(line)


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
COMMANDS["refresh"] = refreshAddons
COMMANDS["addontool"] = addonTools
COMMANDS["at"] = addonTools
COMMANDS["run"] = runScript
COMMANDS["echo"] = lambda x: [print(t) for t in x]


def main():
	print(f"""
 * Machine's operative system: {sys.platform}
 * Current user:               {getuser()}
 * Python version:             {sys.version}
 * Shell version:              {__version__}
	""")
	pars, opts = parseArgs(sys.argv)
	
	if "no-ctrlc" in opts:
		noCtrlc = True
	
	while True:
		try:
			bs = "\\"
			userinput = input(f"{colored('[ '+getuser().upper() + ' ]', 'green', 'on_blue')} {'/' if len(os.getcwd().replace(bs, '/').split('/')) == 1 else '/'.join(os.getcwd().replace(bs,'/').split('/')[1:])}# ")
		except KeyboardInterrupt:
			if noCtrlc:
				print("^C")
			else:
				exit("\nShell closed manually.")

		executeLine(userinput)



if __name__ == '__main__':
	main()    

