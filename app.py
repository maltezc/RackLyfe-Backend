import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from models import db, connect_db, User, Message, Pool, Reservation, PoolImage
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from api_helpers import upload_to_aws


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
app.config["JWT_IDENTITY_CLAIM"] = "username"


connect_db(app)
db.create_all()

#######################  AUTH ENDPOINTS START  ################################

@app.route("/api/auth/login", methods=["POST"])
def login():
    """ Login user, returns JWT if authenticated """

    data = request.json
    username = data['username']
    password = data['password']

    user = User.authenticate(username, password)
    token = create_access_token(identity=user.username)

    return jsonify(token=token)


@app.post("/api/auth/signup")
def create_user():
    """Add user, and return data about new user.

    Returns JSON like:
        {user: {id, email, username, image_url, location, reserved_pools, owned_pools}}
    """
    print("form", request.form)
    try:
        form = request.form
        print("form", form)

        file = request.files.get('file')
        url = None
        if (file):
            [url] = upload_to_aws(file) # TODO: refactor to account for [orig_size_img, small_size_img]
            # print("url", url)
            # print("request.form.get('text')", request.form.get('text'))
            # print("request.form['text']", request.form['text'])
            # print("request.form['text'].keys()", request.form['text'].keys())
            # print("request.forms.keys", request.form.keys())
            # print("request.forms.items", request.form.items())

        user = User.signup(
            username=form['username'],
            password=form['password'],
            email=form['email'],
            location=form['location'],
            image_url=url
        )
        db.session.commit()


        # user = User.authenticate(username, password)
        token = create_access_token(identity=user.username)
        print("jsonify token: ", jsonify(token=token))

        return jsonify(token=token)


        # return (jsonify(user=user.serialize()), 201)

    except Exception as error:
        print("Error", error)
        return (jsonify({"error": "Failed to signup"}), 424)


################################################################################
#######################  USERS ENDPOINTS START  ################################

@app.get("/api/users")
def list_users():
    """Return all users in system.

    Returns JSON like:
        {users: [{id, email, username, image_url,
        location, reserved_pools, owned_pools}, ...]}
    """
    users = User.query.all()

    serialized = [user.serialize() for user in users]

    return jsonify(users=serialized)

@app.get('/api/users/<username>')
def show_user(username):
    """Show user profile.

    Returns JSON like:
        {user: id, email, username, image_url, location, reserved_pools, owned_pools}
    """
    user = User.query.get_or_404(username)
    user = user.serialize()

    return jsonify(user=user)


@app.patch('/api/users/<username>')
@jwt_required()
def update_user(username):
    """ update user information

    Returns JSON like:
        {user: id, email, username, image_url, location, reserved_pools, owned_pools}
    """

    current_user = get_jwt_identity()
    if current_user == username:
        user = User.query.get_or_404(username)
        data = request.json
        # TODO: ADD "CHANGE PASSWORD FEATURE LATER"
        user.email = data['email'],
        user.location = data['location'],

        db.session.add(user)
        db.session.commit()

        return (jsonify(user=user.serialize()), 200)

    return (jsonify({"error": "not authorized"}), 401)


@app.delete('/api/users/delete/<username>')
@jwt_required()
def delete_user(username):
    """Delete user. """

    current_user = get_jwt_identity()
    if current_user == username:
        user = User.query.get_or_404(username)

        db.session.delete(user)
        db.session.commit()

        return jsonify("User successfully deleted", 200)
    return (jsonify({"error": "not authorized"}), 401)


@app.get('/api/users/<username>/pools')
def list_pools_of_user(username):
    """Show pools of logged in user.

    Returns JSON like:
        {pools: {id, owner_id, rate, size, description, address, image_url}, ...}
    """
    pools = Pool.query.filter(Pool.owner_username == username)
    serialized = [pool.serialize() for pool in pools]

    return jsonify(pools=serialized)


################################################################################
######################## POOLS ENDPOINTS START #################################

@app.get("/api/pools")
def list_pools():
    """Return all pools in system.

    Returns JSON like:
        {pools: {id, owner_id, rate, size, description, address, small_image_url}, ...}
    """
    pools = Pool.query.all()

    serialized = [pool.serialize() for pool in pools]
    return jsonify(pools=serialized)


