import re
import datetime

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

import events
from messages import Message
from forms import TextMessageInputForm, RegisterForm, LoginForm, match_registration_passwords,\
    check_registration_password_length, check_registration_password_case,\
    check_registration_password_letters_and_digits
import assistant
import speech

from data import db_session
from data.users import User

SERVER_ADDRESS_HOST = '127.0.0.1'
SERVER_ADDRESS_PORT = 8000

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))
login_manager = LoginManager()
login_manager.init_app(app)

sent_messages = list()
play_audio_answer = False
played_audio_answer = False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
    return render_template('index.html', title="Voice assistant", messages=sent_messages,
                           text_message_input_form=text_message_input_form,
                           play_audio_answer=play_audio_answer, close_tab=assistant.close_tab,
                           link_to_search=assistant.link_to_search, current_user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if not match_registration_passwords(form):
            return render_template('register.html', title='Registration', form=form,
                                   message="Passwords don't match", current_user=current_user)

        if not check_registration_password_length(form):
            return render_template('register.html', title='Registration', form=form,
                                   message="Password should be from 8 to 16 characters long",
                                   current_user=current_user)

        if not check_registration_password_case(form):
            return render_template('register.html', title='Registration', form=form,
                                   message="Password should contain letters in lower and upper cases",
                                   current_user=current_user)

        if not check_registration_password_letters_and_digits(form):
            return render_template('register.html', title='Registration', form=form,
                                   message="Password should contain latin letters, numbers and other symbols",
                                   current_user=current_user)

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Registration', form=form,
                                   message="There is already a user with the same username",
                                   current_user=current_user)

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration', form=form,
                                   message="There is already a user with the same email",
                                   current_user=current_user)

        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title="Registration", form=form,
                           current_user=current_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if re.fullmatch(r'[A-Za-z0-9]+@[A-Za-z0-9]+\.[a-z]+', form.username_or_email.data):
            # The user has inputted an email
            user = db_sess.query(User).filter(User.email == form.username_or_email.data).first()
        else:
            # The user has inputted a username
            user = db_sess.query(User).filter(User.username == form.username_or_email.data).first()

        if user and user.check_password(form.password.data):
            # The user has inputted correct password
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
    return render_template('login.html', title="Authorization", form=form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    speech.setup_assistant_voice()
    db_session.global_init("db/users.db")
    app.run(port=SERVER_ADDRESS_PORT, host=SERVER_ADDRESS_HOST, debug=True)
