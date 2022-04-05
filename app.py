from flask import Flask, render_template, redirect, request
import datetime
import os

import events
from messages import Message, TextMessageInputForm
import assistant
import speech

SERVER_ADDRESS_HOST = '127.0.0.1'
SERVER_ADDRESS_PORT = 8000

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))

sent_messages = list()
play_audio_answer = False
played_audio_answer = False


@app.route('/', methods=['POST', 'GET'])
def index():
    global play_audio_answer, played_audio_answer

    if play_audio_answer and not played_audio_answer:
        played_audio_answer = True
    elif play_audio_answer and played_audio_answer:
        play_audio_answer = False
        played_audio_answer = False

    # Delete past events
    i = 0
    while i < len(events.events):
        if events.events[i].time \
                and (events.events[i].date == datetime.date.today()
                     and events.events[i].time <= datetime.datetime.now().time()) \
                or events.events[i].date < datetime.date.today():
            del events.events[i]
        else:
            i += 1

    # Notify the user about upcoming events
    for event in events.events:
        time_left = ""
        if event.time:
            if not event.notification_10_minutes \
                and (datetime.datetime(year=event.date.year, month=event.date.month,
                                       day=event.date.day, hour=event.time.hour,
                                       minute=event.time.minute) - datetime.datetime.now()) \
                    < datetime.timedelta(minutes=10):
                time_left = "10 minutes"
                event.notification_10_minutes = True

            elif not event.notification_2_hours \
                and (datetime.datetime(year=event.date.year, month=event.date.month,
                                       day=event.date.day, hour=event.time.hour,
                                       minute=event.time.minute) - datetime.datetime.now()) \
                    < datetime.timedelta(hours=2):
                time_left = "2 hours"
                event.notification_2_hours = True

            elif not event.notification_24_hours \
                    and (datetime.datetime(year=event.date.year, month=event.date.month,
                                           day=event.date.day, hour=event.time.hour,
                                           minute=event.time.minute) - datetime.datetime.now()) \
                    < datetime.timedelta(days=1):
                time_left = "1 day"
                event.notification_24_hours = True

        elif not event.notification_24_hours \
                and (event.date - datetime.date.today()) < datetime.timedelta(days=1):
            time_left = "1 day"
            event.notification_24_hours = True

        if time_left:
            sent_messages.append(Message(
                f"""You have an event in {time_left}
                Name: {event.name}
                Date: {event.date}
                Time: {event.time}
                Place: {event.place}""", 'assistant'))

    # Text message input form
    text_message_input_form = TextMessageInputForm()
    if request.method == 'POST':
        if play_audio_answer:
            play_audio_answer = False
        if assistant.close_tab:
            assistant.close_tab = False

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
        return redirect('/')

    # Render HTML
    return render_template('index.html', messages=sent_messages,
                           text_message_input_form=text_message_input_form,
                           play_audio_answer=play_audio_answer, close_tab=assistant.close_tab,
                           link_to_search=assistant.link_to_search)


if __name__ == '__main__':
    speech.setup_assistant_voice()
    app.run(port=SERVER_ADDRESS_PORT, host=SERVER_ADDRESS_HOST, debug=True)
