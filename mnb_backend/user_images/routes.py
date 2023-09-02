"""User Image Routes"""
from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import abort

from mnb_backend.api_helpers import aws_delete_image, aws_upload_image, db_add_user_image
from mnb_backend.database import db
from mnb_backend.user_images.models import UserImage
from mnb_backend.users.models import User

user_images_routes = Blueprint('user_images_routes', __name__)


# region User Image Endpoints Start

@user_images_routes.post("/")
@jwt_required()
def add_user_image():
    """Add user image, and return data about new user image.
    Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}"""

    current_user_id = get_jwt_identity()
    profile_image = request.files.get("profile_image")
    if profile_image is not None:

        image_url = aws_upload_image(profile_image)
        image_element = db_add_user_image(current_user_id, image_url)
        image = UserImage.query.get_or_404(image_element.id)

        return jsonify(user_image=image.serialize()), 201

    abort(400, description="Image needed for upload")


@user_images_routes.get("/current/")
@jwt_required()
def get_current_user_image():
    """ Handle getting current user image
    Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}"""

    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    user_image = user.profile_image

    return jsonify(user_image=user_image.serialize()), 200


@user_images_routes.patch("/current/")
@jwt_required()
def update_user_image():
    """ Updates image to the currently logged-in user
    Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}"""

    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        user_image = user.profile_image
        # user_image = UserImage.query.get_or_404(user_image_id)

        if user.id == user_image.user.id:
            profile_image = request.files.get("profile_image")

            if user_image is not None:
                aws_delete_image(user_image.image_url)

            if profile_image is not None:
                image_url = aws_upload_image(profile_image)
                user_image.image_url = image_url
                db.session.commit()

                return jsonify(user_image=user_image.serialize()), 200

        abort(401, "Not authorized")

    except Exception as error:
        print("Error", error)
        abort(500, description="Failed to update image")



@user_images_routes.delete("/current/")
@jwt_required()
def delete_user_image():
    """ Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        user_image = user.profile_image

        if user.id == user_image.user.id or user.is_admin:
            aws_delete_image(user_image.image_url)
            db.session.delete(user_image)
            db.session.commit()

            return jsonify(user=user.serialize(), user_profile_image=user.profile_image), 200

        return jsonify({"error": "Failed to delete image"}), 424

    except Exception as error:
        print("Error", error)
        abort(500, description="Failed to delete image")

# endregion
