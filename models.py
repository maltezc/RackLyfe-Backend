"""SQLAlchemy models for ShareBNB."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

# TODO: USER DEFAULT IMAGE URL
DEFAULT_USER_IMAGE_URL = "testimage.jpg"
# TODO: POOL DEFAULT IMAGE URL
DEFAULT_POOL_IMAGE_URL = ""


# USERS
class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
        primary_key=True
    )

    image_url = db.Column(
        db.Text,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    # reserved_pools = db.relationship(
    #     'Pools',
    #     secondary='owner',
    #     backref='booker'
    # )

    # owned_pools = db.relationship(
    #     'Pools',
    #     secondary='booker',
    #     backref='owner'
    # )

    def serialize(self):
        """ returns self """
        return {
            "username" : self.username,
            "email" : self.email,
            "location" : self.location,
            "image_url" : self.image_url,

            # "reserved_pools" : self.reserved_pools,
            # "owned_pools" : self.owned_pools
        }

    @classmethod
    def signup(cls, username, email, password, location, image_url=DEFAULT_USER_IMAGE_URL):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            location=location
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def __repr__(self):
        return f"<User #{self.username}, {self.email}>"


# Messages
class Message(db.Model):
    "Messages between users in the system"

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # userid to
    sender_username = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    # userid from
    recipient_username = db.Column(
        db.Text,
        db.ForeignKey('users.username'),
        nullable=False
    )

    # text
    title = db.Column(
        db.Text,
        # nullable=False,
    )
    # text
    body = db.Column(
        db.Text,
        nullable=False,
    )

    #listing message is associated with
    listing = db.Column(
        db.Integer,
        nullable=False,
    )

    # timestamp
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "sender_username" : self.sender_username,
            "recipient_username" : self.recipient_username,
            "body" : self.body,
            "title" : self.title,
            "listing" : self.listing,
            "timestamp" : self.timestamp

        }


# POOLS

class Pool(db.Model):
    """ Pool in the system """

    __tablename__ = 'pools'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    owner_username = db.Column(
        db.Text,
        db.ForeignKey("users.username"),
        nullable=False,
    )

    rate = db.Column(
        db.Numeric(10,2),
        nullable=False
    )

    size = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    city = db.Column(
        db.Text,
        nullable=False,
    )

    orig_image_url = db.Column(
        db.Text,
        nullable=False,
    )

    small_image_url = db.Column(
        db.Text,
        nullable=False,
    )


    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "owner_username" : self.owner_username,
            "rate" : self.rate,
            "size" : self.size,
            "description" : self.description,
            "city" : self.city,
            "orig_image_url": self.orig_image_url,
            "small_image_url": self.small_image_url
        }


class Reservation(db.Model):
    """ Connection of a User and Pool that they reserve """

    __tablename__ = "reservations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booked_username = db.Column(
        db.Text,
        db.ForeignKey("users.username", ondelete="CASCADE"),
    )

    pool_id = db.Column(
        db.Integer,
        db.ForeignKey("pools.id", ondelete="CASCADE"),
    )

    reservation_date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    start_date = db.Column(
        db.DateTime,
        nullable=False,
    )
    end_date = db.Column(
        db.DateTime,
        nullable=False,
    )

    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "username" : self.booked_username,
            "pool_id" : self.pool_id,
            "reservation_date_created" : self.reservation_date_created,
            "start_date" : self.start_date,
            "end_date" : self.end_date,
        }

class UserImage(db.Model):
    """ Connection from the user to their profile images. """

    __tablename__ = "user_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.Text,
        db.ForeignKey("users.username", ondelete="CASCADE"),
    )

    image_path = db.Column(
        db.Text,
        nullable = False
    )

class PoolImage(db.Model):
    """ One to many table connecting a pool to many image paths """

    __tablename__ = "pool_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    pool_owner = db.Column(
        db.Text,
        db.ForeignKey("users.username", ondelete="CASCADE"),
    )

    image_url = db.Column(
        db.Text,
        nullable = False
    )

    def serialize(self):
        """ returns self """
        return {
            "id" : self.id,
            "pool_owner" : self.pool_owner,
            "image_url" : self.image_url,
        }


# db
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)