from flask import Flask, render_template, redirect
from messages import Message, MessageInputForm
from assistant import Assistant

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))
assistant = Assistant()


@app.route('/', methods=['POST', 'GET'])
def main():
    message_input_form = MessageInputForm()
    if message_input_form.validate_on_submit():
        sent_messages.append(Message(message_input_form.text.data, 'user'))
        sent_messages.append(Message(assistant.answer(message_input_form.text.data), 'assistant'))
        return redirect('/')
    return render_template('main_page.html', messages=sent_messages, form=message_input_form)


if __name__ == '__main__':
    sent_messages = list()
    app.run(port=8000, host='127.0.0.1')