@app.get('/api/pools/<int:pool_id>')
def show_pool_by_id(pool_id):
    """Show information on a specific pool.

    Returns JSON like:
        {pool: owner_username, rate, size, description, address}
    """
    pool = Pool.query.get_or_404(pool_id)
    pool = pool.serialize()

    return jsonify(pool=pool)

@app.get('/api/pools/<city>')
def show_pool_by_city(city):
    """Show information on a specific pool.

    Returns JSON like:
        {pool: owner_username, rate, size, description, address}
    """

    pools = Pool.query.filter(Pool.city == city)
    serialized = [pool.serialize() for pool in pools]

    return jsonify(pools=serialized)

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

@app.post("/api/pools")
@jwt_required()
def create_pool():
    """Add pool, and return data about new pool.

    Returns JSON like:
        {pool: {id, owner_id, rate, size, description, address, orig_image_url, small_image_url}}
    """
    print("I'm in api/pools")
    current_user = get_jwt_identity()
    if current_user:
        try:
            form=request.form
            print("current_user", current_user)
            print("form", form)
            file = request.files.get('file')
            print("file", file)
            orig_url=None
            if(file):
                [orig_url, small_url] = upload_to_aws(file)

            pool = Pool(
                owner_username=current_user,
                rate=form['rate'],
                size=form['size'],
                description=form['description'],
                city=form['city'],
                orig_image_url=orig_url,
                small_image_url=small_url
            )

            db.session.add(pool)
            db.session.commit()

            return (jsonify(pool=pool.serialize()), 201)
        except Exception as error:
            print("Error", error)
            return (jsonify({"error": "Failed to add pool"}), 401)


@app.patch('/api/pools/<int:pool_id>')
@jwt_required()
def update_pool(pool_id):
    """ update pool information

    Returns JSON like:
    {pool: owner_username, rate, size, description, address}

    Authorization: must be owner of pool
    """

    current_user = get_jwt_identity()
    pool = Pool.query.get_or_404(pool_id)
    print("pool owner", pool.owner_username)
    if current_user == pool.owner_username:
        data = request.json

        pool.rate = data['rate'],
        pool.size = data['size'],
        pool.description = data['description'],
        pool.address = data['address']

        db.session.add(pool)
        db.session.commit()

        return (jsonify(pool=pool.serialize()), 200)

    return (jsonify({"error": "not authorized"}), 401)

@app.delete('/api/pools/<int:pool_id>')
@jwt_required()
def delete_pool(pool_id):
    """ update pool information

    Returns JSON like:
    {pool: owner_username, rate, size, description, address}

    Authorization: must be owner of pool
    """

    current_user = get_jwt_identity()
    pool = Pool.query.get_or_404(pool_id)
    if current_user == pool.owner_username:

        db.session.delete(pool)
        db.session.commit()

        return (jsonify("Pool successfully deleted"), 200)

    return (jsonify({"error": "not authorized"}), 401)

@app.post("/api/pools/<int:pool_id>/images")
@jwt_required()
def add_pool_image(pool_id):
    """Add pool image, and return data about pool image.

    Returns JSON like:
        {pool_image: {id, pool_owner, image_url }}
    """
    # TODO: if we get an array of files, then we could do a list comprehension where
    # we use the helper function and add that to the table for each one in the comprehension

    current_user = get_jwt_identity()
    pool = Pool.query.get_or_404(pool_id)
    if current_user == pool.owner_username:
        file = request.files['file']
        url = upload_to_aws(file) # TODO: refactor to account for [orig_size_img, small_size_img]

        pool_image = PoolImage(
            pool_owner=current_user,
            image_url=url
        )

        db.session.add(pool_image)
        db.session.commit()

        return (jsonify(pool_image=pool_image.serialize()), 201)

    return (jsonify({"error": "not authorized"}), 401)

################################################################################
#######################  MESSAGES ENDPOINTS START  #############################


@app.get("/api/messages")
@jwt_required()
def list_messages():
    """ Gets all messages outgoing and incoming to view """

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

    response = {"messages" : {"inbox": serialized_inbox, "outbox": serialized_outbox}}
    return response


