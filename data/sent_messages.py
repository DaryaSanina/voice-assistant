import sqlalchemy
from .db_session import SqlAlchemyBase


class SentMessage(SqlAlchemyBase):
    __tablename__ = 'sent_messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    sender = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    def __init__(self, user_id: int, text: str, sender: str):
        super(SentMessage, self).__init__()
        self.user_id = user_id
        self.text = text
        self.sender = sender
