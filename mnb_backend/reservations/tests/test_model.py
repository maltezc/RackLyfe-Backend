"""File for reservations model tests"""
from datetime import datetime, timedelta

from mnb_backend import app
from mnb_backend.addresses.models import Address
from mnb_backend.listing_images.models import ListingImage
from mnb_backend.listings.models import Listing
from mnb_backend.reservations.models import Reservation
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
        with app.app_context():
            u1 = db.session.get(User, self.u1_id)

            l1 = db.session.get(Listing, self.l1_id)

            # primary_image_url = "https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3" \
            #                     "&hl=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280"
            # title = "Small Ski Rack"
            # rack_mount_type = RackMountTypeEnum.ROOF.value
            # activity_type = RackActivityTypeEnum.SKISSNOWBOARD.value
            # rate_price = 1000,

            start_date1 = datetime(2023, 5, 20, 12, 1)
            timedelta1 = timedelta(weeks=5) # double check insomnia if this errors out.
            # total1 = listing1.rate_price * (timedelta1.days / 7)

            # TODO: ERRORS OUT HERE
            reservation1 = Reservation.create_new_reservation(start_date1, timedelta1, l1, u1)
            # reservation1 = Reservation(
            #     # id="1",
            #     reservation_date_created=datetime.utcnow(),
            #     start_date=start_date1,
            #     duration=timedelta1,
            #     end_date=start_date1 + timedelta1,
            #     status=ReservationStatusEnum.ACCEPTED,
            #     total=total1,
            # )

            # Create a listing
            # listing1 = Listing.create_listing(
            #     owner=u1_id,
            #     primary_image_url=primary_image_url,
            #     title=title,
            #     mount_type=rack_mount_type,
            #     activity_type=activity_type,
            #     rate_price=1500,
            #     # rate_schedule=RentalDurationEnum.WEEKLY,
            #     # status=ListingStatusEnum.AVAILABLE,
            # )

            serialized_listing = reservation1.serialize()

            # self.assertEqual(serialized_listing, {
            #     "id": listing1.id,
            #     "owner_id": listing1.owner_id,
            #     "owner": listing1.owner.serialize(),
            #     "primary_image_url": listing1.primary_image_url,
            #     "title": listing1.title,
            #     "mount_type": listing1.mount_type.value,
            #     "activity_type": listing1.activity_type.value,
            #     "rate_price": listing1.rate_price,
            #     # "rate_schedule": listing1.rate_schedule.value,
            #     "status": listing1.status.value,
            #     "reservations": []
            # })

    def test_attempt_reservation_update(self):
        pass

    def test_reservation_model_serialize_happy(self):
        pass
