
from geopy.geocoders import Nominatim

from sqlalchemy import func

from mnb_backend.addresses.models import Address, City, State, ZipCode, Location
from mnb_backend.listings.models import Listing
from mnb_backend.users.models import User


# region User Queries
def get_all_users_in_city(city):
    """ Gets all users of a city"""

    users = User.query \
        .join(Address) \
        .join(City) \
        .filter(City.city_name == city) \
        .all()
    return users


def get_all_users_in_state(state):
    """ Gets all users of a city"""

    users = User.query \
        .join(Address) \
        .join(City) \
        .join(State) \
        .filter(State.state_abbreviation == state) \
        .all()
    return users


def get_all_users_in_zipcode(zipcode):
    """ Gets all users of a city"""

    users = User.query \
        .join(Address) \
        .join(City) \
        .join(ZipCode) \
        .filter(ZipCode.code == zipcode) \
        .all()
    return users


# endregion


# region Book Queries by geography
def get_all_books_in_city(city):
    """ Gets all books of a city"""

    books = Listing.query \
        .join(User) \
        .join(Address) \
        .join(City) \
        .filter(City.city_name == city) \
        .all()
    return books


def get_all_books_in_state(state):
    """ Gets all books of a city"""

    books = Listing.query \
        .join(User) \
        .join(Address) \
        .join(City) \
        .join(State) \
        .filter(State.state_abbreviation == state) \
        .all()
    return books


def get_all_books_in_zipcode(code):
    """ Gets all books of a Zipcode"""

    books = Listing.query \
        .join(User) \
        .join(Address) \
        .join(ZipCode) \
        .filter(ZipCode.code == code) \
        .all()
    return books


def basic_book_search(logged_in_user_uid, book_title, book_author, city, state, zipcode):
    """ Performs basic searches based off the information provided """

    books = Listing.query
    if logged_in_user_uid is not None:
        books = books.join(User).filter(User.id != logged_in_user_uid)
    if book_title is not None:
        books = books.filter(Listing.title.ilike(f"%{book_title}%"))
    if book_author is not None:
        books = books.filter(Listing.author.ilike(f"%{book_author}%"))
    if city is not None or state is not None or zipcode is not None:
        books = books.join(Address)
        if zipcode is not None:
            books = books.join(ZipCode).filter(ZipCode.code.ilike(f"%{zipcode}%"))
        if city is not None:
            books = books.join(City).filter(City.city_name.ilike(f"%{city}%"))
        if city is not None and state is not None:
            books = books.join(State).filter(State.state_abbreviation == state)
        elif state is not None:
            books = books.join(City).join(State).filter(State.state_abbreviation == state)

    return books.all()


# endregion

# def search_other_points_nearby():
#     LatLong.query.filter(func.ST_Distance_Sphere(LatLong.latlong, point) <= radius_m).all()


def books_within_radius(latitude, longitude, radius, logged_in_user_uid, book_title, book_author):
    """ Returns books within a specified radius"""

    # convert radius to meters
    radius_m = int(radius) * 1000

    # create a point from the latitude and longitude values
    point = f"POINT({longitude} {latitude})"

    books = Listing.query

    if logged_in_user_uid is not None:
        books = books.join(User).filter(User.id != logged_in_user_uid)
    if book_title is not None:
        books = books.filter(Listing.title.ilike(f"%{book_title}%"))
    if book_author is not None:
        books = books.filter(Listing.author.ilike(f"%{book_author}%"))

    books_nearby = books.join(Address).join(Location).filter(
        func.ST_DistanceSphere(Location.point, point) <= radius_m)

    return books_nearby.all()


def locations_within_radius(latitude, longitude, radius):
    """ Function for searching nearby points """

    # convert radius to meters
    radius_m = int(radius) * 1000

    # create a point from the latitude and longitude values
    point = f"POINT({longitude} {latitude})"

    # query the database to find locations within the specified radius
    locations = Location.query.filter(
        func.ST_DistanceSphere(Location.point, point) <= radius_m)

    return locations.all()


def geocode_address(address):
    """ Geocode address and return lat/long. """

    geolocator = Nominatim(user_agent="mnb")
    location = geolocator.geocode(address)

    return location.latitude, location.longitude
