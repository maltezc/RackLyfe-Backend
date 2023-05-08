import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from models import db, connect_db, User, Address, City, State, ZipCode, Message, Book, Reservation, BookImage, \
    UserImage, Location
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from api_helpers import upload_to_aws, db_post_book, aws_upload_image, db_add_book_image
from util_filters import get_all_users_in_city, get_all_users_in_state, get_all_users_in_zipcode, get_all_books_in_city, \
    get_all_books_in_state, get_all_books_in_zipcode, basic_book_search, locations_within_radius, books_within_radius, \
    geocode_address
from decorators import admin_required

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
    token = create_access_token(identity=user.user_uid)

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

        token = create_access_token(identity=user.user_uid)

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
            password=request.form.get('password'),
            firstname=request.form.get('firstname'),
            lastname=request.form.get('lastname'),
        )

        token = create_access_token(identity=user.user_uid)
        print("jsonify token: ", jsonify(token=token))

        if profile_image is not None:
            [url] = upload_to_aws(profile_image)  # TODO: refactor to account for [orig_size_img, small_size_img]
            user_image = UserImage(
                image_url=url,
                user_uid=user.user_uid
            )
            db.session.add(user_image)
            db.session.commit()

            return jsonify(token=token, user=user.serialize(), user_image=user_image.serialize()), 201

        return jsonify(token=token, user=user.serialize()), 201

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424


# endregion


# region Address Endpoints Start
@app.post("/api/address")
@jwt_required()
def create_address():
    """ Adds address to the currently logged-in user
    Returns JSON like:
        {address: {address_uid, street, city, state, zipcode}}
    """

    try:
        current_user = get_jwt_identity()
        user = User.query.get_or_404(current_user)
        data = request.json

        # TODO: should have table of states already set up
        state = data['state']
        state_found_id = State.query.filter(State.state_abbreviation == state).first().id
        state = State.query.get_or_404(state_found_id)
        # books = Book.query.filter(Book.owner_uid == user_uid)

        # TODO: write checker for city to confirm its actually a real city
        existing_city = City.query.filter(City.city_name == data['city']).first()
        if existing_city is not None:
            city = existing_city
        else:
            new_city = City(city_name=data['city'], state_uid=state_found_id)
            db.session.add(new_city)
            db.session.commit()
            city = new_city

        # TODO: write checker for zipcode to confirm its actually a real zipcode
        zipcode = str(data['zipcode'])
        existing_zipcode = ZipCode.query.filter(ZipCode.code == zipcode).first()
        if existing_zipcode is not None:
            zipcode = existing_zipcode
        else:
            zipcode = ZipCode(code=data['zipcode'])
            db.session.add(zipcode)
            db.session.commit()

        # TODO: write checker for address to confirm its actually a real address
        street_address = data['address']
        existing_address = Address.query.filter(Address.street_address == street_address).first()
        if existing_address is not None:
            address = existing_address
        else:
            address = Address(street_address=street_address,
                              city_uid=city.id,
                              zipcode_uid=zipcode.id
                              )
            db.session.add(address)
            db.session.commit()

        address_string = f"{address.street_address} {city.city_name}, {state.state_abbreviation} {zipcode.code}"
        geocoded_address = geocode_address(address_string)
        location = Location(point=f"POINT({geocoded_address[1]} {geocoded_address[0]})")
        db.session.add(location)
        db.session.commit()

        address.latlong_uid = location.id

        user.address = address.address_uid
        db.session.commit()

        return jsonify(address=address.serialize()), 201

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to create address"}), 424


# endregion


# region USERS ENDPOINTS START

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


@app.get('/api/users/<int:user_uid>/books')
def list_books_of_user(user_uid):
    """Show books of logged in user.

    Returns JSON like:
        {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """
    books = Book.query.filter(Book.owner_uid == user_uid)
    serialized = [book.serialize() for book in books]

    return jsonify(books=serialized)


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
def list_books():
    """Return all books in system.

    Returns JSON like:
       {books: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}, ...}
    """
    books = Book.query.all()

    serialized = [book.serialize() for book in books]
    return jsonify(pools=serialized)


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
                image_element = db_add_book_image(current_user_id, book_posted.book_uid, image_url)
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

@app.get("/api/reservations")
def list_reservations():
    """Return all reservations in system.

    Returns JSON like:
       {reservations: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}
    """
    reservations = Reservation.query.all()

    serialized = [reservation.serialize() for reservation in reservations]
    return jsonify(reservations=serialized)


