from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, FileField
from wtforms.validators import DataRequired

import re


class TextMessageInputForm(FlaskForm):
    text = StringField(validators=[DataRequired()], render_kw={"placeholder": "Type your message"})
    send = SubmitField('Send', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = EmailField(validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password_again = PasswordField(validators=[DataRequired()],
                                   render_kw={"placeholder": "Repeat password"})
    image = FileField('Image')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username_or_email = StringField(validators=[DataRequired()],
                                    render_kw={"placeholder": "Username or email"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Log in')


def check_registration_password_length(form: RegisterForm):
    return 8 <= len(form.password.data) <= 16


def check_registration_password_letters_and_digits(form: RegisterForm):
    return re.fullmatch(r'[!-~]+', form.password.data) and re.findall(r'[A-Z]', form.password.data) \
           and re.findall(r'[a-z]', form.password.data) and re.findall(r'[0-9]', form.password.data) \
           and re.findall(r'[!-/:-@\[-`{-~]', form.password.data)


def check_registration_password_case(form: RegisterForm):
    return form.password.data != form.password.data.lower() \
           and form.password.data != form.password.data.upper()


def match_registration_passwords(form: RegisterForm):
    return form.password.data == form.password_again.data