@app.post("/api/messages")
@jwt_required()
def create_message():
    """ Creates a message to be sent to listing owner. """

    current_user = get_jwt_identity()

    data = request.json
    message = Message(
        sender_username=current_user,
        recipient_username=data['recipient_username'],
        title=data['title'],
        body=data['body'],
        listing=data['listing'],
    )

    db.session.add(message)
    db.session.commit()

    return (jsonify(message=message.serialize()), 201)


@app.get("/api/messages/<message_id>")
@jwt_required
def show_message(message_id):
    """ Show specific message """

    current_user = get_jwt_identity()

    message = User.query.get_404(message_id)

    if ((message.sender_username == current_user) or
        (message.recipient_username == current_user)):
        message = message.serialize()
        return jsonify(message=message)
    else:
        return (jsonify({"error": "not authorized"}), 401)



################################################################################
#####################  RESERVATIONS ENDPOINTS START  ###########################

@app.post("/api/reservations/<int:pool_id>")
@jwt_required()
def create_reservation(pool_id):
    """ Creates a reservation for the pool you looking at if you are logged in """

    current_user = get_jwt_identity()

    if current_user:

        data=request.json

        reservation = Reservation(
            booked_username=current_user,
            pool_id=pool_id,
            start_date=data['start_date'],
            end_date=data['end_date']
        )

        db.session.add(reservation)
        db.session.commit()

        return (jsonify(reservation=reservation.serialize()), 201)

    return (jsonify({"error": "not authorized"}), 401)


@app.get("/api/reservations/<int:pool_id>")
@jwt_required()
def get_reservations_for_pool(pool_id):
    """ Gets all reservations assocaited with pool_id """

    current_user = get_jwt_identity()

    pool = Pool.query.get_or_404(pool_id)
    if(pool.owner_username==current_user):
        reservations = (Reservation.query
        .filter(pool_id=pool_id)
        .order_by(Reservation.start_date.desc()))

        serialized_reservations = ([reservation.serialize()
            for reservation in reservations])

        return (jsonify(reservations=serialized_reservations))

    #TODO: better error handling for more diverse errors
    return (jsonify({"error": "not authorized"}), 401)


@app.get("/api/reservations/<username>")
@jwt_required()
def get_booked_reservations_for_username(username):
    """ Gets all reservations created by a username """

    current_user = get_jwt_identity()

    user = User.query.get_or_404(username)
    if(user.username==current_user):
        reservations = (Reservation.query
        .filter(username=username)
        .order_by(Reservation.start_date.desc()))

        serialized_reservations = ([reservation.serialize()
            for reservation in reservations])

        return (jsonify(reservations=serialized_reservations))

    #TODO: better error handling for more diverse errors
    return (jsonify({"error": "not authorized"}), 401)


@app.get("/api/reservations/<int:reservation_id>")
@jwt_required()
def get_booked_reservation(reservation_id):
    """ Gets specific reservation """

    current_user = get_jwt_identity()

    reservation = Reservation.get_or_404(reservation_id)
    pool_id = reservation.pool_id
    pool = Pool.get_or_404(pool_id)

    if ((reservation.booked_username == current_user) or
        (pool.owner_username == current_user)):

        serialized_reservation = reservation.serialize()

        return (jsonify(reservation=serialized_reservation), 200)

    #TODO: better error handling for more diverse errors
    return (jsonify({"error": "not authorized"}), 401)


# TODO: delete reservation
@app.delete("/api/reservations/<int:reservation_id>")
@jwt_required()
def delete_booked_reservation(reservation_id):
    """ Deletes a specific reservation if either pool owner or reservation booker """

    current_user = get_jwt_identity()

    reservation = Reservation.get_or_404(reservation_id)
    pool_id = reservation.pool_id
    pool = Pool.get_or_404(pool_id)

    if ((reservation.booked_username == current_user) or
        (pool.owner_username == current_user)):


        db.session.delete(reservation)
        db.session.commit()

        return (jsonify("Reservation successfully deleted"), 200)

    #TODO: better error handling for more diverse errors
    return (jsonify({"error": "not authorized"}), 401)





########################  MESSAGES ENDPOINTS END  ##############################
