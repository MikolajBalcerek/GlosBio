from tkinter import *
from tkinter.font import Font
class MyView(Frame):
    #Przed initem robimy szablon wszystkich labeli, guzików ect.
    def loadView(self):
        title = Label(self.frame, text="GŁOS BIOMETRYCZNY", font=("Helvetica", 14)).grid(row = 0,column = 0, columnspan = 2, sticky = E, pady=30, padx=40)
        kom0 = Label(self.frame,textvariable = self.kom0_text, font=("Helvetica", 12)).grid(row = 1, column = 0, columnspan = 3, sticky = EW)
        kom1 = Label(self.frame,textvariable = self.kom1_text, font=("Helvetica", 12)).grid(row = 2, column = 0, columnspan = 3, sticky = EW)
        kom2  = Label(self.frame,textvariable = self.kom2_text, font=("Helvetica", 12)).grid(row = 3, column = 0, columnspan = 3, sticky = EW)
        output = Label(self.frame,textvariable = self.output_text, font=("Helvetica", 12)).grid(row = 4, column = 0, columnspan = 3, sticky = EW)
        question = Label(self.frame,textvariable = self.question, font=("Helvetica", 12)).grid(row = 5, column = 0, columnspan = 3, sticky = EW)
        runBtn = Button(self.frame, text ="Start", command = self.vc.runBtnPressed, relief='flat', bg="#999999", font=("Helvetica", 14)).grid(row = 7,column = 0, columnspan = 2, sticky = EW, padx=30)
        wykresBtn = Button(self.frame, text ="Wykres", command = self.vc.wykresBtnPressed, relief='flat', bg="#999999", font=("Helvetica", 14)).grid(row = 8,column = 0, columnspan = 2, sticky = EW, pady=10, padx=30)
        quitBtn = Button(self.frame, text ="Quit", command = self.vc.quitButtonPressed, relief='flat', bg="#999999", font=("Helvetica", 14)).grid(row = 9,column = 0, columnspan = 2, sticky = EW, pady=20, padx=30)

    def __init__(self,vc):
        self.frame = Frame()
        self.frame.grid(row = 0,column=0)
        self.vc = vc
        self.kom0_text = StringVar()
        self.kom0_text.set('')
        self.kom1_text = StringVar()
        self.kom1_text.set('')
        self.kom2_text = StringVar()
        self.kom2_text.set('')
        self.output_text = StringVar()
        self.output_text.set('')
        self.question = StringVar()
        self.question.set('')
        self.loadView()

    def setKom0Text(self, text):
        self.kom0_text.set(text)

    def setKom1Text(self, text):
        self.kom1_text.set(text)

    def setKom2Text(self, text):
        self.kom2_text.set(text)

    def setOutputText(self, text):
        self.output_text.set(text)

    def setQuestion(self, text):
        self.question.set(text)
        self.vc.parent.update()

    def setQuestionYesNo(self, text):
        """
        Sets a Yes/No question with text string and Yes/No buttons
        :param text: string text
        :return:
        """
        self.setQuestion(text)
        self.yesBtn = Button(self.vc.view.frame, text ="Tak", command = self.vc.questionYes, relief='flat', bg="#999999", font=("Helvetica", 14))
        self.yesBtn.grid(row = 6,column = 0, pady=20, sticky = EW, padx=30)
        self.noBtn = Button(self.vc.view.frame, text ="Nie", command = self.vc.questionNo, relief='flat', bg="#999999", font=("Helvetica", 14))
        self.noBtn.grid(row = 6,column = 1, pady=20, sticky = EW, padx=30)
        self.vc.parent.update()
