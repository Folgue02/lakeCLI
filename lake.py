#!/usr/bin/env python3
# Imports of the same project
from lib import *
# The addons tool its not necessary
# So its outside of the main file, and the main file can be executed without the addons tool 
try:
    import addontool

except ModuleNotFoundError:
    createWarningMessage("Couldn't find the addon tools module.")



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

# linux or darwin readline module
if sys.platform != "win32":
    import rlcompleter
    import readline


# Colors in the terminal
from termcolor import colored
from colorama import init
init()


# Header
__version__ = 2.0
__author__ = "Folgue02"

# Init variables
INIT_VARIABLES = {
    "no-ctrlc":False, # If set to true, disables the ability of closing the CLI by pressing Ctrl + C
    "start-directory":".", #Sets the directory where the shell its going to start.
    "debug":False, # Modifies the behaviour of some parts of the code allowing better debugging.
    "separate-commands":False, # Draws a line between the end of a command and the prompt
    "disable-completer":False, # Disables the auto completer function
    "run-autorun":True, # Run the autorun script
    "title":f"LakeCLI v{__version__}", # Title displayed
    "max-text-size":30, # Maximum length of the text displayed in tables
    "shell-execution-mode":False, # Activates the shell execution mode. (Commands that are not from lakeCLI are tried to be executed as shell commands)
    "disable-readline":False, # Disables the usage of the readline module when asking for userinput
    "prompt":"%U%W# ", # Prompt to be displayed in the CLI
    "save-history":True, # Save the commands used in a file, separated by lines
    "history-file":f"C:\\Users\\{getuser()}\\.lakeCLIAddons\\history.txt" if sys.platform ==  "win32" else f"/home/{getuser()}/.config/.lakeCLIAddons/history.txt", # File where the commands used will be saved.
    "addon-directory":f"C:\\Users\\{getuser()}\\.lakeCLIAddons" if sys.platform ==  "win32" else f"/home/{getuser()}/.config/.lakeCLIAddons", # Directory that contains the addons
    "addon-file":f"C:\\Users\\{getuser()}\\.lakeCLIAddons\\.addon_config.json" if sys.platform == "win32" else f"/home/{getuser()}/.config/.lakeCLIAddons/.addon_config.json" # Location where the addon configuration file is.
}


# Variables
VARIABLES = {"cwd":os.getcwd(),
    "platform":sys.platform, 
    "home":os.path.expanduser("~") if sys.platform != "win32" else f"C:\\Users\\{getuser()}",
    "user":getuser(),
    "version":str(__version__),
    "pyVersion":str(sys.version_info[0:3]).replace('(', '').replace(')', '').replace(', ', '.')
}
COMMANDS = {} # These are the built-in commands
ADDON_COMMANDS = {"addons":{},"aliases":{}}


