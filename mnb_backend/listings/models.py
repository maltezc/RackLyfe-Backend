"""Models for listings"""
from mnb_backend.database import db
from mnb_backend.enums import enum_serializer, PriceEnums, RentalDurationEnum, ListingStatusEnum
from sqlalchemy import Enum as SQLAlchemyEnum


# region Listings
class Listing(db.Model):
    """ Listing in the system """

    __tablename__ = 'listings'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    owner = db.relationship("User", back_populates="listings", uselist=False)

    primary_image_url = db.Column(
        db.Text,
        nullable=False,
    )

    images = db.Relationship("ListingImage", back_populates="listing", uselist=True)

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

    rate_price = db.Column(
        SQLAlchemyEnum(PriceEnums, name='rental_price_enum'),
        nullable=False  # select from $1-$10 / week
    )

    rate_schedule = db.Column(
        SQLAlchemyEnum(RentalDurationEnum, name='rental_duration_enum'),
    )

    status = db.Column(
        SQLAlchemyEnum(ListingStatusEnum, name='listing_status_enum'),
        nullable=False
    )

    reservations = db.relationship('Reservation', back_populates='listing', uselist=True)

    def serialize(self):
        """ returns self """

        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "owner": self.owner.serialize(),
            "primary_image_url": self.primary_image_url,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "genre": self.genre,
            # "condition": enum_serializer(self.condition),
            "rate_price": enum_serializer(self.rate_price),
            "rate_schedule": enum_serializer(self.rate_schedule),
            "status": enum_serializer(self.status),
            "reservations": [reservation.serialize() for reservation in self.reservations]
        }

    def __repr__(self):
        return f"< Listing #{self.id}, " \
               f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}, Genre: {self.genre}, " \
               f"Price: {self.rate_price}, Schedule: {self.rate_schedule}, Status: {self.status} >"


# endregion