"""File for model tests"""

from mnb_backend import app
from mnb_backend.addresses.models import Address
from mnb_backend.listings.models import Listing
from mnb_backend.listings.tests.setup import ListingBaseViewTestCase
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums, PriceEnums, RentalDurationEnum, ListingStatusEnum
from mnb_backend.errors import EmailAlreadyExistsError
from mnb_backend.users.models import User


class CreateListingTestCase(ListingBaseViewTestCase):
    def test_listing_model_0(self):
        u1 = db.session.get(User, self.u1_id)
        a1 = db.session.get(Address, self.a1_id)

        # User should have no listings
        self.assertEqual(len(u1.listings), 0)

    def test_listing_model_1(self):
        with app.app_context():
            u1 = db.session.get(User, self.u1_id)
            a1 = db.session.get(Address, self.a1_id)

            # Create a listing
            listing1 = Listing(
                owner=u1,
                primary_image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
                title="The Name of the Wind",
                author="Patrick Rothfuss",
                isbn=9780756405892,
                genre="",
                rate_price=PriceEnums.FOUR,
                rate_schedule=RentalDurationEnum.WEEKLY,
                status=ListingStatusEnum.AVAILABLE,
            )
            db.session.add(listing1)
            db.session.commit()

            u1.listings.append(listing1)
            db.session.commit()

            # User should have 1 listing
            self.assertEqual(len(u1.listings), 1)



