import os
import sys
import unittest
import speech_recognition as sr

from Backend.utils.speech_recognition_wrapper import speech_to_text_wrapper as wrapper


class TestSpeechToText(unittest.TestCase):
    def setUp(self):
        self.AUDIO_Mikolaj_Balcerek = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Mikolaj_Balcerek_CLEAR.flac")
        self.AUDIO_Robert_Lewandowski = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Robert_Lewandowski_NOISE.flac")
        self.AUDIO_Kornelia_Cwik = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Kornelia_Cwik.wav")

    #tests just for speech recognition in Polish, not recording and noise detection
    def test_recognize_speech_google_bing_CLEAR_POLISH_FLAC(self):
        with sr.AudioFile(self.AUDIO_Mikolaj_Balcerek) as audio:
            self.assertIn("Mikołaj Balcerek", [wrapper.recognize_speech(audio)], "Failed test to recognize speech \"Mikołaj Balcerek\" in a clear ALREADY PREPARED recording")

    def test_recognize_speech_google_bing_NOISE_POLISH_FLAC(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_Robert_Lewandowski) as audio:
            self.assertIn("Robert Lewandowski", [wrapper.recognize_speech(audio)], "Failed test to recognize speech \"Rober Lewandowski\" in a noisy ALREADY PREPARED recording")

    # test for wav female polish recording
    def test_recognize_speech_google_bing_NOISE_POLISH_FEMALE_WAV(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_Kornelia_Cwik) as audio:
            self.assertIn("Kornelia Ćwik",
                          [wrapper.recognize_speech(audio)],
                          "Failed test to recognize speech \"Kornelia Ćwik\" in a noisy polish wav ALREADY PREPARED recording")

    # test recognize speech from path
    def test_recognize_speech_from_path(self):
        self.assertIn("Kornelia Ćwik",
                      wrapper.recognize_speech_from_path(
                          self.AUDIO_Kornelia_Cwik),
                      "Failed test to recognize speech \"Kornelia Ćwik\" in a noisy polish wav ALREADY PREPARED recording taking from PATH (instead of file)")

if __name__ == '__main__':
    unittest.main()
