from datetime import datetime
from collections import defaultdict

import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from address_helpers import set_retrieve_address
from api_helpers import upload_to_aws, db_post_book, aws_upload_image, db_add_book_image, db_add_user_image, \
    aws_delete_image
from reservation_helpers import create_new_reservation, attempt_reservation_update, reservation_is_in_future, \
    attempt_to_accept_reservation_request, attempt_to_decline_reservation_request, attempt_to_cancel_reservation
from decorators import admin_required, is_reservation_booker, is_reservation_listing_owner, \
    is_book_owner_or_is_reservation_booker_or_is_admin, is_message_sender_reciever_or_admin
from models import db, connect_db, User, Address, City, Message, Book, Reservation, BookImage, \
    UserImage
from util_filters import get_all_users_in_city, get_all_users_in_state, get_all_users_in_zipcode, get_all_books_in_city, \
    get_all_books_in_state, get_all_books_in_zipcode, basic_book_search, locations_within_radius, books_within_radius
from enums import UserStatusEnums, PriceEnums, ReservationStatusEnum, BookStatusEnum, RentalDurationEnum, \
    BookConditionEnum

load_dotenv()

app = Flask(__name__)
CORS(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# Setting up jwt
app.config["JWT_SECRET_KEY"] = os.environ['SECRET_KEY']
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_IDENTITY_CLAIM"] = "user_uid"
# app.config["JWT_IDENTITY_CLAIM"] = "username"


connect_db(app)
db.create_all()


# region AUTH ENDPOINTS START

@app.route("/api/auth/login", methods=["POST"])
def login():
    """ Login user, returns JWT if authenticated """

    data = request.json
    email = data['email']
    password = data['password']

    user = User.authenticate(email, password)
    token = create_access_token(identity=user.id)

    return jsonify(token=token)


@app.post("/api/auth/signup_admin")
@jwt_required()
@admin_required
def create_admin_user():
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {user_uid, email, image_url, firstname, lastname, address, is_admin, preferred_trade_location}}
    """

    try:
        user = User.signup(
            email=request.form.get('email'),
            password=request.form.get('password'),
            firstname=request.form.get('firstname'),
            lastname=request.form.get('lastname'),
            is_admin=request.form.get('is_admin'),
        )

        token = create_access_token(identity=user.id)

        return jsonify(token=token, user=user.serialize()), 201

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424


@app.post("/api/auth/signup")
def create_user():
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {user_uid, email, image_url, firstname, lastname, address, preferred_trade_location}}
    """

    try:
        profile_image = request.form.get('profile_image')

        user = User.signup(
            email=request.form.get('email'),
            status=UserStatusEnums.ACTIVE,
            password=request.form.get('password'),
            firstname=request.form.get('firstname'),
            lastname=request.form.get('lastname'),
        )

        token = create_access_token(identity=user.id)
        print("jsonify token: ", jsonify(token=token))

        if profile_image is not None:
            [url] = upload_to_aws(profile_image)  # TODO: refactor to account for [orig_size_img, small_size_img]
            user_image = UserImage(
                image_url=url,
                user_uid=user.id
            )
            db.session.add(user_image)
            db.session.commit()

            return jsonify(token=token, user=user.serialize(), user_image=user_image.serialize()), 201

        return jsonify(token=token, user=user.serialize()), 201

    # todo: refactor to only have try/execpt around databse edits.
    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424


# endregion

# region User Image Endpoints Start

@app.post("/api/user_image")
@jwt_required()
def add_user_image():
    """ Adds image to the currently logged-in user
    Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}
    """

    try:
        current_user_id = get_jwt_identity()
        profile_image = request.files.get("profile_image")

        if profile_image is not None:
            image_url = aws_upload_image(profile_image)
            image_element = db_add_user_image(current_user_id, image_url)
            image = UserImage.query.get_or_404(image_element.id)

            return jsonify(user_image=image.serialize()), 201

        return jsonify({"error": "Failed to add image"}), 424

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to add image"}), 424


