from flask import abort, jsonify
from flask_jwt_extended import get_jwt_identity
from functools import wraps

from mnb_backend.messages.models import Message
from mnb_backend.reservations.models import Reservation
from mnb_backend.users.models import User
from mnb_backend.database import db


def user_address_required(f):
    """
    Decorator to ensure user has address"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user has address"""

        current_user_id = get_jwt_identity()

        user = db.session.get(User, current_user_id)
        if not user:
            abort(400)
        if not user.address:
            abort(401, description="Not authorized. Address required.")
            # return jsonify({"error": "Not authorized. Address required."}), 403
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to ensure user is admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is admin"""

        current_user_id = get_jwt_identity()

        user = db.session.get(User, current_user_id)
        if not user:
            abort(400)
        if not user.is_admin:
            abort(403, description="Not authorized. Admin required.")
        return f(*args, **kwargs)

    return decorated_function


def is_listing_owner_or_is_reservation_booker_or_is_admin(func):
    """
    Decorator to ensure user is listing owner or reservation booker"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on listing"""
        reservation_id = kwargs.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if reservation.renter_id == user.id or reservation.listing.owner_id == user.id or user.is_admin:
            return func(*args, **kwargs)

        abort(401)

    return decorated_function


def is_reservation_booker(func):
    """
    Decorator to ensure user is authorized to perform action on listing"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on listing"""
        reservation_id = kwargs.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if reservation.renter_id == user.id:
            return func(*args, **kwargs)

        abort(401, description="Not authorized")

    return decorated_function


def is_reservation_listing_owner(func):
    """
    Decorator to ensure user is authorized to perform action on listing"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on listing"""
        reservation_id = kwargs.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if reservation.listing.owner.id == user.id:
            return func(*args, **kwargs)

        abort(401, description="Not authorized")

    return decorated_function


def is_message_sender_receiver_or_admin(func):
    """
    Decorator to ensure user is authorized to perform action on listing"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on listing"""
        message_id = kwargs.get('message_id')
        message = Message.query.get_or_404(message_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if message.sender_id == user.id or message.reciever_id == user.id or user.is_admin:
            return func(*args, **kwargs)

        abort(401, description="Not authorized")

    return decorated_function
