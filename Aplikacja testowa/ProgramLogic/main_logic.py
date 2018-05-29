import sys
sys.path.append('..')
import RecordingPackage.speech_recognition_recording
import RecordingPackage.simple_audio
import SpeechRecognition.speech_recognition
import speech_recognition
import io

def startup():
    users_database = {}
    register_user(users_database)
    print(users_database)


def register_user(database):
    while(True):
        print("Przedstaw się do programu: ")
        AudioData, text = SpeechRecognition.speech_recognition.record_and_recognize()
        print(text)
        flac = io.BytesIO(AudioData.get_flac_data())
        RecordingPackage.simple_audio.play_from_file(flac)
        if(str(input("Czy jesteś zadowolony? T/N: ")) == "T"):

            database[text] = {"name" : text, "AudioData" : AudioData, "flac" : flac,
                              "NumpyArray": RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(AudioData)['NumpyArray'],
                              "fs": RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(AudioData)['fs']};


            break


