from json import loads, dumps, JSONDecodeError; import os;
from lib import *
import os
import shutil
from prettytable import PrettyTable as pt
__version__ = 1.0

# Contains the essential properties for a installer file
TEMPLATE = {
	"referenceCommand":str,
	"files":dict,
	"directories":list,
	"entryFile":str,
	"version":float
}

def guide(requestedGuides):
	guides = {
		"install":os.path.split(__file__)[0]+"/at_guides/install.md",
		"installer_example":os.path.split(__file__)[0]+"/at_guides/installer_example.md",
		"uninstall":os.path.split(__file__)[0]+"/at_guides/uninstall.md",
		"troubleshoot_launch":os.path.split(__file__)[0]+"/at_guides/launch_problems.md"
	}
	
	if requestedGuides == []:
		createBoxTitle("Available guides")
		for index, g in enumerate(guides):
			print(f"{index}....: {g}")
	
	for g in requestedGuides:
		if not g in guides:
			createErrorMessage(f"Couldn't find a guide for this -> '{g}'")
			
		else:
			print(open(guides[g], "r").read())
			print("Press <Enter> to continue...", end="")
			waitForKey("\r")




def install(addonFile, installFile):
	validConfigurationFile = True
	addonPath = os.path.split(addonFile)[0]

	# install file doesn't exist.
	if not os.path.isfile(installFile):
		createErrorMessage(f"The install file specified doesn't exist. ('{installFile}')")
		createErrorMessage(f"Cancelling installation...")

	else:
		installInfo = open(installFile, "r").read()

		try:
			installInfo = loads(installInfo)
		# not a json file
		except JSONDecodeError:
			createErrorMessage(f"The install file specified its corrupted or its not a valid install configuration file. ('{installFile}')")
			return


		# Loop through the elements on the template checking that all of them exist in the specified file
		createLogMessage("Checking properties of the install file.")
		for prop in TEMPLATE:
			if not prop in installInfo:
				createErrorMessage(f"The install file doesn't contain an essential property: '{prop}'.")
				validConfigurationFile = False


			else:
			    # Invalid type of configuration
				if type(installInfo[prop])  != TEMPLATE[prop]:
					createErrorMessage(f"This property's type its invalid: '{prop}' should be a '{TEMPLATE[prop]}', instead, it is a '{type(installInfo[prop])}'.")
					validConfigurationFile = False

		# The install file its corrupte or wrong
		if not validConfigurationFile:
			createErrorMessage(f"The install file specified its not valid due to the previous reasons specified. ('{installFile}')")

		else:
			createLogMessage("Starting addon installation...")
			currentConfig = open(addonFile, "r").read()

			try:
				currentConfig = loads(currentConfig)
			except JSONDecodeError:
				createErrorMessage("The addon configuration file its corrupted.")
				return

			# Check that the addon doesn't exist already
			if installInfo["referenceCommand"] in currentConfig["addons"]:
				createWarningMessage(f"There is already a command named '{installInfo['referenceCommand']}'")

			# Check that there isnt a folder with the same name
			if os.path.isdir(os.path.join(os.path.split(addonFile)[0], installInfo['referenceCommand'])):
				createErrorMessage(f"A folder for the new addon has been tried to be created, but there is already one with that name.")
				createErrorMessage("Cancelling installation.")
				return

			os.mkdir(os.path.join(os.path.split(addonFile)[0], installInfo['referenceCommand']))

			# Create the directories -------------------------
			for d in installInfo["directories"]:
				createLogMessage(f"Creating directory '{d}'...")
				try:
					os.mkdir(os.path.join(addonPath, installInfo["referenceCommand"],d))

				except Exception as e:
					createErrorMessage(f"A directory couldn't be created due to the following reason: '{e}'")
					createErrorMessage("Cancelling installation...")
					return

			# Move the files ----------------------------------
			for f in installInfo["files"]:
				createLogMessage(f"Copying file '{f}' into '{installInfo['files'][f]}'...")
				try:
					shutil.copyfile(f, os.path.join(addonPath, installInfo["referenceCommand"],installInfo["files"][f]))
				except Exception as e:
					createErrorMessage(f"A file couldn't be copied due to the following reason: '{e}'")
					createErrorMessage("Cancelling installation...")
					return
					
			
			# replace the addon configuration file with the new addon
			currentConfig["addons"][installInfo["referenceCommand"]]= {
				"entryFile":installInfo["entryFile"],
				"help":{} if not "help" in installInfo else  installInfo["help"],
				"version":installInfo["version"]
			}

			createLogMessage("Saving new addon configuration...")
			try:
				open(addonFile, "w").write(dumps(currentConfig))

			except Exception as e:
				createErrorMessage(f"There was an error while saving the new addon configuration.")
				return

			createLogMessage(f"The addon '{installInfo['referenceCommand']} has been installed succesfully.'")

			
