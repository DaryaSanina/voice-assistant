from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class Message:
    def __init__(self, text, sender):
        self.text = text
        self.sender = sender

    def __repr__(self):
        return self.text


class MessageInputForm(FlaskForm):
    text = StringField(validators=[DataRequired()], render_kw={"placeholder": "Type your message"})
