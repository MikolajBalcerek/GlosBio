import sys
sys.path.append('..')
import RecordingPackage.speech_recognition_recording
import RecordingPackage.simple_audio
import SpeechRecognition.speech_recognition_wrapper
import speech_recognition
import io
from tkinter import *

def startup():

    # Tkinter start loop
    root = Tk()
    frame = Frame(root,bg='#0555ff' )
    root.title('Głos Biometryczny')
    app = MyController(root)
    root.mainloop()
    #####################3

    #register_user(users_database)
    #print(users_database)


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
        self.view.setKom0Text("Przedstaw się do programu: ")

        text = self.model.register_user()
        self.view.setOutputText(text)
        self.parent.update()

class MyView(Frame):
    #Przed initem robimy szablon wszystkich labeli, guzików ect.
    def loadView(self):
        title = Label(self.frame, text="GŁOS BIOMETRYCZNY").grid(row = 0,column = 0)
        kom0 = Label(self.frame,textvariable = self.kom0_text).grid(row = 1, column = 0, columnspan = 3, sticky = EW)
        kom1 = Label(self.frame,textvariable = self.kom1_text).grid(row = 2, column = 0, columnspan = 3, sticky = EW)
        kom2  = Label(self.frame,textvariable = self.kom2_text).grid(row = 3, column = 0, columnspan = 3, sticky = EW)
        output = Label(self.frame,textvariable = self.output_text).grid(row = 4, column = 0, columnspan = 3, sticky = EW)
        runBtn = Button(self.frame, text ="Run", command = self.vc.runBtnPressed, relief='flat', bg="#999999").grid(row = 5,column = 0)
        quitBtn = Button(self.frame, text ="Quit", command = self.vc.quitButtonPressed, relief='flat', bg="#999999").grid(row = 5,column = 2)

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
        self.loadView()

    def setKom0Text(self, text):
        self.kom0_text.set(text)

    def setKom1Text(self, text):
        self.kom1_text.set(text)

    def setKom2Text(self, text):
        self.kom2_text.set(text)

    def setOutputText(self, text):
        self.output_text.set(text)

class MyModel():
    def __init__(self,vc):
        self.vc = vc
        self.users_database = {}

    def register_user(self):
        AudioData, text = SpeechRecognition.speech_recognition_wrapper.record_and_recognize(self.vc)
        self.vc.view.setOutputText(text)
        self.vc.parent.update()
        flac = io.BytesIO(AudioData.get_flac_data())
        RecordingPackage.simple_audio.play_from_file(flac)
        if(str(input("Czy jesteś zadowolony? T/N: ")) == "T"):

            self.users_database[text] = {"name" : text, "AudioData" : AudioData, "flac" : flac,
                                 "NumpyArray": RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(AudioData)['NumpyArray'],
                                 "fs": RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(AudioData)['fs']};
