"""Models for reservations"""
from datetime import datetime

from flask import jsonify

from mnb_backend.database import db
from mnb_backend.listings.models import Listing
from mnb_backend.enums import enum_serializer, ReservationStatusEnum
from sqlalchemy import Enum as SQLAlchemyEnum

from mnb_backend.reservations.reservation_helpers import get_time_duration_and_total


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

    # create upcoming filter property
    # create past filter property

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

    @classmethod
    def create_new_reservation(cls, start_date, duration, listing, user_renter):
        """ Function for creating a reservation"""

        if listing.owner.id == user_renter.id:
            return jsonify({"error": "The owner cannot rent out their own item."}), 400

        total, duration = get_time_duration_and_total(duration, listing)

        # TODO: ADD CHECK FOR RENTER AND OWNER CANNOT BE THE SAME USER

        try:
            reservation = Reservation(
                reservation_date_created=datetime.utcnow(),
                start_date=start_date,  # TODO: hook up with calendly to be able to coordinate pickup/dropoff times
                duration=duration,
                # duration=timedelta_duration,
                end_date=start_date + duration,
                # end_date=start_date + timedelta_duration,
                status=ReservationStatusEnum.PENDING,
                total=total
            )
            reservation.listing = listing
            reservation.renter = user_renter

            db.session.add(reservation)
            db.session.commit()

            return reservation

        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"error": "unable to create reservation"}), 400

    @classmethod
    def attempt_reservation_update(cls, reservation, start_date, duration):
        """ Function for updating a reservation"""

        # total, timedelta_duration, duration = get_time_duration_and_total(reservation.listing.rate_schedule, duration, reservation.listing)
        total, duration = get_time_duration_and_total(duration, reservation.listing)

        try:
            reservation.start_date = start_date
            reservation.duration = duration
            # reservation.duration = timedelta_duration
            reservation.end_date = start_date + duration
            # reservation.end_date = start_date + timedelta_duration
            reservation.total = total
            db.session.commit()

            return reservation

        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"error": "unable to create reservation"}), 400

# endregion
