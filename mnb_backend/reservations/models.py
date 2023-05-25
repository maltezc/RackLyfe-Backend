"""Models for reservations"""
from datetime import datetime

from database import db
from enums import enum_serializer, ReservationStatusEnum
from sqlalchemy import Enum as SQLAlchemyEnum


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

        book = self.book

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
            "book_owner": book.owner.serialize(),
            "book_renter": self.renter.serialize(),
        }

    def __repr__(self):
        return f"< Reservation # {self.id}, DateCreated: {self.reservation_date_created}, DateStart{self.start_date}, " \
               f"EndDate: {self.end_date}, Status: {self.status}, Duration: {self.duration}, " \
               f"Total: {self.total}>, CancellationReason: {self.cancellation_reason} >"


# endregion