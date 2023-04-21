"""SQLAlchemy models for ShareBNB."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

# TODO: USER DEFAULT IMAGE URL
DEFAULT_USER_IMAGE_URL = "testimage.jpg"
# TODO: Book DEFAULT IMAGE URL
DEFAULT_BOOK_IMAGE_URL = ""


# region Users
class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    user_uid = db.Column(
        db.Integer,
        primary_key=True
    )

    status = db.Column(
        db.Text,
        default="Active",
        nullable=False
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    firstname = db.Column(
        db.Text,
        nullable=False,
    )

    lastname = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
    )

    address_street = db.Column(
        db.Text,
        nullable=False
    )

    address_city = db.Column(
        db.Text,
        nullable=False
    )

    address_state = db.Column(
        db.Text,
        nullable=False
    )

    address_zipcode = db.Column(
        db.Integer,
        nullable=False
    )

    preferred_trade_location = db.Column(
        db.Text
    )

    user_rating = db.Column(
        db.Integer,
        default=5.0
    )

    # TODO: owned_books_for_rent

    # TODO: others_books_rented

    # TODO: reservations

    # reserved_books = db.relationship(
    #     'Books',
    #     secondary='owner',
    #     backref='booker'
    # )

    # owned_books = db.relationship(
    #     'Books',
    #     secondary='booker',
    #     backref='owner'
    # )

    owned_books = db.relationship('Book', backref='user')

    # reservations = db.relationship('Reservation', backref='user') # TODO: need to figure this out.

    def serialize(self):
        """ returns self """
        return {

            "user_uid": self.user_uid,
            "status": self.status,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "image_url": self.image_url,
            "address_street": self.address_street,
            "address_city": self.address_city,
            "address_state": self.address_state,
            "address_zipcode": self.address_zipcode,
            "preferred_trade_location": self.preferred_trade_location,
            "user_rating": self.user_rating

            # "owned_books" : self.owned_books
            # "reserved_books" : self.reserved_books,
        }

    @classmethod
    def signup(cls, email, password, firstname, lastname, address, preferred_trade_location,
               image_url=DEFAULT_USER_IMAGE_URL):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            firstname=firstname,
            lastname=lastname,
            address=address,
            preferred_trade_location=preferred_trade_location
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def __repr__(self):
        return f"<User #{self.email}"


# endregion


# region userimage
class UserImage(db.Model):
    """ Connection from the user to their profile images. """

    __tablename__ = "user_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    user_uid = db.Column(
        db.Integer,
        db.ForeignKey("users.user_uid", ondelete="CASCADE"),
    )

    image_path = db.Column(
        db.Text,
        nullable=False
    )


# endregion


# region Books
class Book(db.Model):
    """ Book in the system """

    __tablename__ = 'books'

    book_uid = db.Column(
        db.Integer,
        primary_key=True,
    )

    owner_uid = db.Column(
        db.Integer,
        db.ForeignKey("users.user_uid"),
        nullable=False,
    )

    orig_image_url = db.Column(
        db.Text,
        nullable=False,
    )

    title = db.Column(
        db.Text,
        nullable=False
    )

    author = db.Column(
        db.Text,
        nullable=False
    )

    isbn = db.Column(
        db.Text,
        nullable=False
    )

    genre = db.Column(
        db.Text,
        # nullable=False
    )

    condition = db.Column(
        db.Text,
        nullable=False

        # TODO: select form (like new, fair, old af)
    )

    price = db.Column(
        db.Integer,
        nullable=False  # select from $1-$10 / week
    )

    reservations = db.relationship('Reservation', backref='book')

    def serialize(self):
        """ returns self """
        return {

            "book_uid": self.book_uid,
            "owner_uid": self.owner_uid,
            "orig_image_url": self.orig_image_url,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "genre": self.genre,
            "condition": self.condition,
            "price": self.price
        }


# endregion


# region bookimage
class BookImage(db.Model):
    """ One to many table connecting a book to many image paths """

    __tablename__ = "book_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    book_owner_uid = db.Column(
        db.Integer,
        db.ForeignKey("users.user_uid", ondelete="CASCADE"),
    )

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    def serialize(self):
        """ returns self """
        return {
            "id": self.id,
            "book_owner": self.book_owner,
            "image_url": self.image_url,
        }


# endregion


# region reservations
class Reservation(db.Model):
    """ Connection of a User and Book that they reserve """

    __tablename__ = "reservations"

    reservation_uid = db.Column(
        db.Integer,
        primary_key=True
    )

    book_uid = db.Column(
        db.Integer,
        db.ForeignKey("books.book_uid", ondelete="CASCADE"),
    )

    owner_uid = db.Column(
        db.Integer,
        db.ForeignKey("users.user_uid", ondelete="CASCADE"),
    )

    renter_uid = db.Column(
        db.Integer,
        db.ForeignKey("users.user_uid", ondelete="CASCADE"),
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

    status = db.Column(
        db.Text,
        default="Booked"
    )

    rental_period_method = db.Column(
        db.Text,
        default="Days"
    )

    rental_period_duration = db.Column(
        db.Integer,
        nullable=False
    )

    total = db.Column(
        db.Integer,
        nullable=False
    )

    def serialize(self):
        """ returns self """
        return {
            "reservation_uid": self.reservation_uid,
            "book_uid": self.book_uid,
            "owner_uid": self.owner_uid,
            "renter_uid": self.renter_uid,
            "reservation_date_created": self.reservation_date_created,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "rental_period_method": self.rental_period_method,
            "rental_period_duration": self.rental_period_duration,
            "total": self.total
        }


# endregion


# region Messages

class Message(db.Model):
    "Messages between users in the system"

    __tablename__ = "messages"

    message_uid = db.Column(
        db.Integer,
        primary_key=True
    )

    # listing message is associated with
    reservation_uid = db.Column(
        db.Integer,
        nullable=False,
    )

    # userid to
    sender_uid = db.Column(
        db.Integer,
        db.ForeignKey('users.user_uid'),
        nullable=False
    )

    # userid from
    recipient_uid = db.Column(
        db.Integer,
        db.ForeignKey('users.user_uid'),
        nullable=False
    )

    # text
    message_text = db.Column(
        db.Text,
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

            "message_uid": self.message_uid,
            "res_uid": self.res_uid,
            "sender_uid": self.sender_uid,
            "recipient_uid": self.recipient_uid,
            "text": self.text,
            "timestamp": self.timestamp
        }


# endregion


# db
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
