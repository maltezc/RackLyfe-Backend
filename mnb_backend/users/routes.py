"""Routes for users blueprint."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from mnb_backend.database import db
from mnb_backend.users.models import User

root_views = Blueprint('user_views', __name__)

user_routes = Blueprint('user_routes', __name__)


# region USERS List ENDPOINTS START

@user_routes.get("/api/users")
def list_users():
    """Return all users in system.

    Returns JSON like:
        {users: [{user_uid, email, status, firstname, lastname, image_url,
        location, books, reservations}, ...]}
    """

    users = User.query.all()

    serialized = [user.serialize() for user in users]

    return jsonify(users=serialized)


@user_routes.get('/api/users/<int:user_uid>')
def show_user(user_uid):
    """Show user profile.

    Returns JSON like:
        {user: user_uid, email, image_url, firstname, lastname, address, owned_books, reservations}
    """
    user = User.query.get_or_404(user_uid)
    user = user.serialize()

    return jsonify(user=user)


@user_routes.patch('/api/users/<int:user_uid>')
@jwt_required()
def update_user(user_uid):
    """ update user information

    Returns JSON like:
        {user: user_uid, email, firstname, lastname, image_url, location, owned_books, reservations}
    """

    current_user = get_jwt_identity()
    if current_user == user_uid:
        user = User.query.get_or_404(user_uid)
        data = request.json
        # TODO: ADD "CHANGE PASSWORD FEATURE LATER"
        user.email = data['email'],
        user.location = data['location'],

        db.session.add(user)
        db.session.commit()

        return jsonify(user=user.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@user_routes.patch('/api/users/<int:user_uid>/toggle_status')
@jwt_required()
def toggle_user_status(user_uid):
    """ Toggles_user's activity_status """

    current_user = get_jwt_identity()
    if current_user == user_uid:
        user = User.query.get_or_404(user_uid)

        if user.status == "Active":
            user.status = "Deactivated"
        else:
            user.status = "Active"

        db.session.add(user)
        db.session.commit()

        return jsonify(user=user.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@user_routes.delete('/api/users/delete/<int:user_uid>')
@jwt_required()
def delete_user(user_uid):
    """Delete user. """

    # TODO: add admin role to delete users
    current_user = get_jwt_identity()
    if current_user == user_uid or current_user.is_admin:
        user = User.query.get_or_404(user_uid)

        db.session.delete(user)
        db.session.commit()

        return jsonify("User successfully deleted", 200)
    return jsonify({"error": "not authorized"}), 401

# endregion
