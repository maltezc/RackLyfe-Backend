
from flask import abort, jsonify
from flask_jwt_extended import get_jwt_identity
from functools import wraps

from mnb_backend.messages.models import Message
from mnb_backend.reservations.models import Reservation
from mnb_backend.users.models import User


def admin_required(f):
    """
    Decorator to ensure user is admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is admin"""

        current_user_id = get_jwt_identity()

        # user_id = g.user_id  # assuming g.user_id is the user ID of the logged-in user
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            abort(403)  # raise a 403 Forbidden error if the user is not an admin
        return f(*args, **kwargs)

    return decorated_function


def is_book_owner_or_is_reservation_booker_or_is_admin(func):
    """
    Decorator to ensure user is book owner or reservation booker"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on book"""
        reservation_id = kwargs.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if reservation.renter_id == user.id or reservation.book.owner_id == user.id or user.is_admin:
            return func(*args, **kwargs)

        return jsonify({"error": "Not authorized"}), 401

    return decorated_function


def is_reservation_booker(func):
    """
    Decorator to ensure user is authorized to perform action on book"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on book"""
        reservation_id = kwargs.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if reservation.renter_id == user.id:
            return func(*args, **kwargs)

        return jsonify({"error": "Not authorized"}), 401

    return decorated_function


def is_reservation_listing_owner(func):
    """
    Decorator to ensure user is authorized to perform action on book"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on book"""
        reservation_id = kwargs.get('reservation_id')
        reservation = Reservation.query.get_or_404(reservation_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if reservation.book.owner.id == user.id:
            return func(*args, **kwargs)

        return jsonify({"error": "Not authorized"}), 401

    return decorated_function


def is_message_sender_reciever_or_admin(func):
    """
    Decorator to ensure user is authorized to perform action on book"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function to ensure user is authorized to perform action on book"""
        message_id = kwargs.get('message_id')
        message = Message.query.get_or_404(message_id)

        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        if message.sender_id == user.id or message.reciever_id == user.id or user.is_admin:
            return func(*args, **kwargs)

        return jsonify({"error": "Not authorized"}), 401

    return decorated_function
