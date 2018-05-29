import speech_recognition as sr
import sys
sys.path.append('..')
import RecordingPackage.speech_recognition_recording

#this file handles speech recognition

def recognize_speech(AudioData : sr.AudioData, Recognizer : sr.Recognizer):
    r = Recognizer
    audio = AudioData
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        return r.recognize_google(audio, language="pl-PL")
    except:

        r.recognize_bing()
    #     print("Google Speech Recognition could not understand audio")
    # except sr.RequestError as e:
    #     print("Could not request results from Google Speech Recognition service; {0}".format(e))

def record_and_recognize():
    """
    Records voice and return AudioData and string with recognized text
    :return Audiodata, str recognized Text
    """
    AudioData, Recognizer = RecordingPackage.speech_recognition_recording.record_till_end_of_voice()
    return AudioData, str(recognize_speech(AudioData, Recognizer))
