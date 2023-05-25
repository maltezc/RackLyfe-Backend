"""Routes for listing images blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from mnb_backend.database import db

from mnb_backend.api_helpers import upload_to_aws
from mnb_backend.listing_images.models import ListingImage
from mnb_backend.listings.models import Listing

listing_images_routes = Blueprint('listing_images_routes', __name__)


@listing_images_routes.post("/api/listings/<int:listing_uid>/images")
@jwt_required()
def add_listing_image(listing_uid):
    """Add listing image, and return data about listing image.

    Returns JSON like:
        {listing_image: {id, listing_owner, image_url }}
    """
    # TODO: if we get an array of files, then we could do a list comprehension where
    # we use the helper function and add that to the table for each one in the comprehension

    current_user = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_uid)
    if current_user == listing.owner_username:
        file = request.files['file']
        url = upload_to_aws(file)  # TODO: refactor to account for [orig_size_img, small_size_img]

        listing_image = ListingImage(
            listing_owner=current_user,
            image_url=url
        )

        db.session.add(listing_image)
        db.session.commit()

        return jsonify(listing_image=listing_image.serialize()), 201

    return jsonify({"error": "not authorized"}), 401

# TODO: MAKE DELETE ROUTE FOR Listing IMAGE
