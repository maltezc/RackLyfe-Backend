"""File for reservations model tests"""

from mnb_backend import app
from mnb_backend.addresses.models import Address
from mnb_backend.listing_images.models import ListingImage
from mnb_backend.listings.models import Listing
from mnb_backend.reservations.tests.setup import ReservationsBaseViewTestCase
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums, PriceEnums, RentalDurationEnum, ListingStatusEnum, RackMountTypeEnum, \
    RackActivityTypeEnum
from mnb_backend.users.models import User

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


class CreateReservationTestCase(ReservationsBaseViewTestCase):
    def test_create_new_reservation(self):
        pass

    def test_attempt_reservation_update(self):
        pass

    def test_reservation_model_serialize_happy(self):
        pass
