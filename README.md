# Lake **C**ommand **L**ine **I**nterface

## Getting started
LakeCLI its a command line made with python, it contains different built-in commands and the possibility to add addons.

### Requirements
- **Operative System**: Windows 8/10 & Linux 
- **Python version**:Python 3.X (Newer versions might need 3.10 or above due to new syntax)
- **Python libraries**:
	- termcolor
	- colorama
	- keyboard


### Installing
LakeCLI doesn't require any installation. Although, by default it creates a couple of files out of its original directory, which can be changed by
modifying the `autorun.lcs` file, and adding some parameters to the execution of `lake.py`

### Command line parameters
LakeCLI accepts command line arguments. This change the settings inside of the terminal.

#### Command line parameters example
```cmd
python3 lake.py --start-directory:/home/user/
```
This parameter sets the setting `start-directory` to `/home/user/`.\
Note that this settings can only be changed to a variable of the same type that they are by default. To see their default variable types, you can use the command `settings --show`, which will display a table that contains, the variable names, its value, and its variable type (str/int/bool).

### Autorun file
If the setting `run-autorun` is not set to `False` in the command line arguments, lakeCLI will look for a file named `autorun.lcs` in the same directory the script its located. The extension 'lcs' stands for *Lake CLI Script*. This file will be executed by lakeCLI. It is used to save settings and run commands every time the CLI its started. *This is also were the code to print the logo of lakeCLI its stored, feel free to remove it if it bothers you.*

## Authors
* Folgue  - [Folgue02](https://www.github.com/Folgue02)
