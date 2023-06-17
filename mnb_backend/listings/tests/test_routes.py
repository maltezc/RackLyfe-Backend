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

listings_root = "/api/listings"


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
            "title": "Large Roof Cargo Basket",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            # "condition":"",
            "rate_price": 2000,
            "image1": test_image,
            # "image2":ListingStatusEnum.AVAILABLE,
        }

        with app.test_client() as client:
            # Act
            response = client.post(f"{listings_root}/", headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            # Assert
            self.assertEqual(response.status_code, 201)
            self.assertEqual(len(u1.listings), 1)


class GetSpecificListingOfCurrentUserTestCase(ListingBaseViewTestCase):
    def test_get_specific_listing_happy(self):
        u1 = db.session.get(User, self.u1_id)
        access_token = create_access_token(identity=u1.id)

        # Create a test listing for the user
        listing_data = {
            "title": "testTitle",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 400,
            # "status": ListingStatusEnum.AVAILABLE

        }
        listing = Listing.create_listing(owner=u1, **listing_data)

        with app.test_client() as client:
            # Act
            response = client.get(f"{listings_root}/{listing.id}", headers={"Authorization": f"Bearer {access_token}"})
            data = response.get_json()

            # Assert
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(data, dict)
            self.assertEqual(len(data), 1)
            self.assertEqual(data["listing"]["id"], listing.id)
            self.assertEqual(data["listing"]["title"], listing_data["title"])


class GetListingsOfCurrentUserTestCase(ListingBaseViewTestCase):
    def test_get_listings_of_current_user_happy(self):
        u1 = db.session.get(User, self.u1_id)
        access_token = create_access_token(identity=u1.id)

        # Create a test listing for the user
        listing_data = {
            "title": "testTitle1",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 1000,
        }
        listing1 = Listing.create_listing(owner=u1, **listing_data)

        listing_data = {
            "title": "testTitle2",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 400,


        }
        listing2 = Listing.create_listing(owner=u1, **listing_data)

        with app.test_client() as client:
            # Act
            response = client.get(f"{listings_root}/current", headers={"Authorization": f"Bearer {access_token}"})
            data = response.get_json()

            self.assertEqual(len(u1.listings), 2)
            self.assertEqual(len(data['listings']), 2)


class GetListingOfSpecificUser(ListingBaseViewTestCase):
    def test_get_listings_of_specific_user_happy(self):
        u1 = db.session.get(User, self.u1_id)
        access_token = create_access_token(identity=u1.id)

        # Create a test listing for the user
        listing_data = {
            "title": "testTitle1",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 400,
        }
        listing1 = Listing.create_listing(owner=u1, **listing_data)

        listing_data = {
            "title": "testTitle2",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 400,
        }
        listing2 = Listing.create_listing(owner=u1, **listing_data)

        with app.test_client() as client:
            # Act
            response = client.get(f"{listings_root}/user/{u1.id}")
            data = response.get_json()
            self.assertEqual(len(data['listings']), 2)
            self.assertEqual(data["listings"][0]["owner_id"], u1.id)
            self.assertEqual(data["listings"][1]["owner_id"], u1.id)


class UpdateListingTestCase(ListingBaseViewTestCase):
    def test_update_listing_happy(self):
        u1 = db.session.get(User, self.u1_id)
        access_token = create_access_token(identity=u1.id)

        # Create a test listing for the user
        listing_data = {
            "title": "testTitle1",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 1000,
        }
        listing1 = Listing.create_listing(owner=u1, **listing_data)

        # create a test image file
        test_image = BytesIO(b"test image data")
        test_image.name = "test_image.jpg"

        json_data = {
            "title": "updatedTitle",
            "mount_type": RackMountTypeEnum.HITCH.value,
            "activity_type": RackActivityTypeEnum.BICYCLE.value,
        }
        # TODO: COME BACK AND UPDATE AFTER MODELS CHANGE TO ROOFRACK

        with app.test_client() as client:
            response = client.patch(f"{listings_root}/{listing1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    json=json_data)

            self.assertEqual(response.status_code, 200)


class ToggleListingStatus(ListingBaseViewTestCase):
    def test_toggle_listing_status_happy(self):
        u1 = db.session.get(User, self.u1_id)
        access_token = create_access_token(identity=u1.id)

        # Create a test listing for the user
        listing_data = {
            "title": "testTitle1",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 400,
        }
        listing1 = Listing.create_listing(owner=u1, **listing_data)
        listing_original_status = listing1.status

        with app.test_client() as client:
            response = client.patch(f"{listings_root}/toggle_status/{listing1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"})

            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            updated_status_value = data["listing"]["status"]
            self.assertEqual(updated_status_value, ListingStatusEnum.UNAVAILABLE.value)


class DeleteListingTestCase(ListingBaseViewTestCase):
    def test_delete_listing_happy(self):
        u1 = db.session.get(User, self.u1_id)
        access_token = create_access_token(identity=u1.id)

        # Create a test listing for the user
        listing_data = {
            "title": "testTitle1",
            "mount_type": RackMountTypeEnum.ROOF.value,
            "activity_type": RackActivityTypeEnum.SKISSNOWBOARD.value,
            "rate_price": 400,
        }
        listing1 = Listing.create_listing(owner=u1, **listing_data)

        with app.test_client() as client:
            response_delete = client.delete(f"{listings_root}/{listing1.id}",
                                            headers={"Authorization": f"Bearer {access_token}"})

            data_delete = response_delete.get_json()

            response_current_user_listings = client.get(f"{listings_root}/current",
                                                        headers={"Authorization": f"Bearer {access_token}"})
            data_get_current = response_current_user_listings.get_json()

            self.assertEqual(response_delete.status_code, 200)
            self.assertEqual(len(data_get_current["listings"]), 0)
