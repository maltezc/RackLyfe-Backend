"""Routes for listings blueprint."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from mnb_backend.database import db
from mnb_backend.api_helpers import aws_upload_image, db_add_listing_image
from mnb_backend.decorators import user_address_required
from mnb_backend.enums import ListingStatusEnum
from mnb_backend.listings.models import Listing
from mnb_backend.listings.helpers import db_post_listing
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
            author = request.form.get("author")
            isbn = int(request.form.get("isbn"))
            condition = request.form.get("condition")
            rate_price = int(request.form.get("rate_price"))
            rate_schedule = request.form.get("rate_schedule")

            curren_user = User.query.get_or_404(current_user_id)

            listing = Listing.create_listing(
                owner=curren_user,
                title=title,
                author=author,
                isbn=isbn,
                genre="",
                status=ListingStatusEnum.AVAILABLE,
                # condition=condition,
                rate_price=rate_price,
                rate_schedule=rate_schedule,
                images=images,
            )

            # post listing to db
            # listing_posted = db_post_listing(current_user_id, title, author, isbn, condition, rate_price, rate_schedule)
            #
            # images_posted = []
            # # post image to aws
            #
            # for image in images:
            #     image_url = aws_upload_image(images[image])
            #     # post image to database
            #     image_element = db_add_listing_image(current_user_id, listing_posted.id, image_url)
            #     images_posted.append(image_element.serialize())

            # TODO: might have to set primary listing image here but then its pinging the db twice for the patch request

            return jsonify(listing=listing.serialize()), 201
            # return jsonify(listing=listing_posted.serialize(), images_posted=images_posted), 201

        except Exception as error:
            print("Error", error)
            return jsonify({"error": f"Failed to add listing and listing image: {error}", }), 401


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

        # Update the listing attributes
        listing.title = data.get('title', listing.title),
        listing.author = data.get('author', listing.author),
        listing.isbn = data.get('isbn', listing.isbn),
        listing.genre = data.get('genre', listing.genre),
        # listing.condition = data.get('condition', listing.condition),
        # listing.rate_price = data.get('rate_price', listing.rate_price.value),

        db.session.add(listing)
        db.session.commit()

        return jsonify(listing=listing.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


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

    return jsonify({"error": "not authorized"}), 401


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

    return jsonify({"error": "not authorized"}), 401
