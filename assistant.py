import speech
import re

close_tab = False


def answer(user_message_text: str) -> str:
    answer_text = recognize_user_intention(user_message_text)
    speech.save_assistant_speech(answer_text)
    return answer_text


def recognize_user_intention(user_message_text: str) -> str:
    global close_tab

    # Greeting
    if re.findall(r"hello", user_message_text):
        return "Hello!"
    if re.findall(r"hi", user_message_text):
        return "Hi!"

    # Farewell
    if re.findall(r"bye", user_message_text):
        close_tab = True
        return "Bye!"

    return user_message_text
