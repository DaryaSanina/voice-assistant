import speech_recognition as sr


def recognize(file) -> str:
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file)
    with audio_file as source:
        audio_data = recognizer.record(source)
    recognized_data = recognizer.recognize_google(audio_data, language="en").lower()
    return recognized_data
