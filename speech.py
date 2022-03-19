import speech_recognition as sr
import pyttsx3
import os.path

ASSISTANT_ANSWER_FILENAME = os.path.abspath('static\\music\\answer.wav')
engine = pyttsx3.init()  # pyttsx3 engine


def recognize(file) -> str:
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file)
    with audio_file as source:
        audio_data = recognizer.record(source)
    recognized_data = recognizer.recognize_google(audio_data, language="en").lower()
    return recognized_data


def setup_assistant_voice():
    voices = engine.getProperty("voices")
    # The assistant's voice is
    # Microsoft Zira Desktop - English (United States)
    engine.setProperty("voice", voices[1].id)


def save_assistant_speech(text: str):
    # Add a command to save the synthesized speech
    engine.save_to_file(text, filename=ASSISTANT_ANSWER_FILENAME)

    engine.runAndWait()  # Execute engine commands
