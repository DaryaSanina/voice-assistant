import sqlalchemy
from .db_session import SqlAlchemyBase

from flask_login import UserMixin


class SentMessage(SqlAlchemyBase, UserMixin):
    __tablename__ = 'sent_messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    sender = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    def __init__(self, user_id, text, sender):
        super(SentMessage, self).__init__()
        self.user_id = user_id
        self.text = text
        self.sender = sender
