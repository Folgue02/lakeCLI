# Problems when launching an addon

## Why does this happen?
The majority for the addons made for lakeCLI are made with python.
When an addon tries to be executed by the user, lakeCLI will try to open the entryFile with the default program related to it.
Some editors automatically link the ".py" file type with themselves, so when lakeCLI tries to open the entryFile, it will open the mentioned editor instead of executing the script.

## How do I fix this?
For fixing this you must go to control panel > Default Programs > search for the py file extension, and link it to the python interpreter.