# dialog box
import tkinter
from tkinter import filedialog

main_win = tkinter.Tk()
main_win.geometry("1000x500")
main_win.sourceFolder = ''
main_win.sourceFile = ''

def chooseDir():

    main_win.sourceFolder = filedialog.askdirectory(parent=main_win, initialdir= "/", title='Please select a directory')

b_chooseDir = tkinter.Button(main_win, text = "Choose Folder", width=20, height=3, command=chooseDir)
b_chooseDir.place(x=50, y=50)
b_chooseDir.width=100

def chooseFile():
    main_win.sourceFile = filedialog.askopenfilename(parent=main_win, initialdir="/", title='Please select a directory')

b_chooseFile = tkinter.Button(main_win, text="Choose File", width=20, height=3, command=chooseFile)
b_chooseFile.place(x=250, y=50)
b_chooseFile.width=100

def closeDialog():
    main_win.destroy()

b_closeDialog = tkinter.Button(main_win, text="Confirm & Close", width=20, height=3, command=closeDialog)
b_closeDialog.place(x=250, y=125)
b_closeDialog.width=75


def return_path():
    main_win.mainloop()
    single_file = main_win.sourceFile
    multiple_files = main_win.sourceFolder + "/"
    if single_file == '': #error logic should be updated, doesn't work if dialog box is closed out
        if multiple_files == '':
            return 'ERROR: no file(s) selected'
        else:
            return multiple_files
    else:
        if single_file == '':
            return 'Error: no file(s) selected'
        return single_file

def filepath():
    path = return_path()
    return path

def main():
    print('Test of main function:')
    print('')
    print(filepath)

if __name__ == '__main__':
    filepath()
    main()