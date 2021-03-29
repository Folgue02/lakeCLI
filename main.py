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
import ctypes
import shutil
import readline
# Colors in the terminal
from termcolor import colored
from colorama import init
init()

# Tables
from prettytable import PrettyTable as pt


# Header
__version__ = 1.0
__author__ = "Folgue02"

# Init variables
INIT_VARIABLES = {
	"no-ctrlc":False, # If set to true, disables the ability of closing the CLI by pressing Ctrl + C
	"start-directory":".", #Sets the directory where the shell its going to start.
	"debug":False, # Modifies the behaviour of some parts of the code allowing better debugging.
	"separate-commands":False, # Draws a line between the end of a command and the prompt
	"disable-completer":False, # Disables the auto completer function
	"addon-directory":f"C:\\Users\\{getuser()}\\.lakeCLIAddons", # Directory that contains the addons
	"addon-file":f"C:\\Users\\{getuser()}\\.lakeCLIAddons\\.addon_config.json" # Location where the addon configuration file is.
}


# Variables
VARIABLES = {}
COMMANDS = {} # These are the built-in commands
ADDON_COMMANDS = {"addons":{}}



# CLI functions
print(f"""
    __          __        ________    ____
   / /   ____ _/ /_____  / ____/ /   /  _/
  / /   / __ `/ //_/ _ \\/ /   / /    / /  
 / /___/ /_/ / ,< /  __/ /___/ /____/ /   
/_____/\\__,_/_/|_|\\___/\\____/_____/___/   
                                          
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
					createErrorMessage(f"Exception triggered in built-in command.\nException: '{traceback.format_exc() if 'debug' in INIT_VARIABLES else e}'")

			# Addon commands
			else:
				try:
					# Executes the command in the folder of the addon.
					os.system(os.path.join(INIT_VARIABLES['addon-directory'], command, ADDON_COMMANDS["addons"][command]["entryFile"]) + " " + " ".join(args))

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
	simpleMode = False
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
				"ls --no-file / --no-dir":"Lists the content of the diretory except for what has been specified (only works in normal mode).",
				"ls --simple-mode":"Only prints all the files and folders names. (avoids name shortening, which happens in normal mode)"
			}
		})
		return

	if "no-dir" in opts:
		noDir = True

	if "no-file" in opts:
		noFile = True
		
	if "simple-mode" in opts:
		simpleMode = True

	# Execution time
	for directory in targetFolders:
		if not os.path.isdir(directory):
			createErrorMessage(f"The path specified doesn't exist: '{directory}'")
			continue
	
		print(f"Showing content of '{directory}'")
		dirElements = os.listdir(directory)
		files = []
		dirs = []
		# Table to display
		table = pt()
		table.field_names = ["Name", "Size", "Creation date", "Attributes"]

		# Separates the folders from the files
		for element in dirElements:
			if os.path.isdir(os.path.abspath(os.path.join(directory, element))):
				dirs.append(element)

			else:
				files.append(element)

		# Dirs
		if files != [] and not noFile and not simpleMode:
			for f in files:
				try:
					attribs = getFileAttribs(os.path.join(directory, f))
				except:
					attribs = "UNKNOWN"
				
				name = f
				if len(name) > 30:
					name = name[:27] + "..."
				table.add_row([name, f"{format(os.path.getsize(os.path.join(directory, f)) / 1000, 'f')} KB", ctime(os.path.getctime(os.path.join(directory, f))), attribs])
			
		if dirs != [] and not noDir and not simpleMode:
			for d in dirs:
				try:
					attribs = getFileAttribs(os.path.join(directory, d))
				except:
					attribs = "UNKNOWN"
				
				
				name = d
				if len(name) > 30:
					name = name[:27] + "..."	
					
				
				table.add_row([name, "<FOLDER>", ctime(os.path.getctime(os.path.join(directory, d))), attribs])
		if not simpleMode:
			print(table)
			
		else:
			createBoxTitle(f"Showing files and folders of directory '{directory}'")
			for index, element in enumerate(os.listdir(directory)):
				print(f"{index+1}\t:\t{colored(element, on_color='on_green') if os.path.isdir(os.path.join(directory, element)) else element}")
					
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
			createErrorMessage(f"This file doesn't exist: '{file}'")

		else:
			print(f"{20*'-'} START OF FILE '{file}'")



			# Print the content
			if pauseMode:
				h = os.get_terminal_size()[1] 
				try:
					content = open(file, "r").read().split("\n")
				except PermissionError:
					createErrorMessage(f"Cannot read content of file '{file}', you don't have read permissions.")
				
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
				try:
					print(open(file, "r").read()) if open(file, "r").read() != "" else print(colored("This file is empty.", "red"))
				except PermissionError:
					createErrorMessage(f"Cannot read content of file '{file}', you don't have read permissions.")
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
	pars, opts = parseArgs(args)
	
	
	if "help" in opts:
		createHelpText({
			"description":"Updates the addon configuration by reading the addon configuration file.",
			"usage":{
				"refresh":"Refreshes the addon configuration."
			}
		})
		return
	
	
	if not os.path.isfile(INIT_VARIABLES['addon-file']):
		createErrorMessage(f"The addon configuration file doesn't exist. '{INIT_VARIABLES['addon-file']}'")
		print(f"Creating an empty version of it...")
		
		# The directory doesn't exist either
		if not os.path.isdir(INIT_VARIABLES['addon-directory']):
			os.mkdir(INIT_VARIABLES['addon-directory'])
			print("The addons directory wasn't found, so it will be created as well.")

		open(INIT_VARIABLES['addon-file'], "w").write("{\"addons\":{}}") # Empty file

	else:
		try:
			print(f"Reading addon configuration file in location {INIT_VARIABLES['addon-file']}...")
			ADDON_COMMANDS = loads(open(INIT_VARIABLES['addon-file'], "r").read())
			print(f"Addon configuration updated.")

		except JSONDecodeError:
			createErrorMessage("The configuration file its corrupted.")

			if askYesNo("Do you want to clear the addon configuration file?"):
				open(INIT_VARIABLES['addon-file'], "w").write("{}")


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
				print(colored("\n\tThis doesn't look like a path.", "red"))

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
				addontool.install(INIT_VARIABLES['addon-file'], f)
	# list
	elif "list" == opts["tool"]:
		addontool.list(INIT_VARIABLES['addon-file'])

	# remove
	elif "uninstall" == opts["tool"] or "remove" == opts["tool"]:
		if pars == []:
			createErrorMessage("You must specify an addon to uninstall.")

		else:
			for p in pars:
				addontool.uninstall(INIT_VARIABLES['addon-file'], p)

	elif "help" == opts["tool"]:
		if pars == []:
			createErrorMessage("You must specify the addon.")
		
		else:
			addontool.getHelp(INIT_VARIABLES['addon-file'], pars[0])
				

	elif "guide" == opts["tool"]:
		addontool.guide(pars)
								
	
	else:
		createErrorMessage(f"Unknown tool: '{opts['tool']}'")

	del addontool

def moveElement(args):
	pars, opts = parseArgs(args)
	
	if "help" in opts or len(pars) != 2:
		createHelpText({
			"description":"Moves a file or a directory to an specified location.",
			"usage":{
				"move <target> <destiny>":"Moves <target> to <destiny>"
			}
		})
	
	else:
		try:
			createLogMessage(f"Moving '{pars[0]}' to destiny '{pars[1]}'...")
			shutil.move(pars[0], pars[1])
			
		except Exception as e:
			createErrorMessage(f"Cannot do operation due to the following error: '{e}'")
	
def copyFile(args):
	pars, opts = parseArgs(args)
	
	if "help" in opts or pars == []:
		createHelpText({
			"description":"Copies files into a destiny.",
			"usage":{
				"copyf <file1> <destiny>":"Copies <file1> to <destiny>",
				"copyf <file1> <destiny> --overwrite":"Copies <file1> to <destiny> even if <destiny> already exists."
			}
		})

	elif len(pars) != 2:
		createErrorMessage("You must specify only two arguments, the file to copy, and its destiny.")
		
	else:
		# File doesn't exist
		if not os.path.isfile(pars[0]):
			createErrorMessage(f"Cannot copy file '{pars[0]}', file not found.")
				
		else:
			# Read content of file and then write it into the destiny.
			binContent = open(pars[0], "rb").read()
				
			# Destiny file exists
			if os.path.isfile(pars[1]) and not "overwrite" in opts:
				createErrorMessage(f"Cannot copy '{pars[0]}' into '{pars[1]}' because the file already exists. (Use \"--overwrite\" to avoid this error.)")
			
			# Write the content of the file
			else:
				open(pars[1], "wb").write(binContent)

				
	
def copyDirectory(args):
	pars, opts = parseArgs(args)

	if "help" in opts or pars == []:
		createHelpText({
			"description":"Copies a directory (includes its child directories and files) into a destiny.",
			"usage":{
				"copyd <directory> <destiny>":"Copies <directory> to <destiny>."
			}
		})
		
	
	elif len(pars) != 2:
		createErrorMessage("You must specify only two arguments, the directory to copy and its destiny.")
			
	else:
		if not os.path.isdir(pars[0]):
			createErrorMessage(f"Cannot copy folder '{pars[0]}', folder not found.")
			
		else:
			shutil.copytree(pars[0], pars[1])
				
def settings(args):
	pars, opts = parseArgs(args)
	
	if "help" in opts or opts == {}:
		createHelpText({
			"description":"A command for modifying or showing the settings of the cli.",
			"usage":{
				"settings --show <setting>":"Prints the value of the setting <setting>. If <setting> its not specified, it will print the values for all the settings.",
				"settings --change:<setting> <value>":"Modifies the value of <setting>, setting the new value, <value>."
			}
		})
		
	else:
		if "show" in opts:
			t = pt()
			t.field_names = ["Variable name", "Variable value", "Variable value type"]
			
			# Show all settings
			if pars == []:
				for s in INIT_VARIABLES:
					t.add_row([s, INIT_VARIABLES[s], type(INIT_VARIABLES[s])])
					
			else:
				for s in pars:
					if not s in INIT_VARIABLES:
						t.add_row([s, colored("Doesn't exist.", "red"), colored("Doesn't exist.", "red")])
					
					else:
						t.add_row([s, INIT_VARIABLES[s], type(INIT_VARIABLES[s])])
			print(t)
					
		if "change" in opts:
			targetSetting = opts["change"]
			
			# No new value for the setting
			if pars == []:
				createErrorMessage(f"You must specify the new value for the setting you want to modify.")
				
			if opts["change"] == None:
				createErrorMessage(f"You must specfiy the setting you want to modify.")
				
			else:
				if not opts["change"] in INIT_VARIABLES:
					createErrorMessage(f"This setting couldn't be found, '{opts['change']}'")
				
				else:
					INIT_VARIABLES[opts["change"]] = parseData(pars[0])

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

def startElevatedProccess(args):
	pars, opts = parseArgs(args)
	
	if "help" in opts or pars == []:
		createHelpText({
			"description":"Executes a process with elevated privileges (win32).",
			"usage":{
				"sep \"<proccestoexecute> <argument1> <argument2>\"": "Starts process <proccesstoexecute> with elevated privileges and <argument1> and <argument2> as arguments."
			}
		})
		
	else:
		pars = parseSyntax(pars[0])
		proc = pars[0]
		parameters = pars[1:]
		try:
			if len(pars) == 1:
				os.system(f"powershell Start-Process {pars[0]} -verb runas")


			else:
				proc = pars[0]
				parameters = pars[1:]
				os.system(f"powershell Start-Process \"{proc}\" -ArgumentList \"{', '.join(parameters)}\"")
		except Exception as e:
			createErrorMessage(f"Something went wrong: {e}")
			

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
COMMANDS["copyf"]= copyFile
COMMANDS["copyd"]= copyDirectory
COMMANDS["settings"] = settings
COMMANDS["sep"] = startElevatedProccess
COMMANDS["echo"] = lambda x: [print(t) for t in x]
COMMANDS["exit"] = lambda x: [exit(0)]
COMMANDS["move"] = moveElement

def main():
	print(f"""
 * Machine's operative system: {sys.platform}
 * Current user:               {getuser()}
 * Python version:             {sys.version}
 * CLI version:                {__version__}
	""")
	pars, opts = parseArgs(sys.argv)
	
	# Parse the commandline arguments
	# Loop through all the arguments specified
	for argument in opts:
		# in case that it is an initializing variable
		if argument in INIT_VARIABLES:
		
			# It must contain a value
			if opts[argument] == None:
				createErrorMessage(f"You must specify a value for the variable specified. ('{argument}')")
				
			else:
				predefinedValues = {"False": False, "True":True, "cwd":os.getcwd()}
				if opts[argument] in predefinedValues:
					opts[argument] = predefinedValues[opts[argument]]
				
				INIT_VARIABLES[argument] = opts[argument]
		
		# Rest of settings
		else:
			# So far this is empty
			pass
	
			
	# Initializiation
	
	# Directory where the CLI will be started
	os.chdir(INIT_VARIABLES["start-directory"])
	if not INIT_VARIABLES["disable-completer"]:
		def completer(text, state):
			for d in os.listdir():
				if d.startswith(text):
					if not state:
						return d
				
					else:
						state -= 1
	
	else:
		def completer(text, state):
			pass
						
						
	readline.parse_and_bind("tab: complete")
	readline.set_completer(completer)	

	# Main loop
	while True:
		try:
			# Create prompt
			userPrompt = f"[ {getuser().upper()} ]"
			pathPrompt = os.getcwd().replace("\\", "/").upper()[2:]
			
			# Detect privileges
			if ctypes.windll.shell32.IsUserAnAdmin():
				userPrompt = f"[ ADMIN ]"

			else:
				pass

			# Get the user input
			userinput = input(colored(userPrompt, on_color="on_green") + pathPrompt + "# ")

		except KeyboardInterrupt:
			if INIT_VARIABLES["no-ctrlc"]:
				print("^C")
				userinput = "" # Empty the userinput variable instead of parsing it in.
			
			else:
				exit("\nShell closed manually.")
		
		executeLine(userinput)
		# Separate lines setting activated
		if INIT_VARIABLES["separate-commands"] and userinput != "":
			print(len(userPrompt + pathPrompt)*"=")
			




if __name__ == '__main__':
	main()    

