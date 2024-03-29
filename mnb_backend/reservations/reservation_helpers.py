from datetime import timedelta, datetime
from werkzeug.exceptions import abort
from flask import jsonify

from mnb_backend.database import db
from mnb_backend.enums import RentalDurationEnum, ReservationStatusEnum
# from mnb_backend.reservations.models import Reservation


def get_time_duration_and_total(duration, listing):
# def get_time_duration_and_total(listing_rate_schedule, duration, listing):
    """ Function for getting the timedelta duration and total price of a reservation"""

    timedelta_duration = None
    # if listing_rate_schedule == RentalDurationEnum.DAILY:
    #     timedelta_duration = timedelta(days=duration)
    #
    # elif listing_rate_schedule == RentalDurationEnum.WEEKLY:
    #     timedelta_duration = timedelta(weeks=duration)
    #     duration = int(timedelta_duration.days / 7)

    total = duration.days * listing.rate_price
    # total = duration * listing.rate_price.value

    return total, duration
    # return total, timedelta_duration, duration


def reservation_is_in_future(reservation):
    """
    Function for checking if a reservation is in the future"""
    is_in_future = datetime.utcnow() < reservation.start_date
    return is_in_future


def attempt_to_cancel_reservation(reservation, reason):
    """
    Function for cancelling a reservation"""

    try:
        reservation.status = ReservationStatusEnum.CANCELLED
        reservation.cancellation_reason = reason
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(500, "Unable to cancel reservation")

    return reservation


def attempt_to_accept_reservation_request(reservation):
    """
    Function for accepting a reservation"""

    try:
        reservation.status = ReservationStatusEnum.ACCEPTED
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(500, description="Unable to accept reservation")

    return reservation


def attempt_to_decline_reservation_request(reservation):
    """
    Function for declining a reservation"""

    try:
        reservation.status = ReservationStatusEnum.DECLINED
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(500, description="Unable to decline reservation")

    return reservation
