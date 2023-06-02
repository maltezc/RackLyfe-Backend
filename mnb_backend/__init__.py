import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from mnb_backend.database import connect_db
from mnb_backend.config import DevelopmentConfig, TestConfig, ProductionConfig

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
app = Flask(__name__)

# breakpoint()
if os.environ.get('FLASK_DEBUG') == 'test':
    app.config.from_object(TestConfig)
# elif os.environ.get('FLASK_ENV') == 'prod':
#     app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
CORS(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

# Setting up jwt
app.config["JWT_SECRET_KEY"] = os.environ['SECRET_KEY']
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_IDENTITY_CLAIM"] = "user_uid"

connect_db(app)


# Register Blueprints
# TODO: ADD REVIEWS ROUTES
# TODO: SET UP ROUTES TO HANDLE UPDATED url_prefix UPDATE FOR ALL ROUTES
app.register_blueprint(auth_routes, url_prefix='/api/auth')
app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(user_images_routes, url_prefix='/api/user_images')
app.register_blueprint(addresses_routes, url_prefix='/api/addresses')
app.register_blueprint(listings_routes, url_prefix='/api/listings')
app.register_blueprint(listing_images_routes, url_prefix='/api/listing_images')
app.register_blueprint(reservations_routes, url_prefix='/api/reservations')
app.register_blueprint(messages_routes, url_prefix='/api/messages')
app.register_blueprint(searches_routes, url_prefix='/api/searches')
