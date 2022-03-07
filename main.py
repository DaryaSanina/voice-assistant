from flask import Flask, render_template
from messages import Message

app = Flask(__name__)


@app.route('/')
def main():
    sent_messages = list()
    for i in range(100):
        if i % 3 == 0:
            sent_messages.append(Message(f'message {i}', 'user'))
        else:
            sent_messages.append(Message(f'message {i}', 'assistant'))
    return render_template('main_page.html', messages=sent_messages)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
