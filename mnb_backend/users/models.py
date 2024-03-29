"""Models for Users"""
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

from mnb_backend.database import db

from mnb_backend.enums import UserStatusEnums, enum_serializer
from sqlalchemy import Enum as SQLAlchemyEnum

from mnb_backend.auth.auth_helpers import is_valid_name, is_valid_email
from mnb_backend.errors import EmailAlreadyExistsError

bcrypt = Bcrypt()


# region Users
class User(db.Model):
    """ User model """

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    status = db.Column(
        SQLAlchemyEnum(UserStatusEnums, name='user_status_enum'),
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
        db.String(20),
        nullable=False,
    )

    lastname = db.Column(
        db.String(20),
        nullable=False,
    )

    about_me = db.Column(
        db.Text,
        nullable=False,
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    address = db.relationship('Address', uselist=False, back_populates='user', cascade='delete')

    image_url = db.Column(
        db.Text,
    )

    preferred_trade_location = db.Column(
        db.Text
    )
    # TODO: add preferred drop off method. (meetup, mailbox, porch, etc.)

    user_rating = db.Column(
        db.Integer,
        default=5.0
    )

    profile_image = db.relationship('UserImage', back_populates='user', uselist=False, lazy=True, cascade='delete')

    listings = db.relationship('Listing', back_populates='owner', uselist=True, lazy=True, cascade='delete')

    renting_reservations = db.relationship('Reservation', back_populates='renter',
                                           uselist=True, cascade='delete')  # TODO: need to figure this out.

    sent_messages = db.relationship('Message', back_populates='sender', foreign_keys='Message.sender_uid', lazy=True,
                                    uselist=True, cascade='delete')
    received_messages = db.relationship('Message', back_populates='recipient', foreign_keys='Message.recipient_uid',
                                        lazy=True, uselist=True, cascade='delete')

    def serialize(self):
        """ returns self """

        # TODO: check out marshmellow suggested by David for serializing:
        #  https://flask-marshmallow.readthedocs.io/en/latest/

        address_serialized = self.address.serialize() if self.address else None
        user_image_serialized = self.profile_image.serialize() if self.profile_image else None

        return {
            "id": self.id,
            "status": enum_serializer(self.status),
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "about_me": self.about_me,
            "is_admin": self.is_admin,
            "preferred_trade_location": self.preferred_trade_location,
            "user_rating": self.user_rating,
            "user_image": user_image_serialized,
            "address": address_serialized
        }

    @classmethod
    def signup(cls, email, password, firstname, lastname, about_me, status, is_admin=False):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        if is_valid_name(firstname) is False:
            raise ValueError("Invalid firstname")
        if is_valid_name(lastname) is False:
            raise ValueError("Invalid lastname")
        if is_valid_email(email) is False:
            raise ValueError("Invalid email")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise EmailAlreadyExistsError("Email already exists")

        try:
            user = User(
                email=email,
                password=hashed_pwd,
                firstname=firstname,
                lastname=lastname,
                about_me=about_me,
                status=status,
                is_admin=is_admin
            )

            db.session.add(user)
            db.session.commit()

            return user
        except:
            db.session.rollback()
            return "Failed to create user"

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
        return f"< User #{self.id}, Email: {self.email}, Firstname: {self.firstname}, Lastname: {self.lastname}, " \
               f"About Me:{self.about_me}, Status: {self.status}, is_admin: {self.is_admin} >"

# endregion
