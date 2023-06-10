"""test file for listing routes"""
from io import BytesIO

from flask_jwt_extended import create_access_token

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.listings.tests.setup import ListingBaseViewTestCase
from mnb_backend.users.models import User


# TODO: create_listing
class CreateListingTestCase(ListingBaseViewTestCase):
    def test_create_listing_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)

        access_token = create_access_token(identity=u1.id)

        # create a test image file
        test_image = BytesIO(b"test image data")
        test_image.name = "test_image.jpg"
        # data = {"profile_image": test_image}
        json_data = {
            "title": "testTitle",
            "author": "testAuthor",
            "isbn": 9780756405892,
            # "condition":"",
            "rate_price": 400,
            "image1": test_image,
            # "image2":ListingStatusEnum.AVAILABLE,
        }

        with app.test_client() as client:
            # Act
            response = client.post("/api/listings/", headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            # Assert
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(u1.listings), 1)
            self.assertEqual(response.json['user']['firstname'], 'John')

    # def test_create_listing_sad(self):


# TODO: get_listings_of_current_user
class GetListingOfCurrentUserTestCase():
    pass


# TODO: get_specific_listing
class GetSpecificListingTestCase(ListingBaseViewTestCase):
    pass


# TODO: get_listings_of_specific_user
class GetListingOfSpecificUser(ListingBaseViewTestCase):
    pass


# TODO: update_listing
class UpdateListingTestCase(ListingBaseViewTestCase):
    pass


# TODO: toggle_listing_status
class ToggleListingStatus(ListingBaseViewTestCase):
    pass


# TODO: delete_listing
class DeleteListingTestCase(ListingBaseViewTestCase):
    pass