@app.post("/api/reservations/<int:book_uid>")
@jwt_required()
def create_reservation(book_uid):
    """ Creates a reservation for the pool you looking at if you are logged in

    Returns JSON like:
        {reservation: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }}
    """

    current_user = get_jwt_identity()

    if current_user:
        data = request.json

        reservation = Reservation(
            renter_uid=current_user,
            book_uid=book_uid,
            reservation_date_created=data['reservation_date_created'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            reservation_uid=data['reservation_uid'],
            status=data['status'],
            rental_period=data['rental_period'],
            total=data['total']
        )

        db.session.add(reservation)
        db.session.commit()

        return (jsonify(reservation=reservation.serialize()), 201)

    return (jsonify({"error": "not authorized"}), 401)


@app.get("/api/reservations/<int:book_uid>")
@jwt_required()
def get_reservations_for_book(book_uid):
    """ Gets all reservations assocaited with book_uid

    Returns JSON like:
        {reservations: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    current_user = get_jwt_identity()

    book = Book.query.get_or_404(book_uid)
    if (book.owner_uid == current_user):
        reservations = (Reservation.query
                        .filter(book_uid=book_uid)
                        .order_by(Reservation.start_date.desc()))

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return (jsonify(reservations=serialized_reservations))

    # TODO: better error handling for more diverse errors
    return jsonify({"error": "not authorized"}), 401


@app.get("/api/reservations/<int:user_uid>")
@jwt_required()
def get_booked_reservations_for_user_uid(user_uid):
    """ Gets all reservations created by a user_uid

    Returns JSON like:
        {reservations: {reservation_uid, book_uid, owner_uid, renter_uid, reservation_date_created, start_date, end_date, status, rental_period, total }, ...}

    """

    current_user = get_jwt_identity()

    user = User.query.get_or_404(user_uid)
    if (user.user_uid == current_user):
        reservations = (Reservation.query
                        .filter(owner_uid=current_user)
                        .order_by(Reservation.start_date.desc()))

        serialized_reservations = ([reservation.serialize()
                                    for reservation in reservations])

        return (jsonify(reservations=serialized_reservations))

    # TODO: better error handling for more diverse errors
    return (jsonify({"error": "not authorized"}), 401)


@app.get("/api/reservations/<int:reservation_id>")
@jwt_required()
def get_booked_reservation(reservation_id):
    """ Gets specific reservation """

    current_user = get_jwt_identity()

    reservation = Reservation.get_or_404(reservation_id)
    book_uid = reservation.book_uid
    book = Book.get_or_404(book_uid)

    if ((reservation.renter_uid == current_user) or
            (book.owner_uid == current_user)):
        serialized_reservation = reservation.serialize()

        return (jsonify(reservation=serialized_reservation), 200)

    # TODO: better error handling for more diverse errors
    return (jsonify({"error": "not authorized"}), 401)


# // TODO: delete reservation
# @app.delete("/api/reservations/<int:reservation_id>")
# @jwt_required()
# def delete_booked_reservation(reservation_id):
#     """ Deletes a specific reservation if either pool owner or reservation booker """

#     current_user = get_jwt_identity()

#     reservation = Reservation.get_or_404(reservation_id)
#     pool_id = reservation.pool_id
#     pool = Pool.get_or_404(pool_id)

#     if ((reservation.booked_username == current_user) or
#         (pool.owner_username == current_user)):


#         db.session.delete(reservation)
#         db.session.commit()

#         return (jsonify("Reservation successfully deleted"), 200)

#     #TODO: better error handling for more diverse errors
#     return (jsonify({"error": "not authorized"}), 401)

# endregion


# region MESSAGES ENDPOINTS START

@app.get("/api/messages")
@jwt_required()
def list_messages():
    """ Gets all messages outgoing and incoming to view

    Returns JSON like:
        {messages: {message_uid, reservation_uid, sender_uid, recipient_uid, text, timestamp}, ...}

    """

    current_user = get_jwt_identity()
    # inbox
    messages_inbox = (Message.query
                      .filter(Message.recipient_username == current_user)
                      .order_by(Message.timestamp.desc()))
    serialized_inbox = [message.serialize() for message in messages_inbox]

    # outbox
    messages_outbox = (Message.query
                       .filter(Message.sender_username == current_user)
                       .order_by(Message.timestamp.desc()))
    serialized_outbox = [message.serialize() for message in messages_outbox]

    response = {"messages": {"inbox": serialized_inbox, "outbox": serialized_outbox}}
    return response


@app.post("/api/messages")
@jwt_required()
def create_message():
    """ Creates a message to be sent to listing owner.

    Returns JSON like:
        {message: {message_uid, reservation_uid, sender_uid, recipient_uid, text, timestamp}}
    """

    current_user = get_jwt_identity()

    data = request.json
    message = Message(
        reservation_uid=data['reservation_uid'],
        sender_uid=current_user,
        recipient_uid=data['recipient_uid'],
        message_text=data['message_text'],
        timestamp=data['timestamp']
    )

    db.session.add(message)
    db.session.commit()

    return jsonify(message=message.serialize()), 201


@app.get("/api/messages/<message_uid>")
@jwt_required
def show_message(message_uid):
    """ Show specific message

    Returns JSON like:
        {message: {message_uid, reservation_uid, sender_uid, recipient_uid, text, timestamp}}
    """

    current_user = get_jwt_identity()

    message = User.query.get_404(message_uid)

    if ((message.sender_uid == current_user) or
            (message.recipient_uid == current_user)):
        message = message.serialize()
        return jsonify(message=message)
    else:
        return jsonify({"error": "not authorized"}), 401

# endregion
