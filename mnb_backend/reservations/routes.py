"""Routes for reservations blueprint."""
from datetime import datetime, timedelta
from werkzeug.exceptions import abort

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from mnb_backend.listings.models import Listing
from mnb_backend.reservations.models import Reservation
from mnb_backend.users.models import User
from mnb_backend.reservations.reservation_helpers import reservation_is_in_future, \
    attempt_to_cancel_reservation, attempt_to_accept_reservation_request, attempt_to_decline_reservation_request

from mnb_backend.decorators import is_reservation_listing_owner, is_listing_owner_or_is_reservation_booker_or_is_admin, \
    is_reservation_booker

from mnb_backend.enums import ReservationStatusEnum

reservations_routes = Blueprint('reservations_routes_routes', __name__)


# region RESERVATIONS ENDPOINTS START

@reservations_routes.post("/<int:listing_uid>")
@jwt_required()
def create_reservation(listing_uid):
    """ Creates a reservation for the pool you're looking at if you are logged in

    Returns JSON like:
        {reservation: {reservation_uid, listing_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }}
    """

    current_user = get_jwt_identity()
    user = User.query.get_or_404(current_user)

    if user:
        data = request.form

        start_date_in = data.get('start_date')
        duration_in = data.get('duration')
        renter_in = data.get('renter')

        renter = User.query.get_or_404(renter_in)

        listing = Listing.query.get_or_404(listing_uid)
        start_date = datetime.strptime(start_date_in, '%Y-%m-%d')
        duration = timedelta(days=int(duration_in))

        reservation = Reservation.create_new_reservation(start_date, duration, listing, renter)

        serialized = reservation.serialize()

        return jsonify(reservation=serialized), 201

    abort(401)


@reservations_routes.get("/")
def list_all_reservations():
    """Return all reservations in system.

    Returns JSON like: {reservations: {reservation_uid, listing_uid, owner_uid, renter_uid, reservation_date_created,
    start_date, end_date, status, rental_period, total }, ...}
    """
    reservations = Reservation.query.all()

    serialized = [reservation.serialize() for reservation in reservations]
    return jsonify(reservations=serialized)


@reservations_routes.get("/<int:listing_uid>/upcoming")
@jwt_required()
def get_all_upcoming_reservations_for_listing(listing_uid):
    """ Gets all upcoming reservations associated with listing_uid

    Returns JSON like:
        {reservations: {reservation_uid, listing_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    current_user_id = get_jwt_identity()

    listing = Listing.query.get_or_404(listing_uid)
    if listing.owner.id == current_user_id:
        reservations = list(filter(lambda r: r.start_date > datetime.now(), listing.reservations))

        # reservations = listing.reservations.filter(Reservation.start_date > datetime.now())

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return jsonify(reservations=serialized_reservations)

    abort(401)


@reservations_routes.get("/<int:listing_uid>/past")
@jwt_required()
def get_all_past_reservations_for_listing(listing_uid):
    """ Gets all past reservations associated with listing_uid

    Returns JSON like:
        {reservations: {reservation_uid, listing_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    current_user_id = get_jwt_identity()

    listing = Listing.query.get_or_404(listing_uid)
    if listing.owner.id == current_user_id:
        reservations = list(filter(lambda r: r.start_date < datetime.now(), listing.reservations))

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return jsonify(reservations=serialized_reservations)

    abort(401)


@reservations_routes.get("/user/<int:user_uid>")
@jwt_required()
def get_booked_reservations_for_user_uid(user_uid):
    """ Gets all reservations created by a user_uid

    Returns JSON like:
        {reservations: {reservation_uid, listing_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    # TODO: NOT SURE IF THIS ROUTE IS NECESSARY. MIGHT BE AN ADMIN ROUTE. WILL NOT DO TESTING FOR IT YET.

    current_user_id = get_jwt_identity()

    user = User.query.get_or_404(user_uid)

    if user.id == current_user_id:
        reservations = (Reservation.query
                        .filter(owner_id=current_user_id)
                        .order_by(Reservation.start_date.desc()))

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return jsonify(reservations=serialized_reservations)

    abort(401)


@reservations_routes.get("/<int:reservation_id>")
@jwt_required()
@is_listing_owner_or_is_reservation_booker_or_is_admin
def get_reservation(reservation_id):
    """ Gets specific reservation """

    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation:
        serialized_reservation = reservation.serialize()

        return jsonify(reservation=serialized_reservation), 200

    abort(401)


@reservations_routes.patch("/<int:reservation_id>")
@jwt_required()
@is_reservation_booker
def update_reservation(reservation_id):
    """ Updates specific reservation Returns JSON like: {reservation: {reservation_uid, listing_uid, owner_uid,
    renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }}"""

    reservation = Reservation.query.get_or_404(reservation_id)
    is_in_future = reservation_is_in_future(reservation)

    if is_in_future:
        data = request.form
        start_date_in = data.get('start_date')
        duration_in = data.get('duration')

        start_date = datetime.strptime(start_date_in, '%Y-%m-%d')
        int_duration = int(duration_in)
        duration = timedelta(days=int(duration_in))

        reservation = Reservation.attempt_reservation_update(reservation, start_date, duration)

        return jsonify(reservation=reservation.serialize()), 201

    abort(401)


@reservations_routes.patch("/<int:reservation_id>/cancel")
@jwt_required()
@is_reservation_booker
def cancel_reservation_request(reservation_id):
    """ Cancels specific reservation
    Returns JSON like: {reservation: {reservation_uid, listing_uid, owner_uid,"""

    current_user_id = get_jwt_identity()
    reservation = Reservation.query.get_or_404(reservation_id)
    is_in_future = reservation_is_in_future(reservation)
    data = request.form
    cancellation_reason = data.get('cancellation_reason')
    reservation_status = reservation.status
    # TODO: CHECK USERS' CANCELLATION POLICY

    if (reservation_status == ReservationStatusEnum.PENDING) and is_in_future:
        reservation = attempt_to_cancel_reservation(reservation, cancellation_reason)

        return jsonify(reservation=reservation.serialize()), 201

    abort(401)


@reservations_routes.patch("/<int:reservation_id>/accept")
@jwt_required()
@is_reservation_listing_owner
def accept_reservation(reservation_id):
    """ Accepts specific reservation Returns JSON like: {reservation: {reservation_uid, listing_uid, owner_uid,
    renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }}"""

    reservation = Reservation.query.get_or_404(reservation_id)
    is_in_future = reservation_is_in_future(reservation)

    if (reservation.status == ReservationStatusEnum.PENDING) and is_in_future:
        reservation = attempt_to_accept_reservation_request(reservation)

        return jsonify(reservation=reservation.serialize()), 201

    abort(401)


@reservations_routes.patch("/<int:reservation_id>/decline")
@jwt_required()
@is_reservation_listing_owner
def decline_reservation(reservation_id):
    """ Declines specific reservation Returns JSON like: {reservation: {reservation_uid, listing_uid, owner_uid,
    renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }}"""

    reservation = Reservation.query.get_or_404(reservation_id)
    is_in_future = reservation_is_in_future(reservation)

    if (reservation.status == ReservationStatusEnum.PENDING) and is_in_future:
        reservation = attempt_to_decline_reservation_request(reservation)

        return jsonify(reservation=reservation.serialize()), 201

    abort(401)

# endregion
