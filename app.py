from flask import Flask, render_template, redirect, request
from messages import Message, TextMessageInputForm
from assistant import Assistant

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))
assistant = Assistant()

is_recording_audio = False


@app.route('/', methods=['POST', 'GET'])
def main():
    # Text message input form
    text_message_input_form = TextMessageInputForm()
    if text_message_input_form.validate_on_submit():
        sent_messages.append(Message(text_message_input_form.text.data, 'user'))
        sent_messages.append(
            Message(assistant.answer(text_message_input_form.text.data), 'assistant'))
        return redirect('/')

    # Record audio
    if request.method == 'POST':
        audio_file = request.files['speech_recording']
        # TODO

    # Render HTML
    return render_template('index.html', messages=sent_messages,
                           text_message_input_form=text_message_input_form)


if __name__ == '__main__':
    sent_messages = list()
    app.run(port=8000, host='127.0.0.1', debug=True, threaded=True)
