# HOW TO INSTALL AN ADDON IN LAKECLI

## Basics
What is an addon?
```
Addons are packages of files and folders that can be associated with a command in the cli which can be executed later on.
```

## How does an addon structure look like?
* aMainFile.exe
* itsdependencies.dll
* folders
	* stuffinthefolders.txt

* installer.lci

## How do I install a lakeCLI addon package?
Using the following command:
```
at --tool:install installer.lci

or 

addontool --tool:install installer.lci
```

* (Remember to replace the installer.lci with the name of the installer file.)

## How does this work?
The addon tool reads the installer file, which contains the following contents:
* A command name by which it will run on the console after the installation
* A list of files that are in the folder of the package, and its destiny inside of their own folder in the addons folder.
* A list of directories that will be created
* The version of the addon
* A help dictionary that contains the description and some usage examples. (This is optional, so not all package will have it)

