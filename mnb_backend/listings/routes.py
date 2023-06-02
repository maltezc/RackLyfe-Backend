"""Routes for listings blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from mnb_backend.database import db
from mnb_backend.api_helpers import db_post_listing, aws_upload_image, db_add_listing_image
from mnb_backend.listings.models import Listing

listings_routes = Blueprint('listings_routes', __name__)


@listings_routes.post("/api/listings")
@jwt_required()
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
            author = request.form.get("author")
            isbn = int(request.form.get("isbn"))
            condition = request.form.get("condition")
            rate_price = int(request.form.get("rate_price"))
            rate_schedule = request.form.get("rate_schedule")

            # post listing to db
            listing_posted = db_post_listing(current_user_id, title, author, isbn, condition, rate_price, rate_schedule)

            images_posted = []
            # post image to aws

            for image in images:
                image_url = aws_upload_image(images[image])
                # post image to database
                image_element = db_add_listing_image(current_user_id, listing_posted.id, image_url)
                images_posted.append(image_element.serialize())

            # TODO: might have to set primary listing image here but then its pinging the db twice for the patch request

            return jsonify(listing=listing_posted.serialize(), images_posted=images_posted), 201

        except Exception as error:
            print("Error", error)
            return jsonify({"error": f"Failed to add listing and listing image: {error}", }), 401


@listings_routes.patch('/api/listings/<int:listing_uid>')
@jwt_required()
def update_listing(listing_uid):
    """ Update listing information

    Returns JSON like:
        {listing: {listing_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of listing
    """

    current_user = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_uid)
    print("listing owner", listing.owner_username)
    if current_user == listing.owner_username:
        data = request.json

        listing.orig_image_url = data['orig_image_url'],
        listing.small_image_url = data['small_image_url'],
        listing.title = data['title'],
        listing.author = data['author'],
        listing.isbn = data['isbn'],
        listing.genre = data['genre'],
        listing.condition = data['condition'],
        listing.price = data['price'],

        db.session.add(listing)
        db.session.commit()

        return jsonify(listing=listing.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@listings_routes.patch('/api/users/<int:user_uid>/listings/<int:listing_uid>/toggle_status')
@jwt_required()
def toggle_listing_status(user_uid, listing_uid):
    """ Toggles listing availability status. """

    current_user = get_jwt_identity()

    if current_user == user_uid:
        listing = Listing.query.get_or_404(listing_uid)

        if listing.status == "Available":
            listing.status = "Checked Out"
        else:
            listing.status = "Available"

        db.session.add(listing)
        db.session.commit()

        return jsonify(listing=listing.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@listings_routes.delete('/api/listings/<int:listing_uid>')
@jwt_required()
def delete_listing(listing_uid):
    """ update listing information

    Returns JSON like:
    {listing: {listing_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of listing
    """

    current_user = get_jwt_identity()
    listing = Listing.query.get_or_404(listing_uid)
    if current_user == listing.owner_id:
        db.session.delete(listing)
        db.session.commit()

        return jsonify("Listing successfully deleted"), 200

    return jsonify({"error": "not authorized"}), 401
