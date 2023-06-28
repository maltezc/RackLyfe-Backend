"""test file for listing routes"""
from io import BytesIO

from flask_jwt_extended import create_access_token

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.enums import ListingStatusEnum, RackMountTypeEnum, RackActivityTypeEnum
from mnb_backend.listings.models import Listing
from mnb_backend.listings.tests.setup import ListingBaseViewTestCase
from mnb_backend.users.models import User

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

listings_root = "/api/listings_images"

# arrange
# act
# assert

class CreateListingImageTestCase(ListingBaseViewTestCase):
    # TODO: add_listing_image happy
    def add_listing_image_happy(self):
        pass

    # TODO: add_listing_image sad
    def add_listing_image_sad(self):
        pass


class ReadListingImageTestCase(ListingBaseViewTestCase):
    # TODO: get_all_listing_images happy
    def get_all_listing_images_happy(self):
        pass

    # TODO: get_all_listing_images sad
    def get_all_listing_images_sad(self):
        pass

    # TODO: get_listing_image happy
    def get_listing_image_happy(self):
        pass

    # TODO: get_listing_image sad
    def get_listing_image_sad(self):
        pass


class DeleteListingImageTestCase(ListingBaseViewTestCase):
    # TODO: delete_listing_image happy
    def delete_listing_image_happy(self):
        pass

    # TODO: delete_listing_image sad
    def delete_listing_image_sad(self):
        pass
