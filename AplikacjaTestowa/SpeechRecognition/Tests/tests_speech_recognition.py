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

    def test_smart_recording_and_recognition_clear(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_Mikolaj_Balcerek) as source: audio = r.record(source)
        self.assertIn([wrapper.record_and_recognize()], "Mikołaj Balcerek")



if __name__ == '__main__':
    unittest.main()
