"""Routes for listing images blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.exceptions import abort

from mnb_backend.database import db

from mnb_backend.api_helpers import aws_upload_image
from mnb_backend.listing_images.models import ListingImage
from mnb_backend.listings.models import Listing
from mnb_backend.users.models import User

listing_images_routes = Blueprint('listing_images_routes', __name__)




@listing_images_routes.post("/listing/<int:listing_uid>")
@jwt_required()
def add_listing_image(listing_uid):
    """Add listing image, and return data about listing image.

    Returns JSON like:
        {listing_image: {id, listing_owner, image_url }}
    """
    # TODO: if we get an array of files, then we could do a list comprehension where
    # we use the helper function and add that to the table for each one in the comprehension

    current_user_id = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_uid)

    if current_user_id == listing.owner.id:
        files = request.files

        errors = []
        files_uploaded = []

        if len(files) == 0:
            # if len(files.items()) is 0:
            abort(400, "Image required")
        for title, file in files.items():
            if file.content_type == "image/jpeg":
                url = aws_upload_image(file)
                # url = upload_to_aws(file)

                listing_image = ListingImage.create_listing_image(
                    listing_id=listing_uid,
                    image_url=url
                )

                db.session.add(listing_image)
                db.session.commit()

                files_uploaded.append(listing_image.serialize())

            else:
                errors.append({f"{file.filename}": file.content_type})

            if len(files_uploaded) == 0 and len(errors) > 0:
                abort(400, "No files were uploaded because filetype was incorrect.")

        return jsonify(uploaded_results=files_uploaded, errors=errors), 201
    abort(401, "Not authorized")


@listing_images_routes.get("/")
def get_all_listing_images():
    """gets all listing images

    Returns JSON like:
        {listing_images: [{id, listing_owner, image_url }...]}
    """

    listing_images = ListingImage.query.all()
    serialized = [listing_image.serialize() for listing_image in listing_images]

    return jsonify(listing_images=serialized)


@listing_images_routes.get("/<int:listing_image_id>")
def get_listing_image(listing_image_id):
    """gets listing image

    Returns JSON like:
        {listing_image: {id, listing_owner, image_url }}
    """


    listing_image = db.session.get(ListingImage, listing_image_id)
    if listing_image:
        serialized = listing_image.serialize()
        return jsonify(listing_image=serialized)

    abort(404)


@listing_images_routes.delete("/<int:listing_image_id>")
@jwt_required()
def delete_listing_image(listing_image_id):
    """delete listing image"""

    current_user_id = get_jwt_identity()
    listing_image = db.session.get(ListingImage, listing_image_id)
    if not listing_image:
        abort(404)

    user = User.query.get_or_404(current_user_id)
    is_admin = user.is_admin

    if current_user_id == listing_image.listing.owner.id or is_admin is True:
        db.session.delete(listing_image)
        db.session.commit()

        return jsonify("Listing Image successfully deleted"), 200

    abort(401)
