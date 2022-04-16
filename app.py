import re
import datetime
import random

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

import events
from messages import Message
from forms import TextMessageInputForm, RegisterForm, LoginForm, ForgotPasswordForm, SettingsForm,\
    match_passwords, check_password_length,\
    check_password_case, check_password_letters_and_digits
import assistant
import speech
import send_email
import image
from global_variables import SERVER_ADDRESS_HOST, SERVER_ADDRESS_PORT

from data import db_session
from data.users import User
from data.sent_messages import SentMessage

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
text_to_play_audio = ""


@login_manager.user_loader
def load_user(user_id: int) -> User:
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['POST', 'GET'])
def index():
    global sent_messages, text_to_play_audio

    # Load the user's messages from the database
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user_id = current_user.id

        # Find the user's messages
        database_messages = db_sess.query(SentMessage)\
            .filter(SentMessage.user_id == user_id).all()

        # Load the user's messages
        sent_messages = list()
        for message in database_messages:
            sent_messages.append(Message(text=message.text, sender=message.sender))

    # Load the user's events from the database
    events.events = events.load_events(current_user)

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
        if event.time:  # The event has time

            # The event is in 10 minutes
            if not event.notification_10_minutes \
                and (datetime.datetime(year=event.date.year, month=event.date.month,
                                       day=event.date.day, hour=event.time.hour,
                                       minute=event.time.minute) - datetime.datetime.now()) \
                    < datetime.timedelta(minutes=10):
                time_left = "10 minutes"
                event.notification_10_minutes = True

            # The event is in 2 hours
            elif not event.notification_2_hours and not event.notification_10_minutes \
                and (datetime.datetime(year=event.date.year, month=event.date.month,
                                       day=event.date.day, hour=event.time.hour,
                                       minute=event.time.minute) - datetime.datetime.now()) \
                    < datetime.timedelta(hours=2):
                time_left = "2 hours"
                event.notification_2_hours = True

            # The event is in 24 hours
            elif not event.notification_24_hours and not event.notification_2_hours \
                    and not event.notification_10_minutes \
                    and (datetime.datetime(year=event.date.year, month=event.date.month,
                                           day=event.date.day, hour=event.time.hour,
                                           minute=event.time.minute) - datetime.datetime.now()) \
                    < datetime.timedelta(days=1):
                time_left = "1 day"
                event.notification_24_hours = True

        # The event doesn't have time
        elif not event.notification_24_hours \
                and (event.date - datetime.date.today()) < datetime.timedelta(days=1):
            # The event is in 1 day
            time_left = "1 day"
            event.notification_24_hours = True

        if time_left:  # If the event is in 1 day, 2 hours or 10 minutes
            sent_messages.append(Message(
                f"""You have an event in {time_left}
                Name: {event.name}
                Date: {event.date}
                Time: {event.time}
                Place: {event.place}""", 'assistant'))

    # Text message input form
    text_message_input_form = TextMessageInputForm()

    if request.method == 'POST':
        if text_to_play_audio:
            text_to_play_audio = ""

        if text_message_input_form.validate_on_submit():  # If the user has sent a text message
            # The user's message
            sent_messages.append(Message(text_message_input_form.text.data, 'user'))

            # The assistant's answer
            if current_user.is_authenticated:
                answer = assistant.answer(text_message_input_form.text.data, current_user.language)
            else:
                answer = assistant.answer(text_message_input_form.text.data)
            sent_messages.append(Message(answer, 'assistant'))
            text_to_play_audio = answer

        elif request.files.get('speech_recording') is not None:  # If speech is recorded
            speech_recording_file = request.files['speech_recording']  # Request the recorded speech

            # Recognize the speech
            if current_user.is_authenticated:
                recognized_data = speech.recognize(speech_recording_file,
                                                   user_language=current_user.language)
            else:
                recognized_data = speech.recognize(speech_recording_file)

            # The user's message
            sent_messages.append(Message(recognized_data, 'user'))

            # The assistant's answer
            if current_user.is_authenticated:
                answer = assistant.answer(recognized_data, user_language=current_user.language)
            else:
                answer = assistant.answer(recognized_data)
            sent_messages.append(Message(answer, 'assistant'))
            text_to_play_audio = answer

        # Update the database
        if current_user.is_authenticated:
            db_sess = db_session.create_session()
            user_id = current_user.id

            message = SentMessage(user_id=user_id, text=sent_messages[-2].text,
                                  sender=sent_messages[-2].sender)
            db_sess.add(message)

            message = SentMessage(user_id=user_id, text=sent_messages[-1].text,
                                  sender=sent_messages[-1].sender)
            db_sess.add(message)

            db_sess.commit()

        events.update_database(current_user)

        if assistant.log_out:
            assistant.log_out = False
            if current_user.is_authenticated:
                return redirect('/logout')

        return redirect('/')

    # Render HTML
    return render_template('index.html', title="Yana", messages=sent_messages,
                           text_message_input_form=text_message_input_form,
                           text_to_play_audio=text_to_play_audio,
                           link_to_search=assistant.link_to_search, current_user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        # The user has submitted the registration form and the data is valid

        if not match_passwords(register_form):
            # Passwords in "Password" and "Repeat password" fields don't match
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Passwords don't match", current_user=current_user)

        if not check_password_length(register_form):
            # The password is < 8 characters or > 16 characters
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Password should be from 8 to 16 characters long",
                                   current_user=current_user)

        if not check_password_case(register_form):
            # The password is only in lower case or only in upper case
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Password should contain letters in lower and upper cases",
                                   current_user=current_user)

        if not check_password_letters_and_digits(register_form):
            # The password doesn't have letters, digits or other ASCII symbols
            return render_template('register.html', title='Registration', form=register_form,
                                   message="Password should contain latin letters, numbers and other symbols",
                                   current_user=current_user)
        # The password is OK

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == register_form.username.data).first():
            # There is already a user with the same username
            return render_template('register.html', title='Registration', form=register_form,
                                   message="There is already a user with the same username",
                                   current_user=current_user)
        # The username is OK

        if db_sess.query(User).filter(User.email == register_form.email.data).first():
            # There is already a user with the same email
            return render_template('register.html', title='Registration', form=register_form,
                                   message="There is already a user with the same email",
                                   current_user=current_user)
        # The email is OK
        # All registration data is OK

        user = User(
            username=register_form.username.data,
            email=register_form.email.data
        )
        user.set_password(register_form.password.data)

        # Set the language
        if register_form.language.data:
            user.language = register_form.language.data

        # Set the image
        if register_form.image.data:
            file = register_form.image.data
            file.save(f'static\\images\\user_images\\{register_form.username.data}.png')
            image.resize_image(f'static\\images\\user_images\\{register_form.username.data}.png')
            user.path_to_image \
                = f'static\\images\\user_images\\{register_form.username.data}.png'
        else:
            user.path_to_image = 'static\\images\\default_user_image.png'

        db_sess.add(user)
        db_sess.commit()

        login_user(user, remember=True)
        return redirect('/')

    # The registration form data isn't valid
    return render_template('register.html', title="Registration", form=register_form,
                           current_user=current_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # The user has submitted the login form and the data is valid

        db_sess = db_session.create_session()
        if re.fullmatch(r'[A-Za-z0-9!-/:-@\[-`{-~]+@[A-Za-z0-9]+\.[a-z]+',
                        login_form.username_or_email.data):
            # The user has inputted an email
            user = db_sess.query(User).filter(User.email == login_form.username_or_email.data)\
                .first()
            if not user:
                # The user has inputted a username
                user = db_sess.query(User)\
                    .filter(User.username == login_form.username_or_email.data).first()
        else:
            # The user has inputted a username
            user = db_sess.query(User)\
                .filter(User.username == login_form.username_or_email.data).first()

        if user and user.check_password(login_form.password.data):
            # The user has inputted correct password
            login_user(user, remember=login_form.remember_me.data)
            return redirect('/')

    # The login form data isn't valid
    return render_template('login.html', title="Authorization", form=login_form,
                           current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    global sent_messages

    sent_messages = list()  # Clear the messages
    logout_user()  # Logout
    return redirect('/')  # Redirect to the main page


@app.route('/forgot-password', methods=['POST', 'GET'])
def forgot_password():
    global user_email_address

    forgot_password_form = ForgotPasswordForm()
    if forgot_password_form.validate_on_submit():
        # The user has submitted the password recovery form and the data is valid

        db_sess = db_session.create_session()
        # Search for the user with email as in the form
        user = db_sess.query(User).filter(User.email == forgot_password_form.email.data).first()

        if user:  # There is a user with email as in the form
            user_email_address = forgot_password_form.email.data
            new_password = generate_password()  # Generate a new password
            # Send an email with the new password
            send_email.send_forgot_password_email(address=forgot_password_form.email.data,
                                                  password=new_password)

            # Change the password of the user with specified email
            user.set_password(new_password)
            db_sess.commit()
        else:
            redirect('/register')

        return "We've sent you a new password on your email"

    # The password recovery form data isn't valid
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


@app.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    db_sess = db_session.create_session()
    database_user = db_sess.query(User).filter(User.id == current_user.id).first()
    settings_form = SettingsForm()
    if settings_form.is_submitted():
        if settings_form.username.data:  # The user has changed their username
            if db_sess.query(User).filter(User.username == settings_form.username.data).first():
                # There is already a user with the same username
                return render_template('settings.html', title='Settings', form=settings_form,
                                       message="There is already a user with the same username",
                                       current_user=current_user)
            # The username is OK

            current_user.username = settings_form.username
            database_user.username = settings_form.username

        if settings_form.email.data:  # The user has changed their email
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == settings_form.email.data).first():
                # There is already a user with the same email
                return render_template('settings.html', title='Settings', form=settings_form,
                                       message="There is already a user with the same email",
                                       current_user=current_user)
            # The email is OK

            current_user.email = settings_form.email
            database_user.email = settings_form.email

        if settings_form.password.data:  # The user has changed their password
            if not match_passwords(settings_form):
                # Passwords in "Password" and "Repeat password" fields don't match
                return render_template('settings.html', title='Registration', form=settings_form,
                                       message="Passwords don't match", current_user=current_user)

            if not check_password_length(settings_form):
                # The password is < 8 characters or > 16 characters
                return render_template('settings.html', title='Registration', form=settings_form,
                                       message="Password should be from 8 to 16 characters long",
                                       current_user=current_user)

            if not check_password_case(settings_form):
                # The password is only in lower case or only in upper case
                return render_template('settings.html', title='Registration', form=settings_form,
                                       message="Password should contain letters in lower and upper cases",
                                       current_user=current_user)

            if not check_password_letters_and_digits(settings_form):
                # The password doesn't have letters, digits or other ASCII symbols
                return render_template('settings.html', title='Registration', form=settings_form,
                                       message="Password should contain latin letters, numbers and other symbols",
                                       current_user=current_user)
            # The password is OK

            current_user.set_password(settings_form.password.data)
            database_user.set_password(settings_form.password.data)

        if settings_form.language.data:  # The user has changed their language
            current_user.language = settings_form.language.data
            database_user.language = settings_form.language.data

        if settings_form.image.data:  # The user has changed their image
            file = settings_form.image.data
            file.save(f'static\\images\\user_images\\{current_user.username}.png')
            image.resize_image(f'static\\images\\user_images\\{current_user.username}.png')

        db_sess.commit()
        return redirect('/')
    return render_template('settings.html', title='Registration', form=settings_form,
                           current_user=current_user)


def generate_password() -> str:
    # Generate a password (8 to 16 characters)
    # with lowercase and uppercase letters, digits and other ASCII symbols

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
        # Generate a symbol
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
    db_session.global_init("db/users.db")
    app.run(port=SERVER_ADDRESS_PORT, host=SERVER_ADDRESS_HOST)
