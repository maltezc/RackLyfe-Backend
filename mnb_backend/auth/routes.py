"""Routes for authentication blueprint."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from sqlalchemy.exc import IntegrityError

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
    email = data.get('email')
    password = data.get('password')

    user = User.authenticate(email, password)
    # TODO: SET UP CATCH FOR USER NOT FOUND
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    token = create_access_token(identity=user.id)

    return jsonify(token=token, user=user.serialize()), 200




# endregion
