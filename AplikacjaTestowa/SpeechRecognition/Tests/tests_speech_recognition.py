import unittest
import os
import sys
import speech_recognition as sr
sys.path.append('..')
sys.path.append('../..')
import speech_recognition_wrapper as wrapper


class TestRecordingAndRecognition(unittest.TestCase):
    def setUp(self):
        self.AUDIO_Mikolaj_Balcerek = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Mikolaj_Balcerek_CLEAR.flac")
        self.AUDIO_Robert_Lewandowski = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Robert_Lewandowski_NOISE.flac")

    #tests just for speech recognition in Polish, not recording and noise detection
    def test_recognize_speech_google_bing_CLEAR_POLISH(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_Mikolaj_Balcerek) as source: audio = r.record(source)
        self.assertIn("Mikołaj Balcerek", [wrapper.recognize_speech(audio, r)], "Failed test to recognize speech \"Mikołaj Balcerek\" in a clear ALREADY PREPARED recording")

    def test_recognize_speech_google_bing_NOISE_POLISH(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_Robert_Lewandowski) as source: audio = r.record(source)
        self.assertIn("Robert Lewandowski", [wrapper.recognize_speech(audio, r)], "Failed test to recognize speech \"Rober Lewandowski\" in a noisy ALREADY PREPARED recording")


if __name__ == '__main__':
    unittest.main()
