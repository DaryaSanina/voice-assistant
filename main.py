from flask import Flask, render_template, redirect
from messages import Message, TextMessageInputForm, VoiceMessageInputForm
from assistant import Assistant

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))
assistant = Assistant()

is_recording_audio = False


@app.route('/', methods=['POST', 'GET'])
def main():
    text_message_input_form = TextMessageInputForm()
    if text_message_input_form.validate_on_submit():
        sent_messages.append(Message(text_message_input_form.text.data, 'user'))
        sent_messages.append(
            Message(assistant.answer(text_message_input_form.text.data), 'assistant'))
        return redirect('/')

    if is_recording_audio:
        # TODO
        pass

    return render_template('main_page.html', messages=sent_messages,
                           text_message_input_form=text_message_input_form)


@app.route('/record', methods=['GET', 'POST'])
def start_recording():
    global is_recording_audio
    is_recording_audio = True
    return redirect('/')


if __name__ == '__main__':
    sent_messages = list()
    app.run(port=8000, host='127.0.0.1')
