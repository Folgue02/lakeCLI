# HOW TO INSTALL AN ADDON IN LAKECLI

## Basics

### What is an addon?

Addons are **packages of files and folders that can be associated with a command** in the cli which can be executed later on.

## How does an addon structure look like?
````
| main_file.py
| lib.py
| installer.lci
````

## How do I install a lakeCLI addon package?
Using the following command:
```
at install installer.lci

or 

addontool install installer.lci
```

* (Remember to replace the `installer.lci` with the name of the installer file of the addon.)

## How does this work?
The addon tool reads the installer file (*which in the previous example would be `installer.lci`*), which contains the following contents:
* The name for the command
* The dictionary of **files present in the addon folder** and the destination path.
* The **list of directories** to be created.
* The addon's **version**.
* A dictionary that contains the **description** of the addon, and a list of **usage cases**

[Installer file example](installer_example.md)


