"""Models for Users"""
from flask_bcrypt import Bcrypt
from mnb_backend.database import db

from mnb_backend.enums import UserStatusEnums, enum_serializer
from sqlalchemy import Enum as SQLAlchemyEnum

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

    address = db.relationship('Address', uselist=False, back_populates='user', lazy=True, cascade='delete-orphan')

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

    profile_image = db.relationship('UserImage', back_populates='user', uselist=False, lazy=True, cascade='delete-orphan')

    listings = db.relationship('Listing', back_populates='owner', uselist=True, lazy=True, cascade='delete-orphan')

    renting_reservations = db.relationship('Reservation', back_populates='renter',
                                           uselist=True)  # TODO: need to figure this out.

    sent_messages = db.relationship('Message', back_populates='sender', foreign_keys='Message.sender_uid', lazy=True,
                                    uselist=True)
    received_messages = db.relationship('Message', back_populates='recipient', foreign_keys='Message.recipient_uid',
                                        lazy=True, uselist=True)

    def serialize(self):
        """ returns self """

        # TODO: check out marshmellow suggested by David for serializing:
        #  https://flask-marshmallow.readthedocs.io/en/latest/

        address = self.address.serialize() if self.address else None
        user_image = self.profile_image.serialize() if self.profile_image else None

        return {
            "id": self.id,
            "status": enum_serializer(self.status),
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "is_admin": self.is_admin,
            "image_url": self.image_url,
            "preferred_trade_location": self.preferred_trade_location,
            "user_rating": self.user_rating,
            "user_image": user_image,
            "address": address
        }

    @classmethod
    def signup(cls, email, password, firstname, lastname, status, is_admin=False):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            email=email,
            password=hashed_pwd,
            firstname=firstname,
            lastname=lastname,
            status=status,
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
        return f"< User #{self.id}, Email: {self.email}, Firstname: {self.firstname}, Lastname: {self.lastname}, " \
               f"is_admin: {self.is_admin} >"

# endregion
