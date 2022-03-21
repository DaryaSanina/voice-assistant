from flask import Flask, render_template, redirect, request
from messages import Message, TextMessageInputForm
import assistant
import speech

SERVER_ADDRESS_HOST = '127.0.0.1'
SERVER_ADDRESS_PORT = 8000

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))

sent_messages = list()
play_audio_answer = False


@app.route('/', methods=['POST', 'GET'])
def main():
    global play_audio_answer

    if play_audio_answer:
        play_audio_answer = False
    if assistant.close_tab:
        assistant.close_tab = False

    # Text message input form
    text_message_input_form = TextMessageInputForm()
    if request.method == 'POST':
        if text_message_input_form.validate_on_submit():  # If the user has sent a text message
            # The user's message
            sent_messages.append(Message(text_message_input_form.text.data, 'user'))

            # The assistant's answer
            sent_messages.append(
                Message(assistant.answer(text_message_input_form.text.data), 'assistant'))

        elif request.files.get('speech_recording') is not None:  # If speech is recorded
            speech_recording_file = request.files['speech_recording']  # Request the recorded speech
            recognized_data = speech.recognize(speech_recording_file)  # Recognize the speech

            # The user's message
            sent_messages.append(Message(recognized_data, 'user'))

            # The assistant's answer
            sent_messages.append(Message(assistant.answer(recognized_data), 'assistant'))

        play_audio_answer = True

    # Render HTML
    return render_template('index.html', messages=sent_messages,
                           text_message_input_form=text_message_input_form,
                           play_audio_answer=play_audio_answer, close_tab=assistant.close_tab)


if __name__ == '__main__':
    speech.setup_assistant_voice()
    app.run(port=SERVER_ADDRESS_PORT, host=SERVER_ADDRESS_HOST, debug=True)
