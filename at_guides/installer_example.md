# INSTALLER EXAMPLE


## LakeCLI Installer file example
```json
{
	"referenceCommand":"myCommandName",
	"help":{
		"description":"The description of my addon.",
		"usage":{
			"myCommandName --aParameter:itsValue":"myCommandName will use <itsValue> to o something."
		},
	"entryFile":"theFileToExecute.py",
	"files":{
		"aFileInMyFolder.dll":"itsDestiny.dll",
		"theFileToExecute.py":"theFileToExecute.py"
		}
	},
	"directories":[
		"directory1",
		"directory1\directory2"
	],
	"version":1.0
}

```