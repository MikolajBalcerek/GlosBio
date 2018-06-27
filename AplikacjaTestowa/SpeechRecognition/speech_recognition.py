import speech_recognition as sr
import sys
sys.path.append('..')
import RecordingPackage.speech_recognition_recording
import secret_keys
#this file handles speech recognition

def recognize_speech(AudioData : sr.AudioData, Recognizer : sr.Recognizer):
    r = Recognizer
    audio = AudioData
    try:
        # GOOGLE
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        return r.recognize_google(audio, language="pl-PL")
    except:
        # BING
        return r.recognize_bing(audio, key=secret_keys.SECRET_BING_KEY, language="pl-PL")

def record_and_recognize(vc=None):
    """
    Records voice and return AudioData and string with recognized text
    :return Audiodata, str recognized Text
    """
    for tries in range(2):
        try:
            AudioData, Recognizer = RecordingPackage.speech_recognition_recording.record_till_end_of_voice(vc)
            return AudioData, str(recognize_speech(AudioData, Recognizer))
        except sr.RequestError as e:
            print("Could not request results {0}".format(e))
        except sr.UnknownValueError as e:
            print("Audio wasn't recognized")

    raise Exception("Couldn't recognize any of the samples: connection or recording issue")
