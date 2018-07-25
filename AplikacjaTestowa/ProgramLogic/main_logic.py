import sys
from tkinter import *
sys.path.append('..')
from ProgramLogic import MyController

def startup():
    # Tkinter start loop
    root = Tk()
    frame = Frame(root,bg='#0555ff')
    root.title('Głos Biometryczny')
    app = MyController.MyController(root)
    root.mainloop()
