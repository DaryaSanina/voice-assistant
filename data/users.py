import sqlalchemy
from .db_session import SqlAlchemyBase

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    previous_hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    language = sqlalchemy.Column(sqlalchemy.String)
    path_to_image = sqlalchemy.Column(sqlalchemy.String)

    def __init__(self, username: str, email: str):
        super(User, self).__init__()
        self.username = username
        self.email = email

    def set_password(self, password: str):
        # Hash the password and save it to the user table for the user
        self.previous_hashed_password = self.hashed_password  # Make current password previous
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str):
        # Check whether the password for the user is correct
        return check_password_hash(self.hashed_password, password)
