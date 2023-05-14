"""SQLAlchemy models for MNB."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geography, Geometry
from enums import RentalDurationEnum, PriceEnums
from sqlalchemy import Enum as SQLAlchemyEnum


bcrypt = Bcrypt()
db = SQLAlchemy()

# TODO: USER DEFAULT IMAGE URL
DEFAULT_USER_IMAGE_URL = "testimage.jpg"


# region Users
class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
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

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    address = db.relationship('Address', uselist=False, back_populates='user')

    image_url = db.Column(
        db.Text,
    )

    preferred_trade_location = db.Column(
        db.Text
    )

    user_rating = db.Column(
        db.Integer,
        default=5.0
    )

    profile_image = db.relationship('UserImage', back_populates='user', uselist=False)

    books = db.relationship('Book', back_populates='owner', uselist=True)

    renting_reservations = db.relationship('Reservation', back_populates='renter',
                                           uselist=True)  # TODO: need to figure this out.

    def serialize(self):
        """ returns self """
        # TODO: check out marshmellow suggested by David for serializing:
        #  https://flask-marshmallow.readthedocs.io/en/latest/
        return {
            "id": self.id,
            "status": self.status,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "is_admin": self.is_admin,
            "image_url": self.image_url,
            "preferred_trade_location": self.preferred_trade_location,
            "user_rating": self.user_rating
        }

    def serialize_with_address(self):
        """ returns self """

        return {
            "id": self.id,
            "status": self.status,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "is_admin": self.is_admin,
            "image_url": self.image_url,
            "preferred_trade_location": self.preferred_trade_location,
            "user_rating": self.user_rating,
            "address": self.address.serialize()
        }

    @classmethod
    def signup(cls, email, password, firstname, lastname, is_admin=False):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            email=email,
            password=hashed_pwd,
            firstname=firstname,
            lastname=lastname
        )

        db.session.add(user)
        db.session.commit()

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
        return f"< User #{self.id}, Email: {self.email}, Firstname: {self.firstname}, Lastname: {self.lastname}, is_admin: {self.is_admin} >"


# endregion


# region userimage
class UserImage(db.Model):
    """ Connection from the user to their profile images. """

    __tablename__ = "user_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )
    user = db.relationship('User', back_populates="profile_image", uselist=False)

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "image_url": self.image_url
        }

    def __repr__(self):
        return f"< UserImage #{self.id}, Image URL: {self.image_url} >"


# endregion


# region Address
class Address(db.Model):
    """ Address in the system. """

    __tablename__ = 'addresses'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )
    user = db.relationship('User', back_populates="address", uselist=False)

    street_address = db.Column(
        db.Text,
        nullable=False
    )

    apt_number = db.Column(
        db.Integer
    )

    city_uid = db.Column(
        db.Integer,
        db.ForeignKey('cities.id')
    )
    city = db.relationship('City', back_populates="addresses", uselist=False)

    zipcode_uid = db.Column(
        db.Integer,
        db.ForeignKey('zip_codes.id')
    )
    zipcode = db.relationship('ZipCode', back_populates="addresses", uselist=False)

    location = db.relationship('Location', back_populates="address", uselist=False)

    def __repr__(self):
        return f"< Address #{self.id}, Street Address: {self.street_address}, Apt Number: {self.apt_number}, City: {self.city}, Zipcode: {self.zipcode}, Location: {self.location} >"

    def serialize(self):
        """ returns self """

        return {
            "address_uid": self.id,
            "user_id": self.user_id,
            "street_address": self.street_address,
            "apt_number": self.apt_number,
        }


# endregion


# region Location
class Location(db.Model):
    """ User's geocoded Location point. """

    __tablename__ = 'locations'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    address_id = db.Column(
        db.Integer,
        db.ForeignKey('addresses.id')
    )
    address = db.relationship("Address", back_populates="location", uselist=False)

    point = db.Column(
        Geometry(geometry_type='POINT', srid=4326),
        # nullable=False
    )

    def __repr__(self):
        return f"< Location #{self.id} >"

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "point": self.point,
        }


# endregion


# region Cities
class City(db.Model):
    """ Model for City """

    __tablename__ = 'cities'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    addresses = db.relationship("Address", back_populates="city", uselist=True)

    city_name = db.Column(
        db.Text,
        nullable=False
    )

    state = db.relationship('State', back_populates="cities", uselist=False)

    def __repr__(self):
        return f"< City # {self.id}, City Name: {self.city_name} >"

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "city_name": self.city_name,
            "state_uid": self.state_uid
        }


# endregion

# region States
# NOTE: @LUCAS - keeping states to be able to do search by relationships.
class State(db.Model):
    """ A State for the address """

    __tablename__ = 'states'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    state_abbreviation = db.Column(
        db.String(2),
        db.CheckConstraint(
            "state_abbreviation in ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', "
            "'IL', 'IN','IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', "
            "'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', "
            "'WA', 'WV', 'WI', 'WY')"),
        unique=True
    )

    state_name = db.Column(
        db.String(15),
        unique=True
    )

    city_uid = db.Column(
        db.Integer,
        db.ForeignKey('cities.id')
    )
    cities = db.relationship('City', back_populates='state', uselist=True)

    def __repr__(self):
        return f"< State # {self.id}, State Abbreviation: {self.state_abbreviation}, State name: {self.state_name}>"

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "state_abbreviation": self.state_abbreviation,
            "state_name": self.state_name
        }


