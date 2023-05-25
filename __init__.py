import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from database import connect_db, db

from mnb_backend.auth.routes import auth_routes
from mnb_backend.users.routes import user_routes
from mnb_backend.user_images.routes import user_images_routes

from mnb_backend.addresses.routes import addresses_routes

from mnb_backend.listings.routes import listings_routes
from mnb_backend.listing_images.routes import listing_images_routes
from mnb_backend.reservations.routes import reservations_routes

from mnb_backend.messages.routes import messages_routes
from mnb_backend.searches.routes import searches_routes


# TODO: CREATE REVIEWS ROUTES / MODELS


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

connect_db(app)
db.create_all()

app.register_blueprint(auth_routes)
app.register_blueprint(user_routes)
app.register_blueprint(user_images_routes)
app.register_blueprint(addresses_routes)
app.register_blueprint(listings_routes)
app.register_blueprint(listing_images_routes)
app.register_blueprint(reservations_routes)
app.register_blueprint(messages_routes)
app.register_blueprint(searches_routes)