# Execute a line
def executeLine(line):
    userinput = parseSyntax(line)

    if line.startswith("#") or line.strip() == "":
        return

    parsedResult = [] # This will contain the string with the resolved variables

    # Save the command in the history file.
    if INIT_VARIABLES["save-history"]:
        if not os.path.isfile(INIT_VARIABLES["history-file"]):
            createWarningMessage(f"save-history setting enabled, but the history file doesn't exist, creating it...")
            try:
                open(INIT_VARIABLES["history-file"], "w").write(line + "\n")
            except Exception as e:
                createErrorMessage(f"Cannot create history file in path '{INIT_VARIABLES['history-file']}' due to the following reason: '{e}',\n History setting disabled, to re-enable this setting use this command: 'settings --change:save-history True'") 
                INIT_VARIABLES["save-history"] = False

        else:
            oldContent = open(INIT_VARIABLES["history-file"], "r").read()
            open(INIT_VARIABLES["history-file"], "w").write(oldContent + line + "\n")

    for segment in userinput:
        try:
            parsedResult.append(resolveStringVariables(segment, VARIABLES))
        except KeyError as e:
            print(colored(f"The variable doesn't exist: {e}", "red"))
            return

    userinput = parsedResult 

    # No input into the console
    if userinput == []:
        pass

    # Decide what to do with the input
    else:
        command = userinput[0]
        args = [] if len(userinput) == 0 else userinput[1:]

        # The command doesn't exist
        if command not in COMMANDS and command not in ADDON_COMMANDS["addons"] and not command in ADDON_COMMANDS["aliases"]:

            if INIT_VARIABLES["shell-execution-mode"]:
                # Check for the command in the path env variables

                for p in (os.getenv("PATH").split(";") if sys.platform == "win32" else os.getenv("PATH").split(":")):
                    if not os.path.isdir(p):
                        continue

                    else:
                        if sys.platform == "win32":
                            if command in os.listdir(p):
                                os.system(f"{command} {' '.join(args)}")
                                return

                            elif command + ".exe" in os.listdir(p):
                                os.system(f"{command + '.exe'} {' '.join(args)}")
                                return

                        else:
                            if command in os.listdir(p):
                                os.system(f"{command} {' '.join(args)}")
                                return

                # If the function gets to this point, the command didnt exist
                print(f"'{command}' its not related to any command.")

            else:
                print(f"'{command}' its not related to any command.")





        else:
            # Builtin command
            if command in COMMANDS:
                try:
                    COMMANDS[command](args)
                except Exception as e:
                    errorToDisplay = e if not INIT_VARIABLES["debug"] else traceback.format_exc()
                    createErrorMessage(f"Exception triggered in built-in command. ('{command}')\nException: '{errorToDisplay}'")

            # Alias
            elif command in ADDON_COMMANDS["aliases"]:
                line = ADDON_COMMANDS["aliases"][command] + " ".join(args)

                # Avoid recursion (the alias references another alias, which it creates and endless loop)
                if ADDON_COMMANDS["aliases"][command] in ADDON_COMMANDS["aliases"]:
                    createErrorMessage(f"Cannot execute this alias since it references another alias. ('{command}')")

                else:
                    executeLine(line)
            
            # Addon commands
            else:
                try:
                    # Executes the command in the folder of the addon.
                    os.system(os.path.join(INIT_VARIABLES['addon-directory'], command, ADDON_COMMANDS["addons"][command]["entryFile"]) + " " + " ".join(args))

                except Exception as e:
                    createErrorMessage(f"Exception triggered in addon's command. ('{command}')\nException: '{e}'")

                except KeyboardInterrupt:
                    createErrorMessage(f"Operation cancelled manually by user.")


