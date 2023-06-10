"""Routes for listing_helpers blueprint. UNSURE IF THESE ROUTES ARE NECESSARY"""
from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required, get_jwt_identity
from mnb_backend.util_filters import get_all_listings_in_city, get_all_listings_in_state, get_all_books_in_zipcode

from mnb_backend.database import db
from mnb_backend.api_helpers import aws_upload_image, db_add_listing_image
from mnb_backend.decorators import user_address_required
from mnb_backend.listings.models import Listing
from mnb_backend.listings.helpers import db_post_listing
from mnb_backend.users.models import User

listings_helper_routes = Blueprint('listing_helper_routes', __name__)


# region BOOKS ENDPOINTS START


@listings_helper_routes.get("/api/books")
def list_all_books():
    """Return all books in system.

    Returns JSON like:
       {books: {book_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """
    books = Listing.query.all()

    serialized = [book.serialize() for book in books]
    return jsonify(pools=serialized)


@listings_helper_routes.get('/api/search/books/city')
def show_books_by_city():
    """Return books in a specific city.

    Returns JSON like:
        {books: {book_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    city = request.args.get('city')  # mandatory

    books = get_all_listings_in_city(city)

    serialized = [book.serialize() for book in books]
    return jsonify(books=serialized)


@listings_helper_routes.get('/api/search/books/state')
def show_books_by_state():
    """Return books in a specific state.

    Returns JSON like:
        {books: {book_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    state = request.args.get('state')  # mandatory

    books = get_all_listings_in_state(state)

    serialized = [book.serialize() for book in books]
    return jsonify(books=serialized)


@listings_helper_routes.get('/api/search/books/zipcode')
def search_books_by_zipcode():
    """Return books in a specific zipcode.

    Returns JSON like:
        {books: {book_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    zipcode = request.args.get('zipcode')  # mandatory

    books = get_all_books_in_zipcode(zipcode)

    serialized = [book.serialize() for book in books]
    return jsonify(books=serialized)
