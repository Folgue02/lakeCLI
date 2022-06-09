# Problems when launching an addon

## Windows

### Why does this happen?
The majority of the addons made for lakeCLI are **written in python**.
When an addon tries to be executed by the user, lakeCLI will try to open the `entryFile` with the default program associated to it.
Some editors automatically link the `".py"` file extension type with themselves, so when lakeCLI tries to open the `entryFile`, it will open the mentioned editor instead of executing the script.

### How do I fix this?
By changing the application associated to the `".py"` extension to the python interpreter.
This can be done through `Control panel > Default Programs > *search for the py file extension*`, and link it to the python interpreter.

## UNIX based operating systems

### Why does this happen?
The majority of the addons made for lakeCLI are made with python.
LakeCLI *executes the entry file by doing a shell call*. In order to be executed with the python interpreter, this scripts (the `entryFile`) must contain a *"shebang"*.
If executing an addon written in python triggers an error such as or similar:
```
file.py: 3: something: not found
```

### How do I fix this?
Try adding manually a shebang line at the start of the file, like the one below:
```python
#!/usr/bin/env python3
```
The part after `#!/usr/bin/env` can be either `python3`, `py`, `python`, depending on the aliases you have set for your shell.

