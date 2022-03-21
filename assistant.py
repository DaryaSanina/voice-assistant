import speech
import re


def answer(user_message_text: str) -> str:
    answer_text = recognize_user_intention(user_message_text)
    speech.save_assistant_speech(answer_text)
    return answer_text


def recognize_user_intention(user_message_text: str) -> str:
    # Greeting
    if re.findall(r"hello", user_message_text):
        return "Hello!"
    if re.findall(r"hi", user_message_text):
        return "Hi!"

    return user_message_text
