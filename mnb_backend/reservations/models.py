"""Models for reservations"""
from datetime import datetime

from mnb_backend.database import db
from mnb_backend.listings.models import Listing
from mnb_backend.enums import enum_serializer, ReservationStatusEnum
from sqlalchemy import Enum as SQLAlchemyEnum


# region reservations
class Reservation(db.Model):
    """ Connection of a User and Listing that they reserve """

    __tablename__ = "reservations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    listing_uid = db.Column(
        db.Integer,
        db.ForeignKey("listings.id"),
        # db.ForeignKey("books.id", ondelete="CASCADE"),
    )
    listing = db.relationship('Listing', back_populates='reservations', uselist=False)

    renter_id = db.Column(
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
        SQLAlchemyEnum(ReservationStatusEnum, name='reservation_status_enum'),
    )

    duration = db.Column(
        db.Interval,
        nullable=False
    )

    total = db.Column(
        db.Integer,
        nullable=False
    )

    cancellation_reason = db.Column(
        db.String(500),
    )

    def serialize(self):
        """ returns self """

        listing = self.listing

        return {
            "id": self.id,
            "reservation_date_created": self.reservation_date_created,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": enum_serializer(self.status),
            "duration": str(self.duration),
            "total": self.total,
            "cancellation_reason": self.cancellation_reason,
            # "book": book.serialize(),
            "listing_owner": listing.owner.serialize(),
            "listing_renter": self.renter.serialize(),
        }

    def __repr__(self):
        return f"< Reservation # {self.id}, DateCreated: {self.reservation_date_created}, DateStart{self.start_date}, " \
               f"EndDate: {self.end_date}, Status: {self.status}, Duration: {self.duration}, " \
               f"Total: {self.total}>, CancellationReason: {self.cancellation_reason} >"


# endregion