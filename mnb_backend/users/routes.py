"""Routes for users blueprint."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy.exc import IntegrityError

from mnb_backend.api_helpers import upload_to_aws
from mnb_backend.database import db
from mnb_backend.decorators import admin_required
from mnb_backend.enums import UserStatusEnums
from mnb_backend.user_images.models import UserImage
from mnb_backend.users.models import User
from mnb_backend.auth.auth_helpers import is_valid_name, is_valid_email

root_views = Blueprint('user_views', __name__)

user_routes = Blueprint('user_routes', __name__)


# region USERS List ENDPOINTS START

@user_routes.post("/signup")
def create_user():
    """Add user, and return data about new user.
    Returns JSON like:
        {token: token, user: {user_uid, email, image_url, firstname, lastname, address, is_admin, preferred_trade_location}}"""

    # profile_image = request.form.get('profile_image')
    data = request.json
    email = data.get('email')

    # check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already taken"}), 400

    try:
        user = User.signup(
            email=data.get('email'),
            status=UserStatusEnums.ACTIVE,
            password=data.get('password'),
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            about_me=data.get('about_me')
        )

        token = create_access_token(identity=user.id)
        print("jsonify token: ", jsonify(token=token))

        # if profile_image is not None:
        #     url = upload_to_aws(profile_image)  # TODO: refactor to account for [orig_size_img, small_size_img]
        #     # [url] = upload_to_aws(profile_image)  # TODO: refactor to account for [orig_size_img, small_size_img]
        #     user_image = UserImage(
        #         image_url=url,
        #         user_uid=user.id
        #     )
        #     db.session.add(user_image)
        #     db.session.commit()
        #
        #     return jsonify(token=token, user=user.serialize(), user_image=user_image.serialize()), 201

        return jsonify(token=token, user=user.serialize()), 201

    except IntegrityError:
        # if an IntegrityError occurs, it might be due to the email not being unique
        db.session.rollback()
        return jsonify({"error": "Email already taken"}), 400
    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424


@user_routes.post("/signup_admin")
@jwt_required()
@admin_required
def create_admin_user():
    """Add admin user, and return data about new user.
    Returns JSON like:
        {token: token, user: {user_uid, email, image_url, firstname, lastname, address, is_admin, preferred_trade_location}}"""

    try:
        user = User.signup(
            email=request.form.get('email'),
            password=request.form.get('password'),
            firstname=request.form.get('firstname'),
            lastname=request.form.get('lastname'),
            status=UserStatusEnums.ACTIVE,
            is_admin=True,
        )

        token = create_access_token(identity=user.id)

        return jsonify(token=token, user=user.serialize()), 201

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424


@user_routes.get("/")
def list_users():
    """Return all users in system.

    Returns JSON like:
        {users: [{user_uid, email, status, firstname, lastname, image_url,
        location, books, reservations}, ...]}
    """

    users = User.query.all()

    serialized = [user.serialize() for user in users]

    return jsonify(users=serialized)


@user_routes.get('/<int:user_uid>')
def show_user(user_uid):
    """Show user profile.

    Returns JSON like:
        {user: user_uid, email, image_url, firstname, lastname, address, owned_books, reservations}
    """
    user = User.query.get_or_404(user_uid)
    user = user.serialize()

    return jsonify(user=user)


@user_routes.patch('/<int:user_uid>')
@jwt_required()
def update_user(user_uid):
    """ update user information

    Returns JSON like:
        {user: user_uid, email, firstname, lastname, image_url, location, owned_books, reservations}
    """

    # TODO: ADD "CHANGE PASSWORD FEATURE LATER"
    current_user = get_jwt_identity()
    if current_user == user_uid:
        user = User.query.get_or_404(user_uid)
        data = request.json
        firstname = data['firstname']
        lastname = data['lastname']

        if is_valid_name(firstname):
            user.firstname = firstname
        else:
            return jsonify({"error": "invalid firstname"}), 400

        if is_valid_name(lastname):
            user.lastname = lastname
        else:
            return jsonify({"error": "invalid lastname"}), 400

        db.session.add(user)
        db.session.commit()

        return jsonify(user=user.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@user_routes.patch('/<int:user_uid>/toggle_status')
@jwt_required()
def toggle_user_status(user_uid):
    """ Toggles_user's activity_status """

    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    user_to_update = User.query.get(user_uid)

    if user_to_update is None: return jsonify({"error": "User not found"}), 404

    if current_user_id == user_uid or current_user.is_admin:
        user = User.query.get_or_404(user_uid)

        if user.status == UserStatusEnums.ACTIVE:
            user.status = UserStatusEnums.INACTIVE
        else:
            user.status = UserStatusEnums.ACTIVE

        db.session.add(user)
        db.session.commit()

        return jsonify(user=user.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@user_routes.delete('/<int:user_uid>')
@jwt_required()
def delete_user(user_uid):
    """Delete user. """

    # TODO: add admin role to delete users
    current_user_id = get_jwt_identity()
    user_to_delete = User.query.get(user_uid)

    if user_to_delete is None: return jsonify({"error": "User not found"}), 404

    current_user = User.query.get_or_404(current_user_id)
    if current_user_id == user_uid or current_user.is_admin:
        db.session.delete(user_to_delete)
        db.session.commit()

        return jsonify("User successfully deleted"), 200

    return jsonify({"error": "not authorized"}), 401

# endregion
