"""Routes for searches blueprint."""

from flask import Blueprint, jsonify, request

from mnb_backend.addresses.models import Address, City
from mnb_backend.listings.models import Listing
from mnb_backend.users.models import User
from mnb_backend.util_filters import get_all_books_in_zipcode, get_all_users_in_city, get_all_users_in_state, \
    get_all_users_in_zipcode, get_all_listings_in_city, get_all_listings_in_state, basic_listing_search, books_within_radius, \
    locations_within_radius

searches_routes = Blueprint('searches_routes', __name__)


# region Search Endpoints
@searches_routes.get("/")
def search():
    """ Searches listing properties for matched or similar values.

    Returns JSON like:
        {listings: {listing_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    # query_string = request.query_string

    # endurance
    # 94108

    # logged_in_user_uid, listing_title, listing_author, city, state, zipcode
    title = request.args.get('title')
    author = request.args.get('author')
    isbn = request.args.get('isbn')
    city = request.args.get('city')
    state = request.args.get('state')
    zipcode = request.args.get('zipcode')  # mandatory

    request.args.keys()
    # if len(key) > 0:
    # TODO: Create dynamic filter: if filter is not empty, add filter to ultimate filter
    # https://stackoverflow.com/questions/41305129/sqlalchemy-dynamic-filtering

    # test = Book.query.filter(Book.title.ilike(f"%{title}%") | Book.author.ilike(f"%{author}%") | Book.isbn.ilike(f"%{isbn}%")).all()
    # qs = Book.query.filter(Book.title.ilike(f"%{title}%") | Book.author.ilike(f"%{author}%") | Book.isbn.ilike(f"%{isbn}%")).all()
    # qs = filter book by mandatory field
    # if author is not none, qs = qs.filter(author)

    city_users = get_all_users_in_city("Hercules")
    state_users = get_all_users_in_state("CA")
    zipcode_users = get_all_users_in_zipcode("94547")
    users = User.query.join(Address).join(City).filter(City.city_name == "Hercules").all()
    city_listings = get_all_listings_in_city("Hercules")
    state_listings = get_all_listings_in_state("CA")
    zipcode_listings = get_all_books_in_zipcode("94547")
    all_listings = Listing.query.all()
    searched_listings = basic_listing_search(1, title, author, city, state, zipcode)

    serialized = [listing.serialize() for listing in searched_listings]
    return jsonify(listings=serialized)


@searches_routes.get("/api/search/listings_nearby")
def list_nearby_books():
    """ Shows all books nearby

    Returns JSON like: {books: {book_uid, owner_id, orig_image_url, small_image_url, title, author, isbn, genre,
    condition, price, reservations},...}
    """

    title = request.args.get('title')
    author = request.args.get('author')

    books = books_within_radius(38.006370860286694, -122.28195023589687, 1000, 1, title, author)

    serialized = [book.serialize() for book in books]

    return jsonify(books=serialized)


@searches_routes.get("/api/search/nearby")
def list_nearby():
    """ Shows all points nearby """

    locations = locations_within_radius(38.006370860286694, -122.28195023589687, 1000)

    return locations


# endregion