#builtin commands
def changedir(args):
    if args == []:
        print(os.getcwd())

    else:
        # Path doesn't exist
        if not os.path.isdir(args[0]):
            print(f"The path doesn't exist: '{args[0]}'")

        else:
            try:
                os.chdir(args[0])
                VARIABLES["cwd"] = os.getcwd()
            except PermissionError:
                createErrorMessage(f"You don't have the required permissions to enter in this path: '{args[0]}'")



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
    
        dirElements = os.listdir(directory)
        files = []
        dirs = []
        # Table to display
        t = table(["Name", "Size", "Creation date", "Attributes"])
        

        # Separates the folders from the files
        for element in dirElements:
            if os.path.isdir(os.path.abspath(os.path.join(directory, element))):
                dirs.append(element)

            else:
                files.append(element)

        # Dirs
        if files != [] and not noFile and not simpleMode:
            for f in files:
                attribs = getFileAttribs(os.path.join(directory, f))
                
                name = f

                # Max text size variable
                if len(name) > INIT_VARIABLES["max-text-size"]:
                    name = name[:INIT_VARIABLES["max-text-size"]-3] + "..."
                
                else:
                    pass

                # To avoid errors with symbolic links in UNIX
                if (os.path.islink(os.path.join(directory, f)) if sys.platform != "win32" else False):

                    t.addContent([name, "<SIM. LINK>", "<SIM. LINK>", attribs])

                else:

                    t.addContent([name, f"{format(os.path.getsize(os.path.join(directory, f)) / 1000, 'f')} KB", ctime(os.path.getctime(os.path.join(directory, f))), attribs])


        if dirs != [] and not noDir and not simpleMode:
            for d in dirs:
                try:
                    attribs = getFileAttribs(os.path.join(directory, d))
                except:
                    attribs = "UNKNOWN"
                
                
                name = d
                if len(name) > INIT_VARIABLES["max-text-size"]:
                    name = name[:INIT_VARIABLES["max-text-size"]-3] + "..."
 

                t.addContent([name, "<FOLDER>", ctime(os.path.getctime(os.path.join(directory, d))), attribs])
        if not simpleMode:
            t.printTable()
            
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

    targets = []
    for x in pars:
        results = returnFileMatches(x)

        if results != []:
            for r in results:
                targets.append(r)

        else:
            pass

    for file in targets:
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
                
                except UnicodeDecodeError:
                    createErrorMessage(f"Cannot decode the specified file ('{file}').")
                    
                # In case that the file is smaller than the screen

                if len(content)// h == 0:
                    print(open(file, "r").read())
                    print(f"\n{20*'-'} END OF FILE '{file}'")
                    return

                for index, line in enumerate(content):


                    if index % (len(content) //(len(content) // h)) == 0: 
                        print(f"(Page {0 if index == 0 else index // h}/{len(content)// h})<Enter>:", end="\r")
                        
                        # In case that the user wants to get out of the read command
                        try:
                            waitForKey("\r") # Press enter
                        except KeyboardInterrupt:
                            break

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
                    
                except UnicodeDecodeError:
                    createErrorMessage(f"Cannot decode the specified file ('{file}').")
            print(f"{20*'-'} END OF FILE '{file}'")


def createDirectory(args):
    pars, opts = parseArgs(args)
    recursiveMode = False

    if "help" in opts or pars == []:
        createHelpText({
            "description":"Creates the directory specified in the arguments.",
            "usage":{
                "mkdir <directory>":"Creates <directory>",
                "mkdir <directory> --no-warning":"Tries to create <directory> and in case that it already exist the command will quit without displaying an error.",
                "mkdir \"<directory0>/<directory1>/<directory2>\" --recursive":"Creates the directory <directory2> and its parent directory."
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
                "rmdir <directory> --no-empty/--recursive":"Removes the directory even if its not empty."
            }
        })

    if "no-warning" in opts:
        noWarningMode = True

    if "no-empty" in opts or "recursive" in opts:
        noEmptyMode = True

    # Turn the parameters into a list of matches
    targets = []
    for x in pars:
        results = returnFileMatches(x)

        if results != []:
            for r in results:
                targets.append(r)

        else:
            pass


    # Loop through the paths specified
    for path in targets:

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
                try:
                    os.rmdir(path)
                except PermissionError:
                    createErrorMessage(f"Cannot remove folder '{path}', you lack the permissions for the operation.")


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

    targets = []
    for x in pars:
        results = returnFileMatches(x)

        if results != []:
            for r in results:
                targets.append(r)

        else:
            pass


    for file in targets:
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
            "description":"Reads / changes the configuration file.",
            "usage":{
                "refresh":"Refreshes the addon configuration."
            }
        })
    
    if not os.path.isfile(INIT_VARIABLES['addon-file']):
        createErrorMessage(f"The addon configuration file doesn't exist. '{INIT_VARIABLES['addon-file']}'")
        print(f"Creating an empty version of it...")
        
        # The directory doesn't exist either
        if not os.path.isdir(INIT_VARIABLES['addon-directory']):
            os.mkdir(INIT_VARIABLES['addon-directory'])
            print("The addons directory wasn't found, so it will be created as well.")

        open(INIT_VARIABLES['addon-file'], "w").write("{\"addons\":{}, \"aliases\":{}}") # Empty file

    else:
    
        if "save" in opts:
            open(INIT_VARIABLES["addon-file"], "w").write(dumps(ADDON_COMMANDS))
            createLogMessage("Configuration saved in the configuration file.")
        
        else:
        
            try:
                ADDON_COMMANDS = loads(open(INIT_VARIABLES['addon-file'], "r").read())

            except JSONDecodeError:
                createErrorMessage("The configuration file its corrupted.")

                if askYesNo("Do you want to clear the addon configuration file?"):
                    open(INIT_VARIABLES['addon-file'], "w").write('{"addons":{},"aliases":{}}')

                