# endregion

# region Zipcodes

class ZipCode(db.Model):
    """ A zipcode for every city """
    __tablename__ = 'zip_codes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    code = db.Column(
        db.String(5),
        unique=True
    )

    addresses = db.relationship('Address', back_populates='zipcode', uselist=True)

    def __repr__(self):
        return f"< Zipcode # {self.id}, Code {self.code} >"

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "code": self.code
        }


# endregion




# region Books
class Book(db.Model):
    """ Book in the system """

    __tablename__ = 'books'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    owner_uid = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    owner = db.relationship("User", back_populates="books", uselist=False)

    primary_image_url = db.Column(
        db.Text,
        nullable=False,
    )

    images = db.Relationship("BookImage", back_populates="book", uselist=True)

    title = db.Column(
        db.Text,
        nullable=False
    )

    author = db.Column(
        db.Text,
        nullable=False
    )

    isbn = db.Column(
        db.BigInteger,
        nullable=False
    )

    genre = db.Column(
        db.Text,
    )

    # condition = db.Column(
    #     db.Text,
    #     nullable=False
    #
    #     # TODO: select form (like new, fair, old af)
    # )

    # condition = db.Column(
    #     db.Enum(ConditionEnum),
    #     default=ConditionEnum.LIKE_NEW,
    #     nullable=False,
    # )

    condition = db.Column(
        db.Text,
        nullable=False
    )

    rate_price = db.Column(
        SQLAlchemyEnum(PriceEnums, name='rental_price_enum'),
        nullable=False  # select from $1-$10 / week
    )

    rate_schedule = db.Column(
        SQLAlchemyEnum(RentalDurationEnum, name='rental_duration_enum'),
    )
    # default=RentalDurationEnum.WEEKLY,
    # db.Enum("Daily", "Weekly", "Monthly", name="ScheduleTypes"),

    status = db.Column(
        db.Text,
        default="Available",
        nullable=False
    )

    reservations = db.relationship('Reservation', back_populates='book', uselist=True)

    def serialize(self):
        """ returns self """
        return {

            "id": self.id,
            "owner_uid": self.owner_uid,
            "primary_image_url": self.primary_image_url,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "genre": self.genre,
            "condition": self.condition,
            "rate_price": self.rate_price,
            "rate_schedule": self.rate_schedule,
            "status": self.status,
            "reservations": [reservation.serialize() for reservation in self.reservations]
        }

    def __repr__(self):
        return f"< Book #{self.id}, " \
               f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}, Genre: {self.genre}, " \
               f"Condition: {self.condition}, Price: {self.rate_price}, Schedule: {self.rate_schedule}, Status: {self.status} >"


# endregion


# region bookimage

class BookImage(db.Model):
    """ One-to-many table connecting a book to many image paths """

    __tablename__ = "book_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id", ondelete="CASCADE"),
    )
    book = db.relationship('Book', back_populates='images', uselist=False)

    image_url = db.Column(
        db.Text,
        nullable=False
    )

    def serialize(self):
        """ returns self """
        return {
            "id": self.id,
            "book_id": self.book_id,
            "image_url": self.image_url,
        }

    def __repr__(self):
        return f"< BookImage #{self.id}, ImageUrl: {self.image_url} >"


# endregion


# region reservations
class Reservation(db.Model):
    """ Connection of a User and Book that they reserve """

    __tablename__ = "reservations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_uid = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        # db.ForeignKey("books.id", ondelete="CASCADE"),
    )
    book = db.relationship('Book', back_populates='reservations', uselist=False)

    # owner_uid = db.Column(
    #     db.Integer,
    #     db.ForeignKey("users.user_uid", ondelete="CASCADE"),
    # )
    # owner = db.relationship("User", back_populates="reservations")

    # renter_uid = db.Column(
    #     db.Integer,
    #     db.ForeignKey("users.id", ondelete="CASCADE"),
    # )

    # lender = db.relationship('User', back_populates='lending_reservations', uselist=False)
    # lender = book.owner

    # reservation_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey("reservations.id"),
    #     # db.ForeignKey("users.id", ondelete="CASCADE"), TODO: figure out when to apply on delete=CASCADE
    # )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        # db.ForeignKey("users.id", ondelete="CASCADE"), TODO: figure out when to apply on delete=CASCADE
    )
    renter = db.relationship('User', back_populates='renting_reservations', uselist=False)

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
        db.Interval,
        nullable=False
    )

    total = db.Column(
        db.Integer,
        nullable=False
    )

    def serialize(self):
        """ returns self """
        return {
            "id": self.id,
            # "book_uid": self.book_uid,
            # "owner_uid": self.owner_uid,
            # "renter_uid": self.renter_uid,
            "reservation_date_created": self.reservation_date_created,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "rental_period_method": self.rental_period_method,
            "rental_period_duration": self.rental_period_duration,
            "total": self.total
        }

    def __repr__(self):
        return f"< Reservation # {self.id}, DateCreated: {self.reservation_date_created}, DateStart{self.start_date}, " \
               f"EndDate: {self.end_date}, Status: {self.status}, RentalPeriodMethod: {self.rental_period_method}, " \
               f"Rental Period Duration: {self.rental_period_duration}, Rental Period Total: {self.total}>"


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
        db.ForeignKey('users.id'),
        nullable=False
    )

    # userid from
    recipient_uid = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
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
