"""test file for reservation routes"""
from io import BytesIO

from flask_jwt_extended import create_access_token

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.enums import ListingStatusEnum, RackMountTypeEnum, RackActivityTypeEnum
from mnb_backend.listings.models import Listing
from mnb_backend.listings.tests.setup import ListingBaseViewTestCase
from mnb_backend.reservations.tests.setup import ReservationsBaseViewTestCase
from mnb_backend.users.models import User

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

listings_root = "/api/reservations"


class CreateReservationTestCase(ReservationsBaseViewTestCase):
    def test_create_reservation_happy(self):
        pass

    def test_create_reservation_happy(self):
        pass

class ReadReservationTestCase(ReservationsBaseViewTestCase):
    def test_list_all_reservations_happy(self):
        pass

    def test_get_all_upcoming_reservations_for_listing_happy(self):
        pass

    def test_get_all_past_reservations_for_listing_happy(self):
        pass

    def test_get_booked_reservations_for_user_uid_happy(self):
        pass

    def test_get_reservation_happy(self):
        pass


class UpdateReservationTestCase(ReservationsBaseViewTestCase):
    def test_update_reservation_happy(self):
        pass

    def test_cancel_reservation_request_happy(self):
        pass

    def test_accept_reservation_happy(self):
        pass


class DeleteReservationTestCase(ReservationsBaseViewTestCase):
    def test_decline_reservation_happy(self):
        pass
