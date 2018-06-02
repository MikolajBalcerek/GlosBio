import sys
import AplikacjaTestowa.RecordingPackage.speech_recognition_recording
import AplikacjaTestowa.RecordingPackage.simple_audio
import AplikacjaTestowa.SpeechRecognition.recognize_speech
import recognize_speech
import io

def startup():
    users_database = {}
    register_user(users_database)
    print(users_database)


def register_user(database):
    while(True):
        print("Przedstaw się do programu: ")
        AudioData, text = AplikacjaTestowa.SpeechRecognition.recognize_speech.record_and_recognize()
        print(text)
        flac = io.BytesIO(AudioData.get_flac_data())
        AplikacjaTestowa.RecordingPackage.simple_audio.play_from_file(flac)
        if(str(input("Czy jesteś zadowolony? T/N: ")) == "T"):

            database[text] = {"name" : text, "AudioData" : AudioData, "flac" : flac,
                              "NumpyArray": AplikacjaTestowa.RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(AudioData)['NumpyArray'],
                              "fs": AplikacjaTestowa.RecordingPackage.speech_recognition_recording.convert_AudioData_to_Numpy_array_and_fs(AudioData)['fs']};


            break


