import re
import datetime
import random

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

import events
from messages import Message
from forms import TextMessageInputForm, RegisterForm, LoginForm, ForgotPasswordForm,\
    match_registration_passwords, check_registration_password_length,\
    check_registration_password_case, check_registration_password_letters_and_digits
import assistant
import speech
import send_email
from global_variables import SERVER_ADDRESS_HOST, SERVER_ADDRESS_PORT

from data import db_session
from data.users import User

UNICODE_UPPERCASE_LETTER_CODES = list(range(65, 91))
UNICODE_LOWERCASE_LETTER_CODES = list(range(97, 123))
UNICODE_DIGIT_CODES = list(range(48, 58))
UNICODE_SYMBOL_CODES = list(range(33, 48)) + list(range(58, 65)) + list(range(91, 97)) \
                        + list(range(123, 127))

app = Flask(__name__)
app.config['SECRET_KEY'] = str(hash('secret_key'))
login_manager = LoginManager()
login_manager.init_app(app)

user_email_address = ''
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
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        if not match_registration_passwords(register_form):
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Passwords don't match", current_user=current_user)

        if not check_registration_password_length(register_form):
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Password should be from 8 to 16 characters long",
                                   current_user=current_user)

        if not check_registration_password_case(register_form):
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Password should contain letters in lower and upper cases",
                                   current_user=current_user)

        if not check_registration_password_letters_and_digits(register_form):
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Password should contain latin letters, numbers and other symbols",
                                   current_user=current_user)

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == register_form.username.data).first():
            return render_template('register.html', title='Registration', form=register_form,
                                   message="There is already a user with the same username",
                                   current_user=current_user)

        if db_sess.query(User).filter(User.email == register_form.email.data).first():
            return render_template('register.html', title='Registration', form=register_form,
                                   message="There is already a user with the same email",
                                   current_user=current_user)

        user = User(
            username=register_form.username.data,
            email=register_form.email.data
        )
        user.set_password(register_form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title="Registration", form=register_form,
                           current_user=current_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        db_sess = db_session.create_session()
        if re.fullmatch(r'[A-Za-z0-9!-/:-@\[-`{-~]+@[A-Za-z0-9]+\.[a-z]+',
                        login_form.username_or_email.data):
            # The user has inputted an email
            user = db_sess.query(User).filter(User.email == login_form.username_or_email.data)\
                .first()
        else:
            # The user has inputted a username
            user = db_sess.query(User).filter(User.username == login_form.username_or_email.data)\
                .first()

        if user and user.check_password(login_form.password.data):
            # The user has inputted correct password
            login_user(user, remember=login_form.remember_me.data)
            return redirect('/')
    return render_template('login.html', title="Authorization", form=login_form,
                           current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/forgot-password', methods=['POST', 'GET'])
def forgot_password():
    global user_email_address

    forgot_password_form = ForgotPasswordForm()
    if forgot_password_form.validate_on_submit():
        user_email_address = forgot_password_form.email.data
        new_password = generate_password()  # Generate a new password
        # Send an email with the new password
        send_email.send_forgot_password_email(address=forgot_password_form.email.data,
                                              password=new_password)

        # Change the password of the user with specified email
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == forgot_password_form.email.data).first()
        user.set_password(new_password)
        db_sess.commit()

        return "We've sent you a new password on your email"
    elif forgot_password_form.is_submitted():
        return render_template('forgot_password.html', title="Password recovery",
                               form=forgot_password_form, current_user=current_user,
                               message="Please enter your email")
    return render_template('forgot_password.html', title="Password recovery",
                           form=forgot_password_form, current_user=current_user)


@app.route('/revert-password')
def revert_password():
    # Revert the password of the user with specified email
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == user_email_address).first()
    user.hashed_password = user.previous_hashed_password
    db_sess.commit()
    return redirect('/')


def generate_password():
    length = random.randint(8, 16)
    uppercase_letters_count = min(random.randint(1, length - 3),
                                  len(UNICODE_UPPERCASE_LETTER_CODES))
    lowercase_letters_count = min(random.randint(1, length - uppercase_letters_count - 2),
                                  len(UNICODE_LOWERCASE_LETTER_CODES))
    digits_count = min(random.randint(1, length - uppercase_letters_count -
                                      lowercase_letters_count - 1),
                       len(UNICODE_DIGIT_CODES))
    symbols_count = min(length - uppercase_letters_count - lowercase_letters_count - digits_count,
                        len(UNICODE_LOWERCASE_LETTER_CODES))

    unicode_symbol_counts = dict()
    unicode_symbol_counts["uppercase letters"] = uppercase_letters_count
    unicode_symbol_counts["lowercase letters"] = lowercase_letters_count
    unicode_symbol_counts["digits"] = digits_count
    unicode_symbol_counts["symbols"] = symbols_count

    password = list()
    while list(unicode_symbol_counts.keys()):
        key = random.choice(list(unicode_symbol_counts.keys()))
        if key == "uppercase letters":
            password.append(chr(random.choice(UNICODE_UPPERCASE_LETTER_CODES)))
        elif key == "lowercase letters":
            password.append(chr(random.choice(UNICODE_LOWERCASE_LETTER_CODES)))
        elif key == "digits":
            password.append(chr(random.choice(UNICODE_DIGIT_CODES)))
        elif key == "symbols":
            password.append(chr(random.choice(UNICODE_SYMBOL_CODES)))

        unicode_symbol_counts[key] -= 1
        if unicode_symbol_counts[key] <= 0:
            del unicode_symbol_counts[key]

    return ''.join(password)


if __name__ == '__main__':
    speech.setup_assistant_voice()
    db_session.global_init("db/users.db")
    app.run(port=SERVER_ADDRESS_PORT, host=SERVER_ADDRESS_HOST, debug=True)
