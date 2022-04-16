from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField, FileField,\
    SelectField
from wtforms.validators import DataRequired

import re
from googletrans import LANGUAGES


class TextMessageInputForm(FlaskForm):
    text = StringField(validators=[DataRequired()], render_kw={"placeholder": "Type your message"})
    send = SubmitField('')


class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = EmailField(validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password_again = PasswordField(validators=[DataRequired()],
                                   render_kw={"placeholder": "Repeat password"})
    languages = [LANGUAGES[key] for key in LANGUAGES.keys()]
    language = SelectField('Language', choices=languages, default="english")
    image = FileField('Image')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username_or_email = StringField(validators=[DataRequired()],
                                    render_kw={"placeholder": "Username or email"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class ForgotPasswordForm(FlaskForm):
    email = EmailField(validators=[DataRequired()], render_kw={"placeholder": "Email"})
    submit = SubmitField('Send email with new password')


class SettingsForm(FlaskForm):
    username = StringField(render_kw={"placeholder": "Username"})
    email = EmailField(render_kw={"placeholder": "Email"})
    password = PasswordField(render_kw={"placeholder": "Password"})
    password_again = PasswordField(render_kw={"placeholder": "Repeat password"})
    languages = [LANGUAGES[key] for key in LANGUAGES.keys()]
    language = SelectField('Language', choices=languages, default="english")
    image = FileField('Image')
    submit = SubmitField('Update')


def check_password_length(form):
    return 8 <= len(form.password.data) <= 16


def check_password_letters_and_digits(form):
    # Check if the password contains only latin letters, digits and other ASCII symbols
    return re.fullmatch(r'[!-~]+', form.password.data) and re.findall(r'[A-Z]', form.password.data) \
           and re.findall(r'[a-z]', form.password.data) and re.findall(r'[0-9]', form.password.data) \
           and re.findall(r'[!-/:-@\[-`{-~]', form.password.data)


def check_password_case(form):
    return form.password.data != form.password.data.lower() \
           and form.password.data != form.password.data.upper()


def match_passwords(form):
    # Match "Password" and "Repeat password" fields data
    return form.password.data == form.password_again.data
