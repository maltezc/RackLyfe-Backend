"""File for listing images model tests"""

from mnb_backend import app
from mnb_backend.addresses.models import Address
from mnb_backend.listing_images.models import ListingImage
from mnb_backend.listings.models import Listing
from mnb_backend.listing_images.tests.setup import ListingImagesBaseViewTestCase
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums, PriceEnums, RentalDurationEnum, ListingStatusEnum, RackMountTypeEnum, \
    RackActivityTypeEnum
from mnb_backend.users.models import User

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


class CreateListingImageTestCase(ListingImagesBaseViewTestCase):
    def test_listing_image_model_1(self):
        u1 = db.session.get(User, self.u1_id)
        a1 = db.session.get(Address, self.a1_id)
        l1 = db.session.get(Listing, self.l1_id)

        # User should have no listings
        self.assertEqual(len(u1.listings), 1)

    def test_listing_image_created_happy(self):
        with app.app_context():
            u1 = db.session.get(User, self.u1_id)
            a1 = db.session.get(Address, self.a1_id)
            l1 = db.session.get(Listing, self.l1_id)

            listing_image1 = ListingImage(
                image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
                          "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
            )

            db.session.add(listing_image1)
            db.session.commit()

            l1.images.append(listing_image1)

            db.session.commit()

            # User should have 1 listing
            self.assertEqual(len(u1.listings), 1)
            self.assertEqual(len(ListingImage.query.all()), 1)


class GetListingImageTestCase(ListingImagesBaseViewTestCase):
    def test_serialize_listing_object(self):
        with app.app_context():
            u1 = db.session.get(User, self.u1_id)
            a1 = db.session.get(Address, self.a1_id)
            l1 = db.session.get(Listing, self.l1_id)

            listing_image1 = ListingImage(
                image_url="https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl"
                          "=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280",
            )

            db.session.add(listing_image1)
            db.session.commit()

            l1.images.append(listing_image1)

            db.session.commit()

            serialized_listing_image = listing_image1.serialize()

            self.assertEqual(serialized_listing_image, {
                "id": listing_image1.id,
                "listing_id": listing_image1.listing.id,
                "image_url": listing_image1.image_url
            })
