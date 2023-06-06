"""Routes for authentication blueprint."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required

from mnb_backend.database import db
from mnb_backend.decorators import admin_required
from mnb_backend.enums import UserStatusEnums

from mnb_backend.api_helpers import upload_to_aws
from mnb_backend.user_images.models import UserImage
from mnb_backend.users.models import User

auth_routes = Blueprint('auth_routes', __name__)


# region AUTH ENDPOINTS START

@auth_routes.route("/login", methods=["POST"])
def login():
    """Handle user login.
    Returns JSON like:
        {token: token, user: {user_uid, email, image_url, firstname, lastname, address, is_admin, preferred_trade_location}}"""

    data = request.json
    email = data['email']
    password = data['password']

    user = User.authenticate(email, password)
    token = create_access_token(identity=user.id)

    return jsonify(token=token, user=user.serialize()), 200


@auth_routes.post("/signup_admin")
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
            is_admin=request.form.get('is_admin'),
        )

        token = create_access_token(identity=user.id)

        return jsonify(token=token, user=user.serialize()), 201

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424


@auth_routes.post("/signup")
def create_user():
    """Add user, and return data about new user.
    Returns JSON like:
        {token: token, user: {user_uid, email, image_url, firstname, lastname, address, is_admin, preferred_trade_location}}"""

    profile_image = request.form.get('profile_image')

    try:
        user = User.signup(
            email=request.form.get('email'),
            status=UserStatusEnums.ACTIVE,
            password=request.form.get('password'),
            firstname=request.form.get('firstname'),
            lastname=request.form.get('lastname'),
        )

        token = create_access_token(identity=user.id)
        print("jsonify token: ", jsonify(token=token))

        if profile_image is not None:
            [url] = upload_to_aws(profile_image)  # TODO: refactor to account for [orig_size_img, small_size_img]
            user_image = UserImage(
                image_url=url,
                user_uid=user.id
            )
            db.session.add(user_image)
            db.session.commit()

            return jsonify(token=token, user=user.serialize(), user_image=user_image.serialize()), 201

        return jsonify(token=token, user=user.serialize()), 201

    # todo: refactor to only have try/execpt around databse edits.
    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424

# endregion
