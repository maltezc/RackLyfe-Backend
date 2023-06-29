"""test file for listing routes"""
from io import BytesIO
from unittest.mock import patch
from mnb_backend.api_helpers import aws_upload_image
from flask_jwt_extended import create_access_token

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.listings.models import Listing
from mnb_backend.listing_images.tests.setup import ListingImagesBaseViewTestCase
from mnb_backend.users.models import User

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

listing_images_root = "/api/listing_images"


# /api/listing_images


# arrange
# act
# assert

class CreateListingImageTestCase(ListingImagesBaseViewTestCase):
    # @patch("mnb_backend.api_helpers.aws_upload_image")
    def test_add_listing_image_happy(self):
        # def test_add_listing_image_happy(self, mock_upload_to_aws):
        """Tests adding a listing image and verifies that it is created successfully."""
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        with app.test_client() as client:
            # Create a test image file
            test_image = BytesIO(b"test image data")
            test_image.name = "test_image.jpg"

            json_data = {"image1": test_image}

            listing_images_url = f"/api/listing_images/listing/{l1.id}"

            # Set the return value for the mocked function
            # mock_upload_to_aws.return_value = "mocked_url"

            # Mock the Image.open() method to avoid opening the image file
            with patch("mnb_backend.api_helpers.Image.open"):
                response = client.post(listing_images_url, headers={"Authorization": f"Bearer {access_token}"}, data=json_data)

            # Assert
            self.assertEqual(response.status_code, 201)
            self.assertEqual(len(u1.listings[0].images), 1)
            # TODO: ADD MOCKING FUNCTIONALITY. CHECK WITH @LUCAS?
            # mock_upload_to_aws.assert_called_once()

    # TODO: add_listing_image sad
    def test_add_listing_image_sad(self):
        pass
        # arrange
        # act
        # assert


class ReadListingImageTestCase(ListingImagesBaseViewTestCase):
    # TODO: get_all_listing_images happy
    def test_get_all_listing_images_happy(self):
        pass
        # arrange
        # act
        # assert

    # TODO: get_all_listing_images sad
    def test_get_all_listing_images_sad(self):
        pass
        # arrange
        # act
        # assert

    # TODO: get_listing_image happy
    def test_get_listing_image_happy(self):
        pass
        # arrange
        # act
        # assert

    # TODO: get_listing_image sad
    def test_get_listing_image_sad(self):
        pass
        # arrange
        # act
        # assert


class DeleteListingImageTestCase(ListingImagesBaseViewTestCase):
    # TODO: delete_listing_image happy
    def test_delete_listing_image_happy(self):
        pass
        # arrange
        # act
        # assert

    # TODO: delete_listing_image sad
    def test_delete_listing_image_sad(self):
        pass
        # arrange
        # act
        # assert
