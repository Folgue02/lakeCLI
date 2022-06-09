# ADDON INSTALLER FILE EXAMPLE


## LakeCLI Installer file example
```json
{
	// Command's alias
	"referenceCommand":"myCommandName", 
	// Information about the addon (description, and usage cases)
	"help":{ 
		"description":"The description of my addon.",
		"usage":{
			"myCommandName --aParameter:itsValue":"myCommandName will use <itsValue> to do something."
		},
	// File to be used as entry point when the alias its called in the shell
	"entryFile":"theFileToExecute.py",
	// List of files in the addon's folder and their destination paths.
	"files":{
		"directory1/aFileInADirectory.py":"directory1/itsDestiny.py",
		"theFileToExecute.py":"theFileToExecute.py"
		}
	},
	// Directories that will be created (they are created before `files` are copied to their destination paths)
	"directories":[
		"directory1",
		"directory1/directory2"
	],
	// Addons version
	"version":1.0
}

```
