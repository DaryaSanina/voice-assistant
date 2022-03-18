from flask import Flask, render_template, redirect, request
from messages import Message, TextMessageInputForm
import assistant
import speech

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))

sent_messages = list()


@app.route('/', methods=['POST', 'GET'])
def main():
    # Text message input form
    text_message_input_form = TextMessageInputForm()
    if request.method == 'POST':
        if text_message_input_form.validate_on_submit():  # If the user has sent a text message
            # The user's message
            sent_messages.append(Message(text_message_input_form.text.data, 'user'))

            # The assistant's answer
            sent_messages.append(
                Message(assistant.answer(text_message_input_form.text.data), 'assistant'))

            return redirect('/')

        elif request.files.get('speech_recording') is not None:  # If speech is recorded
            speech_recording_file = request.files['speech_recording']  # Request the recorded speech
            recognized_data = speech.recognize(speech_recording_file)  # Recognize the speech

            # The user's message
            sent_messages.append(Message(recognized_data, 'user'))

            # The assistant's answer
            sent_messages.append(Message(assistant.answer(recognized_data), 'assistant'))

            return redirect('/')

    # Render HTML
    print(sent_messages)
    return render_template('index.html', messages=sent_messages,
                           text_message_input_form=text_message_input_form)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1', debug=True)
