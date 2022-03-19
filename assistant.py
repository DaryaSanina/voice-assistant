import speech


def answer(user_message_text: str) -> str:
    # TODO
    answer_text = user_message_text
    speech.save_assistant_speech(answer_text)
    return answer_text
