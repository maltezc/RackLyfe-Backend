from models import db, connect_db, User, Address, City, State, ZipCode, Message, Book, Reservation, BookImage


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

    books = Book.query \
        .join(User) \
        .join(Address) \
        .join(City) \
        .filter(City.city_name == city) \
        .all()
    return books


# def get_all_users_in_state(state):
#     """ Gets all users of a city"""
#
#     users = User.query \
#         .join(Address) \
#         .join(City) \
#         .join(State) \
#         .filter(State.state_abbreviation == state) \
#         .all()
#     return users
#
#
# def get_all_users_in_zipcode(zipcode):
#     """ Gets all users of a city"""
#
#     users = User.query \
#         .join(Address) \
#         .join(City) \
#         .join(ZipCode) \
#         .filter(ZipCode.code == zipcode) \
#         .all()
#     return users
# endregion
