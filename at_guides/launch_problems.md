# Problems when launching an addon


## Windows

### Why does this happen?
The majority of the addons made for lakeCLI are made with python.
When an addon tries to be executed by the user, lakeCLI will try to open the entryFile with the default program related to it.
Some editors automatically link the ".py" file type with themselves, so when lakeCLI tries to open the entryFile, it will open the mentioned editor instead of executing the script.

### How do I fix this?
For fixing this you must go to control panel > Default Programs > search for the py file extension, and link it to the python interpreter.

## UNIX based operating systems

### Why does this happen?
The majority of the addons made for lakeCLI are made with python.
LakeCLI executes the entry file by doing a shell call. In order to be executed with the python interpreter, this scripts (the entryFile) must contain a "shebang".
If executing an addon written in python triggers an error such as:
```
file.py: 3: pythonkeyword: not found
```

### How do I fix this?
Or similar, try adding manually a shebang line at the start of the file, like the one below:
```python
#!/usr/bin/env python3
```

