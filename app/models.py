from app import db, login_manager

from flask import current_app
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """
    Define the User class with the following columns and relationships:
    id -- Column: Integer, PrimaryKey
    email -- Column: String(64), Unique
    username -- Column: String(64), Unique
    role_id -- Column: Integer, ForeignKey = roles.id
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    validated = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        Creates and stores password hash.
        :param password: String to hash.
        :return: None.
        """
        self.password_hash = generate_password_hash(password)

    # generates token with default validity for 1 hour
    def generate_reset_token(self, expiration=3600):
        """
        Generates a token users can use to reset their accounts if locked out.
        :param expiration: Seconds the token is valid for after being created (default one hour).
        :return: the token.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        session['reset_token'] = {'token': s, 'valid': True}
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        """
        Resets a user's password.
        :param token: The token to verify.
        :param new_password: The password the user will have after resetting.
        :return: True if operation is successful, false otherwise.
        """
        # checks if the new password is at least 8 characters with at least 1 UPPERCASE AND 1 NUMBER
        if not re.match(r'^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{8,128}$', new_password):
            return False
        # If the password has been changed within the last second, the token is invalid.
        if (datetime.now() - self.password_list.last_changed).seconds < 1:
            current_app.logger.error('User {} tried to re-use a token.'.format(self.email))
            raise InvalidResetToken
        self.password = new_password
        self.password_list.update(self.password_hash)
        db.session.add(self)
        return True

    def verify_password(self, password):
        """
        Checks user-entered passwords against hashes stored in the database.
        :param password: The user-entered password.
        :return: True if user has entered the correct password, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %r>' % self.email


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Job(db.Model):
    """
    Define the Job class with the following columns and relationships:
    id -- Column: Integer, PrimaryKey
    name -- Column: String(64)
    description -- Column: String(64)
    status -- Column: String(64)
    location -- Column: String(64)
    creator_id -- Column: Integer, ForeignKey = users.id
    accepted_id -- Column: Integer, ForeignKey = users.id, nullable = True
    rating -- Column: Integer, nullable = True
    review -- Column: String(500), nullable = True
    """
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(500))
    price = db.Column(db.Float(10))
    status = db.Column(db.String(64))
    location = db.Column(db.String(64))
    longitude = db.Column(db.Float(10))
    latitude = db.Column(db.Float(10))
    zipcode = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    accepted_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime)
    date_accepted = db.Column(db.DateTime, nullable=True)
    date_completed = db.Column(db.DateTime, nullable=True)


class JobRequestor(db.Model):
    """
    Define the Job class with the following columns and relationships:
    requestor_id -- Column: Integer, ForeignKey = users.id, PrimaryKey
    job_id -- Column: Integer, ForeignKey = jobs.id, PrimaryKey
    """
    __tablename__ = 'job_requestors'
    requestor_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), primary_key=True)
    price = db.Column(db.Float(10))
