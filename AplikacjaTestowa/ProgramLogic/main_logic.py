import sys
sys.path.append('..')
import RecordingPackage.speech_recognition_recording
import RecordingPackage.simple_audio
import SpeechRecognition.speech_recognition_wrapper
import speech_recognition
import io
from tkinter import *
from tkinter.font import Font
from Plots.plots import basic_plots

def startup():

    # Tkinter start loop
    root = Tk()
    frame = Frame(root,bg='#0555ff')
    root.title('Głos Biometryczny')
    app = MyController(root)
    root.mainloop()


class MyController():
    def __init__(self,parent):
        self.parent = parent
        self.model = MyModel(self)
        self.view = MyView(self)

    def quitButtonPressed(self):
        self.parent.destroy()

    def runBtnPressed(self):
        self.view.kom0_text.set('')
        self.view.kom1_text.set('')
        self.view.kom2_text.set('')
        self.view.output_text.set('')
        self.view.question.set('')
        self.view.setKom0Text("Start programu: ")
        text = self.model.register_user()
        self.view.setOutputText(text)
        self.parent.update()

    def wykresBtnPressed(self):
        audio = RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(self.model.AudioData)
        basic_plots(audio['NumpyArray'], audio['fs'])

    def questionYes(self):
        self.view.kom0_text.set('')
        self.view.kom1_text.set('')
        self.view.kom2_text.set('')
        self.view.output_text.set('')
        self.view.question.set('')
        self.view.yesBtn.destroy()
        self.view.noBtn.destroy()
        self.model.users_database[self.model.text] = {"name" : self.model.text, "AudioData" : self.model.AudioData, "flac" : self.model.flac,
                             "NumpyArray": RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(self.model.AudioData)['NumpyArray'],
                             "fs": RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(self.model.AudioData)['fs']};

    def questionNo(self):
        self.view.kom0_text.set('')
        self.view.kom1_text.set('')
        self.view.kom2_text.set('')
        self.view.output_text.set('')
        self.view.question.set('')

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

class MyModel():
    def __init__(self,vc):
        self.vc = vc
        self.users_database = {}

    def register_user(self):
        self.AudioData, self.text = SpeechRecognition.speech_recognition_wrapper.record_and_recognize(self.vc)
        self.vc.view.setOutputText(self.text)
        self.vc.view.setQuestionYesNo("Czy jesteś zadowolony z efektu?")
        self.flac = io.BytesIO(self.AudioData.get_flac_data())
        RecordingPackage.simple_audio.play_from_file(self.flac)
        self.vc.view.setOutputText(self.text)