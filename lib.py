from termcolor import colored
import os
import sys
from fnmatch import fnmatch

# This libraries only work in windows
if sys.platform == "win32":
    from msvcrt import getch
    import win32api as w
    import win32con as wc

else:
    import keyboard

def createLogMessage(msg):
    print(colored("LOG: ", "green") + f"{msg}")

def createWarningMessage(msg):
    print(colored(f"WARNING: ", "yellow") +  f"{msg}")

def createErrorMessage(msg):
    print(colored(f"ERROR: ", "red") + f"{msg}")



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
        
    if "notes" in template:
        print(f"Notes: {template['notes']}")

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
    

def returnFileMatches(pattern: str) -> list:
    result = []

    path_to_look = os.path.split(pattern)[0]
    pattern = os.path.split(pattern)[1]

    if path_to_look == "":
        path_to_look = "."

    for x in os.listdir(path_to_look):
        if fnmatch(x, pattern):
            result.append(os.path.join(path_to_look, x))

    return result


    
def waitForKey(key):
    while True:
        if sys.platform != "win32":
            input("")
            break
        else:
            try:
                char = getch().decode("utf-8")
            except Exception: # In case of not being able to decode into utf-8 char
                return 

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



def resolveStringVariables(string:str, variables:dict) -> str:
    # This function resolves all the variables inside of the string, replacing the variables written 
    # in the string for its values

    # The string contains variables
    if fnmatch(string, "*$*$*"):
        while True:
            dollarPos = -1 # Contains the position of the first dollar sign found.

            # In case that all the variables in the string have been resolved
            # the loop will break
            if not fnmatch(string, "*$*$*"):
                break

            # The loop gets executed if there are still variables in it
            # It replaces the variables with their values, and, in case that there are two variables that are the same
            # they both get replaced in the same loop
            # Each loop replaces one variable.
            for index, char in enumerate(string):

                # The current character its a dollar sign
                if char == "$":
                    

                    # if dollarPos its different from its default value, it means that the first dollarSign of the 
                    # variable declaration has been found.
                    # So this replaces the variable, with its value
                    # In case that the variable doesn't exist, this will raise a KeyError exception
                    if dollarPos != -1:
                        string = string.replace(string[dollarPos:index+1], variables[string[dollarPos:index+1].replace("$", "")])
                        break   # Breaks the for loop, since the string of the loop has changed

                    else:
                        dollarPos = index # Stores the location of the first dollar sign of the variable.
                
                else:
                    pass
    return string




def getFileAttribs(targetFile):
    if sys.platform == "win32":
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

    if sys.platform == "darwin" or sys.platform == "linux":
        return "-UNKNOWN-"    


class table:
    def __init__(self, rowTitles:list, separator:str=" "):
        self.rowTitles = rowTitles
        self.content = []
        self.separator = separator



    def printTable(self):
        # Print the titles of the rows
        
        # Turn all rows into string lists
        for row in range(len(self.content)):
            for col in range(len(self.content[row])):
                self.content[row][col] = str(self.content[row][col])
        
        # Contains the width of each column
        widths = []
        for col in range(len(self.rowTitles)):
        
            # Default value for the width of the column
            colWidth = len(self.rowTitles[col])
        
            # Iterate through the entire column
            for row in range(len(self.content)):
                if len(self.content[row][col]) > colWidth:
                    colWidth = len(self.content[row][col])
                    
            widths.append(colWidth)
        
        # Print the table
        
        # Function to save time repeating code
        # Creates a string with the content of a column and the filling spaces
        createElement = lambda element, w: element + " "*(w - len(element))
        
        # Start with the column titles
        for index in range(len(self.rowTitles)):
            print(createElement(self.rowTitles[index], widths[index]), self.separator, end="")
        print()
        
        # Print the underline
        for index in range(len(self.rowTitles)):
            print("="*widths[index], self.separator, end="")
        print()
        
        # Print the content
        for row_index in range(len(self.content)):
            for col_index in range(len(self.content[row_index])):
                print(createElement(self.content[row_index][col_index], widths[col_index]), self.separator, end="")
                
            print() # Jumpline after each row printed
            
    def addContent(self, newContent:list):
        # Adds a row of content
        # The length of the list must be as long as the rowTitles length
        
        if len(newContent) != len(self.rowTitles):
            raise ValueError(f"The new row must contain '{len(self.rowTitles)}', instead, the new content had a length of '{len(self.rowTitles)}'")
            
        else:
            self.content.append(newContent)
    

        


if __name__ == "__main__":
    createBoxTitle(f"This script its designed to be a library and be imported by 'main.py'.")
    
