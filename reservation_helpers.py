from datetime import timedelta, datetime

from flask import jsonify

from enums import RentalDurationEnum, ReservationStatusEnum
from models import Reservation
from database import db


def create_new_reservation(start_date, duration, book_rate_schedule, book, user):
    """ Function for creating a reservation"""

    total, timedelta_duration, duration = get_time_duration_and_total(book_rate_schedule, duration, book)

    try:
        reservation = Reservation(
            reservation_date_created=datetime.utcnow(),
            start_date=start_date,  # TODO: hook up with calendly to be able to coordinate pickup/dropoff times
            duration=timedelta_duration,
            end_date=start_date + timedelta_duration,
            status=ReservationStatusEnum.PENDING,
            total=total
        )
        reservation.book = book
        reservation.renter = user

        db.session.add(reservation)
        db.session.commit()

        return reservation

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "unable to create reservation"}), 400


def attempt_reservation_update(reservation, start_date, duration):
    """ Function for updating a reservation"""

    total, timedelta_duration, duration = get_time_duration_and_total(reservation.book.rate_schedule, duration,
                                                                      reservation.book)
    try:
        reservation.start_date = start_date
        reservation.duration = timedelta_duration
        reservation.end_date = start_date + timedelta_duration
        reservation.total = total
        db.session.commit()

        return reservation

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "unable to create reservation"}), 400


def get_time_duration_and_total(book_rate_schedule, duration, book):
    """ Function for getting the timedelta duration and total price of a reservation"""

    timedelta_duration = None
    if book_rate_schedule == RentalDurationEnum.DAILY:
        timedelta_duration = timedelta(days=duration)

    elif book_rate_schedule == RentalDurationEnum.WEEKLY:
        timedelta_duration = timedelta(weeks=duration)
        duration = int(timedelta_duration.days / 7)
    # TODO: HANDLE MONTHLY RENTAL DURATION
    total = duration * book.rate_price.value

    return total, timedelta_duration, duration


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
        return jsonify({"error": "unable to cancel reservation"}), 400

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
        return jsonify({"error": "unable to accept reservation"}), 400

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
        return jsonify({"error": "unable to decline reservation"}), 400

    return reservation


def extract_reservation_data(reservation):
    """
    Function for extracting reservation data"""

    book_title = reservation.book.title
    book_owner_name = f"{reservation.book.owner.firstname} {reservation.book.owner.lastname}"
    renter_name = f"{reservation.renter.firstname} {reservation.renter.lastname}"

    return book_title, book_owner_name, renter_name


def extract_serialized_data_from_multiple_reservations(reservations):
    """
    Function for extracting serialized data from multiple reservations"""

    data = [extract_reservation_data(reservation) for reservation in reservations]
    book_titles, book_owner_names, renter_names = zip(*data)

    serialized_reservations = [reservation.serialize(book_title, book_owner_name, renter_name)
                               for reservation, book_title, book_owner_name, renter_name
                               in zip(reservations, book_titles, book_owner_names, renter_names)]

    return serialized_reservations
