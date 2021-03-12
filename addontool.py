from json import loads, dumps, JSONDecodeError; import os;
from lib import *
import os
import shutil
__version__ = 0.1


TEMPLATE = {
	"referenceCommand":str,
	"files":dict,
	"directories":list,
	"entryCommand":str
}

def install(addonFile, installFile):
	validConfigurationFile = True
	addonPath = os.path.split(addonFile)[0]

	# install file doesn't exist.
	if not os.path.isfile(installFile):
		createErrorMessage(f"The install file specified doesn't exist. ('{installFile}')")

	else:
		installInfo = open(installFile, "r").read()

		try:
			installInfo = loads(installInfo)

		# not a json file
		except JSONDecodeError:
			createErrorMessage(f"The install file specified its corrupted or its not a valid install configuration file. ('{installFile}')")
			return

		print("Checking properties of the install file.")
		# Loop through the elements on the template checking that all of them exist in the specified file
		for prop in TEMPLATE:
			if not prop in installInfo:
				createErrorMessage(f"The install file doesn't contain an essential property: '{prop}'.")
				validConfigurationFile = False


			else:
			    # Invalid type of configuration
				if type(installInfo[prop])  != TEMPLATE[prop]:
					createErrorMessage(f"This property's type its invalid: '{prop}' should be a '{TEMPLATE[prop]}', instead, it is a '{type(installInfo[prop])}'.")
					validConfigurationFile = False

		if not validConfigurationFile:
			createErrorMessage(f"The install file specified its not valid due to the previous reasons specified. ('{installFile}')")

		else:
			print("Beginning addon installation...")
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

			# Create the directories
			for d in installInfo["directories"]:
				createLogMessage(f"Creating directory '{d}'...")
				try:
					os.mkdir(os.path.join(addonPath, installInfo["referenceCommand"],d))

				except Exception as e:
					createErrorMessage(f"A directory couldn't be created due to the following reason: '{e}'")
					createErrorMessage("Cancelling installation...")
					return

			# Move the files
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
				"entryCommand":installInfo["entryCommand"],
				"help":{} if not "help" in installFile else installFile["help"]
			}

			createLogMessage("Saving new addon configuration...")
			try:
				open(addonFile, "w").write(dumps(currentConfig))

			except Exception as e:
				createErrorMessage(f"There was an error while saving the new addon configuration.")
				return

			createLogMessage(f"The addon '{installInfo['referenceCommand']} has been installed succesfully.'")