def alias(args):
    pars, opts = parseArgs(args)
    
    if "help" in opts:
        createHelpText({
            "description":"Modify the console aliases",
            "usage":{
                "alias --show":"Shows all the current aliases.",
                "alias --add:<alias> \"<command>\"":"Creates a new alias with name <alias> for a command (<command>).",
                "alias --remove <alias>":"Removes the alias '<alias>'."
            },
            "notes":"The alias command only changes the configuration of the current session. If you want to save the aliases added or removed, you must use \"refresh --save\""
        })
    
    else:
        if "show" in opts:
            # Shows the current aliases loaded.
            t = table(["Alias name", "Value"])
                    
            for x in ADDON_COMMANDS["aliases"]:
                t.addContent([x, ADDON_COMMANDS["aliases"][x]])
                
            t.printTable()
        
        else:
            
            if "add" in opts:
                # This option requires parameters
                if pars == [] or opts["add"] == None:
                    createErrorMessage("You must specify new alias name, and its command (--add:<newalias> <command>)")
                
                else:
                    if opts["add"] in ADDON_COMMANDS["aliases"] and not "overwrite" in opts:
                        createErrorMessage(f"The alias '{opts['add']}' already exists. If you want to overwrite it add the parameter \"--overwrite\"")
                    ADDON_COMMANDS["aliases"][opts["add"]] = pars[0]
                
            if "remove" in opts:
                if pars == []:
                    createErrorMessage("You must specify the alias to remove.")
                
                else:
                    if not pars[0] in ADDON_COMMANDS["aliases"]:
                        createErrorMessage(f"The alias '{pars[0]}' doesn't exist.")
                    
                    else:
                        del ADDON_COMMANDS["aliases"][pars[0]]
                
def printWorkingDirectory(args):
    pars, opts = parseArgs(args)

    if "help" in opts:
        createHelpText({
            "description":"Shows information about the current working directory or the ones specified.",
            "usage":{
                "pwd":"Prints current directory.",
                "pwd <directory>":"Prints information about <directory>",
                "pwd --print-drive":"Prints the current drive. (Only available in win32)"
            }
        })

    elif "print-drive" in opts:
        if sys.platform != "win32":
            createErrorMessage(f"This parameter is only available in win32 (you are using '{sys.platform}').")
        else:
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

    if not "addontool" in globals():
        createErrorMessage("Addon tool manager couldn't be found when initializing.")

    else:
        # Select the tool
        addontool.main(INIT_VARIABLES["addon-directory"], INIT_VARIABLES["addon-file"], args) 

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
        count = 0
        targets = returnFileMatches(pars[0])
        for file in returnFileMatches(pars[0]):
            # Try to move file or folder
            try:
                createLogMessage(f"Moving element '{file}' to destiny '{pars[1]}'")
                shutil.move(file, pars[1])
                count += 1
            except Exception as e:
                createErrorMessage(f"Couldn't move element '{file}' to destiny '{pars[1]}' due to the following reason: '{e}'")

        createLogMessage(f"'{count}' file/s or folder/s moved.")




def copy(args):
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
        for target in returnFileMatches(pars[0]):
            try:
                shutil.copy(target, pars[1])

            except Exception as e:
                createErrorMessage(f"Cannot copy '{target}' to destiny '{pars[1]}' due to the following reason: '{e}'")


    
