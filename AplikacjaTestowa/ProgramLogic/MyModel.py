import sys
import io
sys.path.append('..')
import SpeechRecognition.speech_recognition_wrapper
import RecordingPackage.speech_recognition_recording

class MyModel():
    def __init__(self,vc):
        self.vc = vc
        self.users_database = {}

    def record_user(self):
        """
        this method records user
        :return:
        """
        self.AudioData, self.recorded_text = SpeechRecognition.speech_recognition_wrapper.record_and_recognize(self.vc)
        self.flac = io.BytesIO(self.AudioData.get_flac_data())

    def register_user(self, name=None, audiodata = None, flac = None):
        """
        this registers the user, with no arguments passed registers the last recorded user
        :return:
        """
        if name == None:
            name = self.recorded_text
        if audiodata == None:
            audiodata = self.AudioData
        if flac == None:
            flac = self.flac
        self.users_database[name] = {"name": name, "AudioData": audiodata,
                                                      "flac": flac,
                                                      "NumpyArray":
                                                          RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(
                                                              audiodata)['NumpyArray'],
                                                      "fs":
                                                          RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(
                                                              audiodata)['fs']}
        print(self.users_database)