def getHelp(addonFile, targetAddon):
	# Read the configuration file
	if not os.path.isfile(addonFile):
		createErrorMessage("The addon configuration file doesn't exist.")
	
	else:
		# find the addon
		try:
			addonConfig = loads(open(addonFile, "r").read())
		except Exception as e:
			createErrorMessage(f"The addon configuration file couldn't be read due to the following reason: {e}")
			return
		
		if not targetAddon in addonConfig["addons"]:
			createErrorMessage(f"Couldn't find the addon specified. ('{targetAddon}')")
			
		else:
			if addonConfig["addons"][targetAddon]["help"] == {}:
				createWarningMessage("No help found for this addon.")
			
			else:
				helpContent = addonConfig["addons"][targetAddon]["help"]
				createHelpText(helpContent)
		
	

def uninstall(addonFile, targetAddon):
	# Read the addon configuration file

	if not os.path.isfile(addonFile):
		createErrorMessage("The addon configuration file doesn't exist.")
		return

	currentConfig = open(addonFile, "r").read()

	try:
		currentConfig = loads(currentConfig)
	except JSONDecodeError:
		createErrorMessage("The addon configuration file it's corrupted.")

	if currentConfig["addons"] == {}:
		print("No addons installed.")
	
	# Check that the target addon its installed.
	if not targetAddon in currentConfig["addons"]:
		createErrorMessage(f"Couldn't find an addon called '{targetAddon}'.")

	else:
		del currentConfig["addons"][targetAddon]

		if not os.path.isdir(os.path.join(os.path.split(addonFile)[0], targetAddon)):
			createWarningMessage("Couldn't find a folder where the addon could be installed. The addon might be badly uninstalled.")

		else:
			createLogMessage(f"Removing installation folder for the addon '{targetAddon}'")
			try:
				shutil.rmtree(os.path.join(os.path.split(addonFile)[0], targetAddon))
			except Exception as e:
				createErrorMessage(f"An error has occurred while removing the installation folder for the addon '{targetAddon}'")
				craeteErrorMessage(e)
				craeteErrorMessage("Cancelling uninstallation...")
				return

			createLogMessage(f"Installation folder for the addon '{targetAddon}' has been succesfully removed.")

		# Save the new addon configuration into the addon file
		createLogMessage("Updating addon configuration file...")
		open(addonFile, "w").write(dumps(currentConfig))
		createLogMessage(f"The addon ('{targetAddon}') has been uninstalled.")

def list(addonFile):
	# Read the addon configuration file

	if not os.path.isfile(addonFile):
		createErrorMessage("The addon configuration file doesn't exist.")
		return

	currentConfig = open(addonFile, "r").read()

	try:
		currentConfig = loads(currentConfig)
	except JSONDecodeError:
		createErrorMessage("The addon configuration file it's corrupted.")

	if currentConfig["addons"] == {}:
		print("No addons installed.")

	else:
		createBoxTitle("Showing all addons installed...")

		p = pt()
		p.field_names = ["Reference command", "Version", "Entry file"]
		for a in currentConfig["addons"]:
			p.add_row([a, currentConfig["addons"][a]["version"], currentConfig["addons"][a]["entryFile"]])

		print(p)
