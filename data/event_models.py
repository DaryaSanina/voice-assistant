import sqlalchemy
from .db_session import SqlAlchemyBase

import datetime


class EventModel(SqlAlchemyBase):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))

    def __init__(self, user_id: int, name: str, date: datetime.date, time: datetime.time, place: str):
        super(EventModel, self).__init__()
        self.user_id = user_id
        self.name = name
        self.date = date
        self.time = time
        self.place = place
