import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from models import db, connect_db, User, Address, City, State, ZipCode, Message, Book, Reservation, BookImage
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from api_helpers import upload_to_aws
from util_filters import get_all_users_in_city, get_all_users_in_state, get_all_users_in_zipcode, get_all_books_in_city, \
    get_all_books_in_state, get_all_books_in_zipcode, basic_book_search, locations_within_radius, books_within_radius

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
    # token = create_access_token(identity=user.email)

    return jsonify(token=token)


@app.post("/api/auth/signup")
def create_user():
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {user_uid, email, image_url, firstname, lastname, address, preferred_trade_location}}
    """
    print("form", request.form)
    try:
        form = request.form
        print("form", form)

        file = request.files.get('file')
        url = None
        if (file):
            [url] = upload_to_aws(file)  # TODO: refactor to account for [orig_size_img, small_size_img]
            # print("url", url)
            # print("request.form.get('text')", request.form.get('text'))
            # print("request.form['text']", request.form['text'])
            # print("request.form['text'].keys()", request.form['text'].keys())
            # print("request.forms.keys", request.form.keys())
            # print("request.forms.items", request.form.items())

        user = User.signup(
            email=form['email'],
            password=form['password'],
            firstname=form['firstname'],
            lastname=form['lastname'],
            address=form['address'],
            preferred_trade_location=form['preferred_trade_location'],
            image_url=url
        )
        db.session.commit()

        # user = User.authenticate(username, password)
        token = create_access_token(identity=user.email)
        print("jsonify token: ", jsonify(token=token))

        return jsonify(token=token)

        # return (jsonify(user=user.serialize()), 201)

    except Exception as error:
        print("Error", error)
        return jsonify({"error": "Failed to signup"}), 424


# endregion

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

    current_user = get_jwt_identity()
    if current_user == user_uid:
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


# @app.post("/api/pools")
# @jwt_required()
# def create_pool():
#     """Add pool, and return data about new pool.

#     Returns JSON like:
#         {pool: {id, owner_id, rate, size, description, address, image_url}}
#     """

#     current_user = get_jwt_identity()
#     if current_user:
#         data = request.json
#         print("data", data)
#         pool = Pool(
#             owner_username=current_user,
#             rate=data['rate'],
#             size=data['size'],
#             description=data['description'],
#             city=data['city'],
#             orig_image_url=data['orig_image_url']
#         )

#         db.session.add(pool)
#         db.session.commit()

#         # POST requests should return HTTP status of 201 CREATED
#         return (jsonify(pool=pool.serialize()), 201)

#     return (jsonify({"error": "not authorized"}), 401)

# @app.post("/api/users/<int:user_uid>/books")
@app.post("/api/books")
@jwt_required()
def create_book():
    """Add book, and return data about new book.

    Returns JSON like:
        {book: {book_uid, owner_uid, orig_image_url, small_image_url, title, author, isbn, genre, condition, price, reservations}}
    """
    # TODO: try posting a book object to the db first. if successful, post book image to aws, if successful,
    #  switch url for book from dummy_url to aws_url.
    # https://www.geeksforgeeks.org/try-except-else-and-finally-in-python/

    print("I'm in api/books")
    current_user = get_jwt_identity()
    if current_user:
        try:
            form = request.form
            print("current_user", current_user)
            print("form", form)
            file = request.files.get('file')
            print("file", file)
            orig_url = None
            if (file):
                [orig_url, small_url] = upload_to_aws(file)

            book = Book(
                owner_uid=current_user,
                title=form['title'],
                author=form['author'],
                isbn=form['isbn'],
                genre=form['genre'],
                condition=form['condition'],
                price=form['price'],
                orig_image_url=orig_url,
                small_image_url=small_url
            )

            db.session.add(book)
            db.session.commit()

            return (jsonify(book=book.serialize()), 201)
        except Exception as error:
            print("Error", error)
            return (jsonify({"error": "Failed to add book"}), 401)


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

        return (jsonify(book=book.serialize()), 200)

    return (jsonify({"error": "not authorized"}), 401)


@app.patch('/api/users/<int:user_uid>/books/<int:book_uid>/toggle_status')
@jwt_required()
def toggle_book_status(user_uid, book_uid):
    """ Toggles book availability status. """

    current_user = get_jwt_identity()

    # book_owner_uid = book.owner_uid

    if current_user == user_uid:
        # user = User.query.get_or_404(book_uid)
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

        return (jsonify("Book successfully deleted"), 200)

    return (jsonify({"error": "not authorized"}), 401)


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

        return (jsonify(book_image=book_image.serialize()), 201)

    return (jsonify({"error": "not authorized"}), 401)


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
    return (jsonify({"error": "not authorized"}), 401)


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

    return (jsonify(message=message.serialize()), 201)


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
        return (jsonify({"error": "not authorized"}), 401)

# endregion
