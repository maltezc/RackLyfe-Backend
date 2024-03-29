"""Routes for listings blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import abort

from mnb_backend.database import db
from mnb_backend.decorators import user_address_required
from mnb_backend.enums import ListingStatusEnum
from mnb_backend.listings.helpers import get_mount_type_enum, get_activity_type_enum
from mnb_backend.listings.models import Listing
from mnb_backend.users.models import User

listings_routes = Blueprint('listings_routes', __name__)


@listings_routes.post("/")
@jwt_required()
@user_address_required
def create_listing():
    """Add listing, and return data about new listing.

    Returns JSON like:
        {listing: {listing_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}
    """
    # TODO: try posting a listing object to the db first. if successful, post listing image to aws, if successful,
    #  switch url for listing from dummy_url to aws_url. if anything fails delete the listing and the listing image.
    # https://www.geeksforgeeks.org/try-except-else-and-finally-in-python/

    print("I'm in api/listings")
    current_user_id = get_jwt_identity()
    if current_user_id:
        try:
            images = request.files
            title = request.form.get("title")
            activity_type = request.form.get("activity_type")
            rack_mount_type = request.form.get("mount_type")
            rate_price = int(request.form.get("rate_price"))

            current_user = User.query.get_or_404(current_user_id)

            listing = Listing.create_listing(
                owner=current_user,
                title=title,
                activity_type=activity_type,
                mount_type=rack_mount_type,
                rate_price=rate_price,
                images=images,
            )

            # TODO: might have to set primary listing image here but then its pinging the db twice for the patch request
            serialized = listing.serialize()

            return jsonify(listing=serialized), 201
            # return jsonify(listing=listing_posted.serialize(), images_posted=images_posted), 201

        except Exception as error:
            abort(500, description="Failed to create listing.")


@listings_routes.get('/current')
@jwt_required()
def get_listings_of_current_user():
    """Show books of specified user.

    Returns JSON like:
        {books: {book_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)

    listings = current_user.listings
    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)


# TODO: GET SPECIFIC LISTING
@listings_routes.get('/<int:listing_id>')
def get_specific_listing(listing_id):
    """Return information on a specific book.

    Returns JSON like:
        {book: {book_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """
    listing = Listing.query.get_or_404(listing_id)
    serialized = listing.serialize()

    return jsonify(listing=serialized)


@listings_routes.get("/user/<int:user_id>")
def get_listings_of_specific_user(user_id):
    """
    Gets listings of current user
    """

    user = User.query.get_or_404(user_id)

    listings = user.listings
    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)


@listings_routes.patch('/<int:listing_uid>')
@jwt_required()
def update_listing(listing_uid):
    """ Update listing information

    Returns JSON like:
        {listing: {listing_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of listing
    """

    current_user_id = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_uid)

    if current_user_id == listing.owner_id:
        data = request.json

        mount_type_value = listing.mount_type
        if "mount_type" in data:
            updated_mount_type = data['mount_type']
            mount_type_value = get_mount_type_enum(updated_mount_type)

        activity_type_value = listing.activity_type
        if "activity_type" in data:
            updated_activity_type = data['activity_type']
            activity_type_value = get_activity_type_enum(updated_activity_type)

        # Update the listing attributes
        listing.title = data.get('title', listing.title),
        listing.mount_type = mount_type_value
        listing.activity_type = activity_type_value
        listing.rate_price = data.get('rate_price', listing.rate_price)

        db.session.add(listing)
        db.session.commit()

        return jsonify(listing=listing.serialize()), 200

    abort(401, "Not authorized")


@listings_routes.patch('/toggle_status/<int:listing_uid>')
@jwt_required()
def toggle_listing_status(listing_uid):
    """ Toggles listing availability status. """

    current_user_id = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_uid)

    if current_user_id == listing.owner_id:

        if listing.status == ListingStatusEnum.AVAILABLE:
            listing.status = ListingStatusEnum.UNAVAILABLE
        else:
            listing.status = ListingStatusEnum.AVAILABLE

        db.session.add(listing)
        db.session.commit()

        return jsonify(listing=listing.serialize()), 200

    abort(401, "Not authorized")


@listings_routes.delete('/<int:listing_uid>')
@jwt_required()
def delete_listing(listing_uid):
    """ update listing information

    Returns JSON like:
    {listing: {listing_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of listing
    """

    current_user_id = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_uid)
    if current_user_id == listing.owner_id:
        db.session.delete(listing)
        db.session.commit()

        return jsonify("Listing successfully deleted"), 200

    abort(401, "Not authorized")