@app.get("/api/current_user_image/")
@jwt_required()
def get_current_user_image():
    """ Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        user_image = user.profile_image

        return jsonify(user_image=user_image.serialize()), 200

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to get image"}), 424


@app.get("/api/user_image/<int:user_image_id>")
def get_other_user_image(user_image_id):
    """ Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}
    """

    try:
        user_image = UserImage.query.get_or_404(user_image_id)

        return jsonify(user_image=user_image.serialize()), 200

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to get image"}), 424


@app.patch("/api/user_image/<int:user_image_id>")
@jwt_required()
def update_user_image(user_image_id):
    """ Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        user_image = UserImage.query.get_or_404(user_image_id)

        if user.id == user_image.user.id:
            profile_image = request.files.get("profile_image")

            if user_image is not None:
                aws_delete_image(user_image.image_url)

            if profile_image is not None:
                image_url = aws_upload_image(profile_image)
                user_image.image_url = image_url
                db.session.commit()

                return jsonify(user_image=user_image.serialize()), 200

        return jsonify({"error": "Failed to update image"}), 424

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to update image"}), 424


@app.delete("/api/user_image/<int:user_image_id>")
@jwt_required()
def delete_user_image(user_image_id):
    """ Returns JSON like:
        {user_image: {user_image_uid, image_url, user_uid}}
    """

    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        user_image = UserImage.query.get_or_404(user_image_id)

        if user.id == user_image.user.id or user.is_admin:
            aws_delete_image(user_image.image_url)
            db.session.delete(user_image)
            db.session.commit()

            return jsonify(user=user.serialize(), user_profile_image=user.profile_image), 200

        return jsonify({"error": "Failed to delete image"}), 424

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to delete image"}), 424


# endregion

# region Address Endpoints Start

@app.post("/api/address")
@jwt_required()
def create_address():
    """ Adds address to the currently logged-in user
    Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    current_user = get_jwt_identity()
    user = User.query.get_or_404(current_user)
    data = request.json

    # TODO: SET UP SCHEMA VALIDATOR
    address_in = data['address']
    city_in = data['city']
    state_in = data['state']
    zipcode_in = data['zipcode']
    user, address, city, state, zipcode, address_string = set_retrieve_address(user, address_in, city_in,
                                                                               state_in, zipcode_in)
    # TODO: VALIDATE ADDRESS USING GOOLGE MAPS OR SIM API

    return jsonify(
        user=user.serialize(),
        address=address.serialize(),
        state=state.serialize(),
        city=city.serialize(),
        zipcode=zipcode.serialize(),
        # location=location.serialize() # NOTE: getting this error: 'Object of type WKBElement is not JSON serializable'. NOT SURE HOW TO FIX
    ), 201


@app.get("/api/address/<int:address_id>")
def get_address(address_id):
    """ Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    try:
        address = Address.query.get_or_404(address_id)

        return jsonify(address=address.serialize()), 200

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to get address"}), 424


@app.patch("/api/address/<int:address_id>")
@jwt_required()
def update_address(address_id):
    """ Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    current_user = get_jwt_identity()
    user = User.query.get_or_404(current_user)
    address = Address.query.get_or_404(address_id)
    # TODO: IF DB IS RESEEDED, AND MOTIONS ARE DONE, USERID IS THE SAME.
    if user.id == address.user.id or user.is_admin:

        if address.location is not None:
            try:
                db.session.delete(address.location)
                db.session.delete(
                    address)  # @Lucas: Should I be deleting the address here or should i just be changing it?
                db.session.commit()
            except Exception as error:
                print("Error", error)
                return jsonify({"error": "Failed to update address"}), 424

        address_in = request.json['address']
        city_in = request.json['city']
        state_in = request.json['state']
        zipcode_in = request.json['zipcode']
        user, address, city, state, zipcode, address_string = set_retrieve_address(user, address_in, city_in, state_in,
                                                                                   zipcode_in)

        # TODO: FE - control this on front end and have user use a drop down of selectable options only

        return jsonify(
            user=user.serialize_with_address(),
            state=state.serialize(),
            city=city.serialize(),
            zipcode=zipcode.serialize(),
            # location=location.serialize() # NOTE: getting this error: 'Object of type WKBElement is not JSON serializable'. NOT SURE HOW TO FIX
        ), 200

    return jsonify({"error": "Failed to update address"}), 424


@app.delete("/api/address/<int:address_id>")
@jwt_required()
def delete_address(address_id):
    """ Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    try:
        current_user = get_jwt_identity()
        user = User.query.get_or_404(current_user)
        address = Address.query.get_or_404(address_id)

        if user.id == address.user.id:
            db.session.delete(address)
            db.session.commit()

            return jsonify(user=user.serialize()), 200

        return jsonify({"error": "Failed to delete address"}), 424

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to delete address"}), 424


