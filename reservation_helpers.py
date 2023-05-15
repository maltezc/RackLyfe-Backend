from datetime import timedelta, datetime

from flask import jsonify

from enums import RentalDurationEnum, ReservationStatusEnum
from models import db, Reservation


def create_reservation(start_date, duration, book_rate_schedule, book, user):
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

