import tkinter
import os



def main():
	
	# Main Window
	mainWindow = tkinter.Tk()
	
	mainWindow.title("Note app")
	
	# gadgets
	noteList = tkinter.Listbox(mainWindow)
	noteList.grid(row=0, column=0, sticky="s")
	
	
	
	
	
	
	mainWindow.mainloop()



	
if __name__ == "__main__":
	main()