# endregion


# region USERS List ENDPOINTS START

@app.get("/api/users")
def list_users():
    """Return all users in system.

    Returns JSON like:
        {users: [{user_uid, email, status, firstname, lastname, image_url,
        location, books, reservations}, ...]}
    """

    users = User.query.all()

    serialized = [user.serialize() for user in users]

    return jsonify(users=serialized)


@app.get('/api/users/<int:user_uid>')
def show_user(user_uid):
    """Show user profile.

    Returns JSON like:
        {user: user_uid, email, image_url, firstname, lastname, address, owned_books, reservations}
    """
    user = User.query.get_or_404(user_uid)
    user = user.serialize()

    return jsonify(user=user)


@app.patch('/api/users/<int:user_uid>')
@jwt_required()
def update_user(user_uid):
    """ update user information

    Returns JSON like:
        {user: user_uid, email, firstname, lastname, image_url, location, owned_books, reservations}
    """

    current_user = get_jwt_identity()
    if current_user == user_uid:
        user = User.query.get_or_404(user_uid)
        data = request.json
        # TODO: ADD "CHANGE PASSWORD FEATURE LATER"
        user.email = data['email'],
        user.location = data['location'],

        db.session.add(user)
        db.session.commit()

        return jsonify(user=user.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@app.patch('/api/users/<int:user_uid>/toggle_status')
@jwt_required()
def toggle_user_status(user_uid):
    """ Toggles_user's activity_status """

    current_user = get_jwt_identity()
    if current_user == user_uid:
        user = User.query.get_or_404(user_uid)

        if user.status == "Active":
            user.status = "Deactivated"
        else:
            user.status = "Active"

        db.session.add(user)
        db.session.commit()

        return jsonify(user=user.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@app.delete('/api/users/delete/<int:user_uid>')
@jwt_required()
def delete_user(user_uid):
    """Delete user. """

    # TODO: add admin role to delete users
    current_user = get_jwt_identity()
    if current_user == user_uid or current_user.is_admin:
        user = User.query.get_or_404(user_uid)

        db.session.delete(user)
        db.session.commit()

        return jsonify("User successfully deleted", 200)
    return jsonify({"error": "not authorized"}), 401


# endregion

# region Search Endpoints
@app.get("/search")
def search():
    """ Searches book properties for matched or similar values.

    Returns JSON like:
        {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    # query_string = request.query_string

    # endurance
    # 94108

    # logged_in_user_uid, book_title, book_author, city, state, zipcode
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
    city_books = get_all_books_in_city("Hercules")
    state_books = get_all_books_in_state("CA")
    zipcode_books = get_all_books_in_zipcode("94547")
    all_books = Book.query.all()
    searched_books = basic_book_search(1, title, author, city, state, zipcode)

    serialized = [book.serialize() for book in searched_books]
    return jsonify(books=serialized)


@app.get("/api/search/books_nearby")
def list_nearby_books():
    """ Shows all books nearby

    Returns JSON like: {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre,
    condition, price, reservations},...}
    """

    title = request.args.get('title')
    author = request.args.get('author')

    books = books_within_radius(38.006370860286694, -122.28195023589687, 1000, 1, title, author)

    serialized = [book.serialize() for book in books]

    return jsonify(books=serialized)


@app.get("/api/search/nearby")
def list_nearby():
    """ Shows all points nearby """

    locations = locations_within_radius(38.006370860286694, -122.28195023589687, 1000)

    return locations


# endregion


# region BOOKS ENDPOINTS START

@app.get("/api/books")
def list_all_books():
    """Return all books in system.

    Returns JSON like:
       {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """
    books = Book.query.all()

    serialized = [book.serialize() for book in books]
    return jsonify(pools=serialized)


@app.get('/api/users/<int:user_uid>/books')
def list_books_of_user(user_uid):
    """Show books of specified user.

    Returns JSON like:
        {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    user = User.query.get_or_404(user_uid)
    books = user.books
    serialized = [book.serialize() for book in books]

    return jsonify(books=serialized)


@app.get('/api/books/<int:book_uid>')
def show_book_by_id(book_uid):
    """Return information on a specific book.

    Returns JSON like:
        {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """
    book = Book.query.get_or_404(book_uid)
    serialized = book.serialize()

    return jsonify(book=serialized)


@app.get('/api/search/books/city')
def show_books_by_city():
    """Return books in a specific city.

    Returns JSON like:
        {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    city = request.args.get('city')  # mandatory

    books = get_all_books_in_city(city)

    serialized = [book.serialize() for book in books]
    return jsonify(books=serialized)


@app.get('/api/search/books/state')
def show_books_by_state():
    """Return books in a specific state.

    Returns JSON like:
        {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    state = request.args.get('state')  # mandatory

    books = get_all_books_in_state(state)

    serialized = [book.serialize() for book in books]
    return jsonify(books=serialized)


@app.get('/api/search/books/zipcode')
def search_books_by_zipcode():
    """Return books in a specific zipcode.

    Returns JSON like:
        {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """

    zipcode = request.args.get('zipcode')  # mandatory

    books = get_all_books_in_zipcode(zipcode)

    serialized = [book.serialize() for book in books]
    return jsonify(books=serialized)


@app.post("/api/books")
@jwt_required()
def create_book():
    """Add book, and return data about new book.

    Returns JSON like:
        {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}
    """
    # TODO: try posting a book object to the db first. if successful, post book image to aws, if successful,
    #  switch url for book from dummy_url to aws_url. if anything fails delete the book and the book image.
    # https://www.geeksforgeeks.org/try-except-else-and-finally-in-python/

    print("I'm in api/books")
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

            # post book to db
            book_posted = db_post_book(current_user_id, title, author, isbn, condition, rate_price, rate_schedule)

            images_posted = []
            # post image to aws

            for image in images:
                image_url = aws_upload_image(images[image])
                # post image to database
                image_element = db_add_book_image(current_user_id, book_posted.id, image_url)
                images_posted.append(image_element.serialize())

            # TODO: might have to set primary book image here but then its pinging the db twice for the patch request

            return jsonify(book=book_posted.serialize(), images_posted=images_posted), 201

        except Exception as error:
            print("Error", error)
            return jsonify({"error": f"Failed to add book and book image: {error}", }), 401


@app.patch('/api/books/<int:book_uid>')
@jwt_required()
def update_book(book_uid):
    """ Update book information

    Returns JSON like:
        {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of book
    """

    current_user = get_jwt_identity()
    book = Book.query.get_or_404(book_uid)
    print("book owner", book.owner_username)
    if current_user == book.owner_username:
        data = request.json

        book.orig_image_url = data['orig_image_url'],
        book.small_image_url = data['small_image_url'],
        book.title = data['title'],
        book.author = data['author'],
        book.isbn = data['isbn'],
        book.genre = data['genre'],
        book.condition = data['condition'],
        book.price = data['price'],

        db.session.add(book)
        db.session.commit()

        return jsonify(book=book.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@app.patch('/api/users/<int:user_uid>/books/<int:book_uid>/toggle_status')
@jwt_required()
def toggle_book_status(user_uid, book_uid):
    """ Toggles book availability status. """

    current_user = get_jwt_identity()

    if current_user == user_uid:
        book = Book.query.get_or_404(book_uid)

        if book.status == "Available":
            book.status = "Checked Out"
        else:
            book.status = "Available"

        db.session.add(book)
        db.session.commit()

        return jsonify(book=book.serialize()), 200

    return jsonify({"error": "not authorized"}), 401


@app.delete('/api/books/<int:book_uid>')
@jwt_required()
def delete_book(book_uid):
    """ update book information

    Returns JSON like:
    {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}

    Authorization: must be owner of book
    """

    current_user = get_jwt_identity()
    book = Book.query.get_or_404(book_uid)
    if current_user == book.owner_uid:
        db.session.delete(book)
        db.session.commit()

        return jsonify("Book successfully deleted"), 200

    return jsonify({"error": "not authorized"}), 401


@app.post("/api/books/<int:book_uid>/images")
@jwt_required()
def add_book_image(book_uid):
    """Add book image, and return data about book image.

    Returns JSON like:
        {book_image: {id, book_owner, image_url }}
    """
    # TODO: if we get an array of files, then we could do a list comprehension where
    # we use the helper function and add that to the table for each one in the comprehension

    current_user = get_jwt_identity()
    book = Book.query.get_or_404(book_uid)
    if current_user == book.owner_username:
        file = request.files['file']
        url = upload_to_aws(file)  # TODO: refactor to account for [orig_size_img, small_size_img]

        book_image = BookImage(
            book_owner=current_user,
            image_url=url
        )

        db.session.add(book_image)
        db.session.commit()

        return jsonify(book_image=book_image.serialize()), 201

    return jsonify({"error": "not authorized"}), 401


# endregion


# region RESERVATIONS ENDPOINTS START


@app.post("/api/reservations/<int:book_uid>")
@jwt_required()
def create_reservation(book_uid):
    """ Creates a reservation for the pool you're looking at if you are logged in

    Returns JSON like:
        {reservation: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }}
    """

    current_user = get_jwt_identity()
    user = User.query.get_or_404(current_user)

    if user:
        data = request.json

        start_date_in = data['start_date']
        duration_in = data['duration']

        book = Book.query.get_or_404(book_uid)
        start_date = datetime.strptime(start_date_in, '%Y-%m-%d')
        duration = int(duration_in)
        book_rate_schedule = book.rate_schedule

        reservation = create_new_reservation(start_date, duration, book_rate_schedule, book, user)

        return jsonify(reservation=reservation.serialize()), 201

    return jsonify({"error": "not authorized"}), 401


@app.get("/api/reservations")
def list_all_reservations():
    """Return all reservations in system.

    Returns JSON like:
       {reservations: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}
    """
    reservations = Reservation.query.all()

    serialized = [reservation.serialize() for reservation in reservations]
    return jsonify(reservations=serialized)


@app.get("/api/reservations/<int:book_uid>/upcoming")
@jwt_required()
def get_all_upcoming_reservations_for_book(book_uid):
    """ Gets all upcoming reservations associated with book_uid

    Returns JSON like:
        {reservations: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    current_user_id = get_jwt_identity()

    book = Book.query.get_or_404(book_uid)
    if book.owner == current_user_id:
        reservations = book.reservations.filter(Reservation.start_date > datetime.now())

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return jsonify(reservations=serialized_reservations)

    # TODO: better error handling for more diverse errors
    return jsonify({"error": "not authorized"}), 401


@app.get("/api/reservations/<int:book_uid>/past")
@jwt_required()
def get_all_past_reservations_for_book(book_uid):
    """ Gets all past reservations associated with book_uid

    Returns JSON like:
        {reservations: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    current_user_id = get_jwt_identity()

    book = Book.query.get_or_404(book_uid)
    if book.owner == current_user_id:
        reservations = book.reservations.filter(Reservation.start_date < datetime.now())

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return jsonify(reservations=serialized_reservations)

    # TODO: better error handling for more diverse errors
    return jsonify({"error": "not authorized"}), 401


@app.get("/api/reservations/user/<int:user_uid>")
@jwt_required()
def get_booked_reservations_for_user_uid(user_uid):
    """ Gets all reservations created by a user_uid

    Returns JSON like:
        {reservations: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    current_user = get_jwt_identity()

    user = User.query.get_or_404(user_uid)
    if user.id == current_user:
        reservations = (Reservation.query
                        .filter(owner_uid=current_user)
                        .order_by(Reservation.start_date.desc()))

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return jsonify(reservations=serialized_reservations)

    # TODO: better error handling for more diverse errors
    return jsonify({"error": "not authorized"}), 401


@app.get("/api/reservations/<int:reservation_id>")
@jwt_required()
@is_book_owner_or_is_reservation_booker_or_is_admin
def get_reservation(reservation_id):
    """ Gets specific reservation """

    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation:
        serialized_reservation = reservation.serialize()

        return jsonify(reservation=serialized_reservation), 200

    # TODO: better error handling for more diverse errors
    return jsonify({"error": "not authorized"}), 401


@app.patch("/api/reservations/<int:reservation_id>")
@jwt_required()
@is_reservation_booker
def update_reservation(reservation_id):
    """ Updates specific reservation """

    # current_user_id = get_jwt_identity()
    reservation = Reservation.query.get_or_404(reservation_id)
    # book = reservation.book
    is_in_future = reservation_is_in_future(reservation)

    if is_in_future:
        data = request.json
        start_date_in = data['start_date']
        duration_in = data['duration']

        start_date = datetime.strptime(start_date_in, '%Y-%m-%d')
        int_duration = int(duration_in)

        reservation = attempt_reservation_update(reservation, start_date, int_duration)

        return jsonify(reservation=reservation.serialize()), 201

    return jsonify({"error": "not authorized"}), 401


@app.patch("/api/reservations/<int:reservation_id>/cancel")
@jwt_required()
@is_reservation_booker
def cancel_reservation_request(reservation_id):
    """ Cancels specific reservation """

    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    reservation = Reservation.query.get_or_404(reservation_id)
    book = reservation.book
    is_in_future = reservation_is_in_future(reservation)
    data = request.json
    cancellation_reason = data.get('cancellation_reason')
    reservation_status = reservation.status
    # TODO: CHECK USERS' CANCELLATION POLICY

    if (reservation_status == ReservationStatusEnum.PENDING) and is_in_future:
        reservation = attempt_to_cancel_reservation(reservation, cancellation_reason)

        return jsonify(reservation=reservation.serialize()), 201

    return jsonify({"error": "not authorized"}), 401


@app.patch("/api/reservations/<int:reservation_id>/accept")
@jwt_required()
@is_reservation_listing_owner
def accept_reservation(reservation_id):
    """ Accepts specific reservation """

    reservation = Reservation.query.get_or_404(reservation_id)
    is_in_future = reservation_is_in_future(reservation)

    if (reservation.status == ReservationStatusEnum.PENDING) and is_in_future:
        reservation = attempt_to_accept_reservation_request(reservation)

        return jsonify(reservation=reservation.serialize()), 201

    return jsonify({"error": "not authorized"}), 401


@app.patch("/api/reservations/<int:reservation_id>/decline")
@jwt_required()
@is_reservation_listing_owner
def decline_reservation(reservation_id):
    """ Declines specific reservation """

    reservation = Reservation.query.get_or_404(reservation_id)
    is_in_future = reservation_is_in_future(reservation)

    if (reservation.status == ReservationStatusEnum.PENDING) and is_in_future:
        reservation = attempt_to_decline_reservation_request(reservation)

        return jsonify(reservation=reservation.serialize()), 201

    return jsonify({"error": "not authorized"}), 401


# endregion


# region MESSAGES ENDPOINTS START

@app.post("/api/messages")
@jwt_required()
def create_message():
    """ Creates a message to be sent to listing owner.

    Returns JSON like:
        {message: {message_uid, reservation_uid, sender_uid, recipient_uid, text, timestamp}}
    """

    current_user_id = get_jwt_identity()

    data = request.json
    book_listing_id = data.get('book_listing_id')
    recipient_uid = data.get('recipient_uid')
    message_text = data.get('message_text')
    # timestamp = data.get('timestamp')

    listing = Book.query.get_or_404(book_listing_id)

    # Ensure that the current user is the owner of the book listing or interested party
    # if listing.owner_uid != current_user_id | listing.renter_uid != current_user_id:
    #     return jsonify({"error": "You are not authorized to send messages for this book listing"}), 401

    try:
        message = Message(
            reservation_uid=book_listing_id,
            sender_uid=current_user_id,
            recipient_uid=recipient_uid,
            message_text=message_text,
        )

        db.session.add(message)
        db.session.commit()

        return jsonify(message=message.serialize(f"{message.sender.firstname} {message.sender.lastname}",
                                      f"{message.recipient.firstname} {message.recipient.lastname}")), 201
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "not authorized"}), 401


@app.get("/api/messages/all")
@jwt_required()
def show_all_messages():
    """Gets all messages, organizing them into conversations"""

    current_user_id = get_jwt_identity()

    # Query all messages involving the current user
    messages = (Message.query
                .filter((Message.sender_uid == current_user_id) | (Message.recipient_uid == current_user_id))
                .order_by(Message.timestamp.desc()))

    # Group messages into conversations based on sender and recipient
    conversations = defaultdict(list)
    for message in messages:
        # Determine the conversation participant
        participant_id = message.recipient_uid if message.sender_uid == current_user_id else message.sender_uid
        conversations[participant_id].append(message.serialize(f"{message.sender.firstname} {message.sender.lastname}",
                                      f"{message.recipient.firstname} {message.recipient.lastname}"))

    # Convert the defaultdict to a regular dictionary
    conversations = dict(conversations)

    return jsonify(conversations=conversations), 200


@app.get("/api/messages/listing/<int:book_listing_id>")
@jwt_required()
def show_conversation(book_listing_id):
    """Gets the conversation between the current user and the book owner"""

    current_user_id = get_jwt_identity()
    book = Book.query.get_or_404(book_listing_id)
    book_owner = book.owner

    # Query messages between the current user and the book owner
    listing_messages = Message.query.filter(Message.reservation_uid == book_listing_id)

    # check for message sender is book owner or current user
    users_messages = (listing_messages
                      .filter(((Message.sender_uid == current_user_id) & (Message.recipient_uid == book_owner.id)) |
                              ((Message.sender_uid == book_owner.id) & (Message.recipient_uid == current_user_id)))
                      .order_by(Message.timestamp.asc())).all()

    conversation = [message.serialize(f"{message.sender.firstname} {message.sender.lastname}",
                                      f"{message.recipient.firstname} {message.recipient.lastname}") for message in
                    users_messages]

    return jsonify(conversation=conversation), 200


@app.get("/api/messages/single/<int:message_id>")
@jwt_required()
# @is_message_sender_reciever_or_admin
def show_message(message_id):
    """ Show specific message

    Returns JSON like:
        {message: {message_uid, reservation_uid, sender_uid, recipient_uid, text, timestamp}}
    """

    message = Message.query.get_or_404(message_id)
    sender_name = f"{message.sender.firstname} {message.sender.lastname}"
    recipient_name = f"{message.recipient.firstname} {message.recipient.lastname}"

    message = message.serialize(f"{sender_name}", f"{recipient_name}")
    return jsonify(message=message), 200

# endregion