def settings(args):
    pars, opts = parseArgs(args)
    
    if "help" in opts or opts == {}:
        createHelpText({
            "description":"A command for modifying or showing the settings of the cli.",
            "usage":{
                "settings --show <setting>":"Prints the value of the setting <setting>. If <setting> its not specified, it will print the values for all the settings.",
                "settings --change:<setting> <value>":"Modifies the value of <setting>, setting the new value, <value>.",
                "settings --export <settingsfile>":"Exports the current settings to a json file. (If <settingsfile> its not specified, it will be set to 'settings.json' by default)",
                "settings --import <settingsfile>":"Imports settings configuration from <settingsfile>. (If <settingsfile> its not specified, it will be set to 'settings.json' by default)"
            }
        })
        
    else:
        if "show" in opts:
            t = table(["Variable name", "Variable value", "Variable value type"])
            
            # Show all settings
            if pars == []:
                for s in INIT_VARIABLES:
                    t.addContent([s, INIT_VARIABLES[s], type(INIT_VARIABLES[s])])
                    
            else:
                for s in pars:
                    if not s in INIT_VARIABLES:
                        t.addContent([s, colored("Doesn't exist.", "red"), colored("Doesn't exist.", "red")])
                    
                    else:
                        t.addContent([s, INIT_VARIABLES[s], type(INIT_VARIABLES[s])])
            t.printTable()
                    
        elif "change" in opts:
            targetSetting = opts["change"]
            
            # No new value for the setting
            if pars == []:
                createErrorMessage(f"You must specify the new value for the setting you want to modify.")
                
            elif opts["change"] == None:
                createErrorMessage(f"You must specfiy the setting you want to modify.")
                
            else:
                if not opts["change"] in INIT_VARIABLES:
                    createErrorMessage(f"This setting couldn't be found, '{opts['change']}'")
                
                else:
                    INIT_VARIABLES[opts["change"]] = parseData(pars[0])

        elif "export" in opts:
            output_file = "settings.json"

            if pars != []:
                output_file = pars[0]
            
            try:
                open(output_file, "w").write(dumps(INIT_VARIABLES))

            except Exception as e:
                createErrorMessage(f"Cannot export settings to file '{output_file}' due to the following reason: {e}")

        elif "import" in opts:
            input_file = "settings.json"

            if pars != []:
                input_file = pars[0]

            try:
                target_content = loads(open(input_file, "r").read())

            except PermissionError:
                createErrorMessage("Not enough permissions to read the specified file.")

            except JSONDecodeError:
                createErrorMessage("The specified file might be corrupt.")

            for key in INIT_VARIABLES:
                if not key in target_content:
                    pass

                else:
                    if not isinstance(target_content[key], type(INIT_VARIABLES[key])):
                        createErrorMessage(f"Cannot import setting '{key}' due to being an invalid type of variable.")

                    else:
                        INIT_VARIABLES[key] = target_content[key]

        else:
            createErrorMessage("A non valid parameter was specified.")

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
            "description":"Executes a process using powershell with elevated privileges (win32), in linux it will use the sudo command.",
            "usage":{
                "sep \"<proccestoexecute> <argument1> <argument2>\"": "Starts process <proccesstoexecute> with elevated privileges and <argument1> and <argument2> as arguments."
            }
        })
        
    else:
        # Non windows machines
        if sys.platform != "win32":
            os.system(f"sudo {' '.join(args)}")

        else:
            pars = parseSyntax(pars[0])
            proc = pars[0]
            parameters = pars[1:]
            try:
                if len(pars) == 1:
                    os.system(f"powershell Start-Process {pars[0]} -Verb RunAs")


                else:
                    proc = pars[0]
                    parameters = pars[1:]
                    os.system(f"powershell Start-Process \"{proc}\" -ArgumentList \"{', '.join(parameters)}\" -Verb RunAs")
            except Exception as e:
                createErrorMessage(f"Something went wrong: {e}")

