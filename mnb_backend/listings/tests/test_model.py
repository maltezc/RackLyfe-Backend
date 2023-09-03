"""File for listings model tests"""

from mnb_backend import app
from mnb_backend.addresses.models import Address
from mnb_backend.listings.models import Listing
from mnb_backend.listings.tests.setup import ListingBaseViewTestCase
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums, PriceEnums, RentalDurationEnum, ListingStatusEnum, RackMountTypeEnum, \
    RackActivityTypeEnum
from mnb_backend.users.models import User
from unittest.mock import patch



from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


class CreateListingTestCase(ListingBaseViewTestCase):
    def test_listing_model_0(self):
        u1 = db.session.get(User, self.u1_id)
        a1 = db.session.get(Address, self.a1_id)

        # User should have no listings
        self.assertEqual(len(u1.listings), 0)

    def test_listing_model_1_listing_created(self):
        with app.app_context():
            u1 = db.session.get(User, self.u1_id)
            a1 = db.session.get(Address, self.a1_id)

            primary_image_url = "https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280"
            title = "Large Cargo basket"
            rack_mount_type = RackMountTypeEnum.ROOF.value
            activity_type = RackActivityTypeEnum.CARGO.value
            rate_price = 2000,

            # Create a listing
            listing1 = Listing.create_listing(
                owner=u1,
                primary_image_url=primary_image_url,
                title=title,
                mount_type=rack_mount_type,
                activity_type=activity_type,
                rate_price=rate_price,
            )

            db.session.add(listing1)
            db.session.commit()

            u1.listings.append(listing1)
            db.session.commit()

            # User should have 1 listing
            self.assertEqual(len(u1.listings), 1)


class GetListingTestCase(ListingBaseViewTestCase):

    @patch("mnb_backend.addresses.models.fuzz_coordinates")
    def test_serialize_listing_object(self, mock_fuzz_coordinates):

        with app.app_context():
            u1 = db.session.get(User, self.u1_id)
            a1 = db.session.get(Address, self.a1_id)

            primary_image_url = "https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3" \
                                "&hl=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280"
            title = "Small Ski Rack"
            rack_mount_type = RackMountTypeEnum.ROOF.value
            activity_type = "skissnowboard"
            # rate_price = 1000,

            # Create a listing
            listing1 = Listing.create_listing(
                owner=u1,
                primary_image_url=primary_image_url,
                title=title,
                mount_type=rack_mount_type,
                activity_type=activity_type,
                rate_price=1500,
                # status=ListingStatusEnum.AVAILABLE,
            )

            mock_fuzz_coordinates.return_value = (-122.28195077277807, 38.006370801958916)

            serialized_listing = listing1.serialize()

            mock_fuzz_coordinates.assert_called_once()

            self.assertEqual(serialized_listing, {
                "id": listing1.id,
                "owner_id": listing1.owner_id,
                "owner": listing1.owner.serialize(),
                "primary_image_url": listing1.primary_image_url,
                "title": listing1.title,
                "mount_type": listing1.mount_type.value,
                "activity_type": listing1.activity_type.value,
                "rate_price": listing1.rate_price,
                "status": listing1.status.value,
                "reservations": []
            })
