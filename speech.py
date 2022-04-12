import speech_recognition as sr
from googletrans import LANGCODES


def recognize(file, user_language="english") -> str:
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file)
    with audio_file as source:
        audio_data = recognizer.record(source)
    recognized_data = recognizer.recognize_google(audio_data,
                                                  language=LANGCODES[user_language]).lower()
    return recognized_data