def varMgr(args):
    pars, opts = parseArgs(args)
    if "help" in opts or pars == []:
        createHelpText({
            "description":"Sets, modifies, and removes variables",
            "usage":{
                "var set <name> <value>":"Creates a variable with the name <name> that contains <value>.",
                "var remove <name> <name1>":"Removes the variables <name> and <name1>.",
                "var show [<name>]":"Shows all the variables stored. If a name of one has been specified, only that variable and its value will be shown."
            }
        })
    
    else:
         
        # Set variable
        if pars[0] == "set":
            if len(pars) < 3:
                createErrorMessage("You must specify the name and the value of the variable.")

            else:
                # Check validity of the var name
                if pars[1].find("$") != -1 or pars[1].find("\"") != -1:
                    createErrorMessage("The variable contains a forbidden character ('$', '\"')")
                else:
                    VARIABLES[pars[1]] = pars[2]
       
        # Show variables
        elif pars[0] == "show":
            
            t = table(["Name", "Value"])
            

            # No var names have been specified
            if len(pars) == 1:
                for var in VARIABLES:
                    t.addContent([var, VARIABLES[var]])

            else:
                for var in pars[1:]:
                    if not var in VARIABLES:
                        t.addContent([var, colored(f"UNKNOWN", "red")])
                        continue
                    
                    else:
                        t.addContent([var, VARIABLES[var]])

            t.printTable()

        # Remove the variables
        elif pars[0] == "remove" or pars[0] == "rm":
            if len(pars) < 2:
                createErrorMessage("You must specify the names of the variables to remove.")

            else:
                for var in pars[1:]:
                    if not var in VARIABLES:
                        createErrorMessage(f"Cannot remove '{var}' since it doesn't exist.")

                    else:
                        del VARIABLES[var]

        # Import command, imports variables from a file
        elif pars[0] == "import":
            if len(pars) == 1:
                createErrorMessage("You must specify the files to import the variables from.")
            
            else:
                for f in pars[1:]:
                    try:
                        content = loads(open(f, "r").read())
                        
                    except JSONDecodeError:
                        createErrorMessage(f"The variables file '{f}' might be corrupted or unreadable.")
                        continue
                    
                    except FileNotFoundError:
                        createErrorMessage(f"File not found: '{f}'")
                        continue

                    # Import the variables to the CLI
                    for var in content:
                        # Check that it contains a valid type of variable
                        if type(content[var]) != str:
                            createErrorMessage(f"Cannot import variable '{var}' from file '{f}' since it contains an invalid type of variable.")
                        
                        else:
                            varMgr(["set", var, content[var]])

        elif pars[0] == "export":
            if len(pars) == 1:
                createErrorMessage("You must specify the output file of the variable exporting.")

            else:
                # Check that the file can be created
                if os.path.exists(pars[1]) and not "overwrite" in opts:
                    createErrorMessage("Cannot exports the variables to the specified file since it already exists. (use \"--overwrite\" to overwrite the specified file.)")

                else:
                    try:
                        open(pars[1], "w").write(dumps(VARIABLES, indent=2))
                    except PermissionError:
                        createErrorMessage(f"You don't own the permissions to write in this file. ('{pars[1]}')")




        else:
            createErrorMessage(f"Command not found: '{pars[0]}'")

def showHistory(args):
    pars, opts = parseArgs(args)

    if not INIT_VARIABLES["save-history"]:
        createWarningMessage("Setting 'save-history' is disabled. Enable it with command 'settings --change:save-history True'")

    elif "help" in opts:
        createHelpText({
            "description":"Display a list of the commands used.",
            "usage":{
                "history":"Displays a list of the commands used.",
                "history --exec:<commandindex>":"Executes the command related to <commandindex> in the history file. ",
                "history --clean":"Empties the history file."
            }
        })

    else:

        try:
            content = open(INIT_VARIABLES["history-file"], "r").read()
        except Exception as e:
            createErrorMessage(f"Cannot open history file in location '{INIT_VARIABLES['history-file']}' due to the following reason: '{e}'")


        if opts == {}:
            t = table(["Index", "Command"], separator="|")
            for index, line in enumerate(content.split("\n")):
                t.addContent([index, line])

            t.printTable()

        elif "exec" in opts: 
            target_index = 0
            try:
                target_index = int(opts["exec"])
            except ValueError:
                createErrorMessage("An integer was expected as index of the history.")
                return
            try:
                executeLine(content.split("\n")[target_index])

            except IndexError:
                createErrorMessage("Cannot summon command from history, since the index specified was out of range.")

        elif "clean" in opts:
            try:
                open(INIT_VARIABLES["history-file"], "w").write("")
            except Exception as e:
                createErrorMessage(f"Cannot clean history file at location '{INIT_VARIABLES['history-file']}' due to following reason: '{e}'")





