import sys
from ProgramLogic import MyModel, MyView
sys.path.append('..')
import RecordingPackage.speech_recognition_recording
import RecordingPackage.simple_audio
import speech_recognition
import io
from tkinter import *
from tkinter.font import Font
from Plots.plots import basic_plots

class MyController():
    def __init__(self,parent):
        self.parent = parent
        self.model = MyModel.MyModel(self)
        self.view = MyView.MyView(self)

    def quitButtonPressed(self):
        self.parent.destroy()

    def runBtnPressed(self):
        self.view.kom0_text.set('')
        self.view.kom1_text.set('')
        self.view.kom2_text.set('')
        self.view.output_text.set('')
        self.view.question.set('')
        self.view.setKom0Text("Start programu: ")
        self.model.record_user()
        RecordingPackage.simple_audio.play_from_file(self.model.flac)
        self.view.setOutputText(self.model.recorded_text)
        self.view.setQuestionYesNo("Czy jesteś zadowolony z efektu?")
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
        self.model.register_user()
        self.parent.update()

    def questionNo(self):
        self.view.kom0_text.set('')
        self.view.kom1_text.set('')
        self.view.kom2_text.set('')
        self.view.output_text.set('')
        self.view.question.set('')
