"""test file for listing routes"""
from io import BytesIO
from unittest.mock import patch
from mnb_backend.api_helpers import aws_upload_image
from flask_jwt_extended import create_access_token

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.listings.models import Listing
from mnb_backend.listing_images.tests.setup import ListingImagesBaseViewTestCase
# from mnb_backend.listing_images.routes import
from mnb_backend.users.models import User

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

listing_images_root = "/api/listing_images"


# arrange
# act
# assert

class CreateListingImageTestCase(ListingImagesBaseViewTestCase):
    @patch("mnb_backend.listing_images.routes.aws_upload_image")
    def test_add_listing_image_happy(self, mock_upload_to_aws):
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
            mock_upload_to_aws.return_value = "mocked_url"

            response = client.post(listing_images_url, headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            # Assert
            self.assertEqual(response.status_code, 201)
            self.assertEqual(len(u1.listings[0].images), 1)
            mock_upload_to_aws.assert_called_once()

    def test_add_listing_image_user_didnt_upload_files(self):
        """Tests failes when creating an image without an image."""

        # Arrange
        u1 = db.session.get(User, self.u1_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        with app.test_client() as client:
            # Create a test image file
            test_image = BytesIO(b"test image data")
            test_image.name = "test_image.jpg"

            json_data = {}

            listing_images_url = f"/api/listing_images/listing/{l1.id}"

            response = client.post(listing_images_url, headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            # Assert
            self.assertEqual(response.status_code, 400)
            self.assertEqual(len(u1.listings[0].images), 0)

    def test_add_listing_image_incorrect_file_type(self):
        """Tests adding a listing image fails when trying to upload an incorrect file type."""
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        with app.test_client() as client:
            # Create a test image file
            test_image = BytesIO(b"test image data")
            test_image.name = "test_image.pdf"

            json_data = {"image1": test_image}

            listing_images_url = f"/api/listing_images/listing/{l1.id}"

            response = client.post(listing_images_url, headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            # Assert
            self.assertEqual(response.status_code, 400)
            self.assertEqual(len(u1.listings[0].images), 0)


class ReadListingImageTestCase(ListingImagesBaseViewTestCase):
    @patch("mnb_backend.listing_images.routes.aws_upload_image")
    def test_get_all_listing_images_happy(self, mock_upload_to_aws):
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
            mock_upload_to_aws.return_value = "mocked_url"

            response = client.post(listing_images_url, headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            response_get = client.get(f"/api/listing_images/")

            data = response_get.json

            # Assert
            self.assertEqual(response_get.status_code, 200)
            self.assertIn('listing_images', data)
            self.assertEqual(len(data["listing_images"]), 1)

    def test_get_all_listing_images_sad(self):
        # TODO: get_all_listing_images sad
        pass
        # arrange
        # act
        # assert

    @patch("mnb_backend.listing_images.routes.aws_upload_image")
    def test_get_specific_listing_image_happy(self, mock_upload_to_aws):
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
            mock_upload_to_aws.return_value = "mocked_url"

            response = client.post(listing_images_url, headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            response_get = client.get(f"/api/listing_images/{l1.images[0].id}")

            data = response_get.json
            # Assert
            self.assertEqual(response_get.status_code, 200)
            self.assertIn('listing_image', data)
            self.assertIn("id", data["listing_image"])
            self.assertIn("image_url", data["listing_image"])
            self.assertIn("listing_id", data["listing_image"])

    # TODO: get_listing_image sad
    def test_get_listing_image_sad(self):
        pass
        # arrange
        # act
        # assert


class DeleteListingImageTestCase(ListingImagesBaseViewTestCase):
    @patch("mnb_backend.listing_images.routes.aws_upload_image")
    def test_delete_listing_image_happy(self, mock_upload_to_aws):

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
            mock_upload_to_aws.return_value = "mocked_url"

            response = client.post(listing_images_url, headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            response_delete = client.delete(f"/api/listing_images/{l1.images[0].id}",
                                            headers={"Authorization": f"Bearer {access_token}"})

            data = response_delete.json

            # Assert
            self.assertEqual(response_delete.status_code, 200)
            self.assertIn('Listing Image successfully deleted', data)
            self.assertEqual(len(u1.listings[0].images), 0)


    # TODO: delete_listing_image sad
    def test_delete_listing_image_sad(self):
        pass
        # arrange
        # act
        # assert