# TODO? Inspect command

def showAllCommands(args):
    pars, opts = parseArgs(args)
    print("Remember: "+ colored("All the built-in commands will return a brief usage guide if you specify \"--help\" as a parameter.", "blue", "on_yellow"))    
    if "help" in opts:
        createHelpText({
            "description":"Prints all built-in commands in the system.",
            "usage":{
                "allcommands":"Prints all built-in commands in the system."
            }
        })

    else:
        t = table(["Index", "Reference command"])
        for index, com in enumerate(COMMANDS):
            t.addContent([index+1, com])

        t.printTable()


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
COMMANDS["copy"] = copy
COMMANDS["settings"] = settings
COMMANDS["sep"] = startElevatedProccess
COMMANDS["move"] = moveElement
COMMANDS["alias"] = alias
COMMANDS["allcommands"] = showAllCommands
COMMANDS["var"] = varMgr
COMMANDS["history"] = showHistory

COMMANDS["echo"] = lambda x: [print(t) for t in x]
COMMANDS["exit"] = lambda x: [exit(0)]

def main():
    print(f"""
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
                
                
                if type(parseData(opts[argument]))!= type(INIT_VARIABLES[argument]):
                    createErrorMessage(f"A setting has been tried to be changed with an invalid type of value. ('{argument}')")
                else:
                    opts[argument] = parseData(opts[argument])
                
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
                if d.lower().startswith(text.lower()):
                    if not state:
                        if " " in d:
                            return ("\"" if not d.startswith("\"") else "") + d + ("\"" if not d.endswith("\"") else "")
                        else:
                            return d
                
                    else:
                        state -= 1
    
    else:
        def completer(text, state):
            pass
    
    # Change the terminal's title (only works in windows)
    os.system(f"title {INIT_VARIABLES['title']}") if sys.platform == "win32" else False

    # Disable readline module
    if not INIT_VARIABLES["disable-readline"] and  sys.platform != "win32": # FIXME create support for tab completion in the prompt for windows 
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer)
    
    # Load the configuration file
    if INIT_VARIABLES["run-autorun"]:
        runScript([os.path.join(os.path.split(__file__)[0], "autorun.lcs")])


    # Define user prompt special chars that will be replaced later
    userPromptChars = {
        "%U":(f"[ {colored(getuser().upper(), 'green')} ]" if getuser() != 'root' else f"[ {colored(getuser().upper(), 'red')} ]") ,
        "%u":getuser()
    }
    
    # Main loop[ FOLGUE ]/home/folgue
    while True:
        try:
            # This prompt chars need to be updated every time.
            userPromptChars["%W"] = os.getcwd().replace("\\", "/").upper()[2:] if sys.platform == "win32" else os.getcwd() 
            userPromptChars["%w"] = os.getcwd()
            userPromptChars["%c"] = os.path.split(os.getcwd())[1]                  
            
            userPrompt = INIT_VARIABLES["prompt"]

            # Replace the special characters with the ones declared
            for c in userPromptChars:
                if c in userPrompt:
                    userPrompt = userPrompt.replace(c, str(userPromptChars[c])) 

                else:
                    continue
            userinput = input(userPrompt)

        except KeyboardInterrupt:
            if INIT_VARIABLES["no-ctrlc"]:
                print("^C")
                userinput = "" # Empty the userinput variable instead of parsing it in.
            
            else:
                exit("\nShell closed manually.")
        
        executeLine(userinput)
        # Separate lines setting activated
        if INIT_VARIABLES["separate-commands"] and userinput != "":
            print(len(userPrompt + pathPrompt)*colored("=", "green"))
            
if __name__ == '__main__':
    main()    
