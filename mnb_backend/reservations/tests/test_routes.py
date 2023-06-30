"""test file for reservation routes"""
from datetime import datetime, timedelta
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
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        json_data = {
            "start_date": "2023-8-1",
            "duration": 5,
            "renter": u2.id
        }

        with app.test_client() as client:
            response = client.post(f"/api/reservations/{l1.id}",
                                   headers={"Authorization": f"Bearer {access_token}"},
                                   data=json_data)

            # Assert
            self.assertEqual(response.status_code, 201)
            self.assertEqual(len(l1.reservations), 1)


class ReadReservationTestCase(ReservationsBaseViewTestCase):
    def test_list_all_reservations_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        json_data1 = {
            "start_date": "2023-8-1",
            "duration": 5,
            "renter": u2.id
        }

        json_data2 = {
            "start_date": "2023-9-1",
            "duration": 10,
            "renter": u2.id
        }

        with app.test_client() as client:
            response1 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data1)

            response2 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data2)

            # Assert
            self.assertEqual(response1.status_code, 201)
            self.assertEqual(response2.status_code, 201)
            self.assertEqual(len(l1.reservations), 2)

    def test_get_all_upcoming_reservations_for_listing_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        today = datetime.utcnow()
        days = timedelta(days=5)
        future_date = today.date() + days

        json_data = {
            "start_date": str(future_date),
            "duration": 5,
            "renter": u2.id
        }

        json_data1 = {
            "start_date": "2023-8-1",
            "duration": 5,
            "renter": u2.id
        }

        json_data2 = {
            "start_date": "2023-9-1",
            "duration": 10,
            "renter": u2.id
        }

        json_data3 = {
            "start_date": "2022-9-1",
            "duration": 10,
            "renter": u2.id
        }

        with app.test_client() as client:
            response1 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data1)

            response2 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data2)

            response3 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data3)

            response = client.get(f"/api/reservations/{l1.id}/upcoming",
                                  headers={"Authorization": f"Bearer {access_token}"},
                                  data=json_data)
            data = response.get_json()

            # Assert
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data["reservations"]), 2)
            self.assertEqual(len(l1.reservations), 3)

    def test_get_all_past_reservations_for_listing_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        today = datetime.utcnow()
        days = timedelta(days=5)
        future_date = today.date() + days

        json_data = {
            "start_date": str(future_date),
            "duration": 5,
            "renter": u2.id
        }

        json_data1 = {
            "start_date": "2023-8-1",
            "duration": 5,
            "renter": u2.id
        }

        json_data2 = {
            "start_date": "2023-9-1",
            "duration": 10,
            "renter": u2.id
        }

        json_data3 = {
            "start_date": "2022-9-1",
            "duration": 10,
            "renter": u2.id
        }

        with app.test_client() as client:
            response1 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data1)

            response2 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data2)

            response3 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data3)

            response = client.get(f"/api/reservations/{l1.id}/past",
                                  headers={"Authorization": f"Bearer {access_token}"},
                                  data=json_data)
            data = response.get_json()

            # Assert
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data["reservations"]), 1)
            self.assertEqual(len(l1.reservations), 3)

    def test_get_booked_reservations_for_user_uid_happy(self):
        pass
        # Arrange
        # u1 = db.session.get(User, self.u1_id)
        # u2 = db.session.get(User, self.u2_id)
        # l1 = db.session.get(Listing, self.l1_id)
        #
        # # Act
        # access_token = create_access_token(identity=u1.id)
        #
        # today = datetime.utcnow()
        # days = timedelta(days=5)
        # future_date = today.date() + days
        #
        # json_data = {
        #     "start_date": str(future_date),
        #     "duration": 5,
        #     "renter": u2.id
        # }
        #
        # json_data1 = {
        #     "start_date": "2023-8-1",
        #     "duration": 5,
        #     "renter": u2.id
        # }
        #
        # json_data2 = {
        #     "start_date": "2023-9-1",
        #     "duration": 10,
        #     "renter": u2.id
        # }
        #
        # json_data3 = {
        #     "start_date": "2022-9-1",
        #     "duration": 10,
        #     "renter": u2.id
        # }
        #
        # with app.test_client() as client:
        #     response1 = client.post(f"/api/reservations/{l1.id}",
        #                             headers={"Authorization": f"Bearer {access_token}"},
        #                             data=json_data1)
        #
        #     response2 = client.post(f"/api/reservations/{l1.id}",
        #                             headers={"Authorization": f"Bearer {access_token}"},
        #                             data=json_data2)
        #
        #     response3 = client.post(f"/api/reservations/{l1.id}",
        #                             headers={"Authorization": f"Bearer {access_token}"},
        #                             data=json_data3)
        #
        #     response = client.get(f"/api/reservations/user/{u1.id}",
        #                           headers={"Authorization": f"Bearer {access_token}"},
        #                           data=json_data)
        #     data = response.get_json()
        #
        #     # Assert
        #     self.assertEqual(response.status_code, 200)
        #     self.assertEqual(len(data["reservations"]), 3)
        #     self.assertEqual(len(u1.listings.reservations), 3)

    def test_get_reservation_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        json_data1 = {
            "start_date": "2023-8-1",
            "duration": 5,
            "renter": u2.id
        }

        with app.test_client() as client:
            response1 = client.post(f"/api/reservations/{l1.id}",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    data=json_data1)

            data = response1.get_json()
            response1_id = data["reservation"]["id"]

            response = client.get(f"/api/reservations/{response1_id}",
                                  headers={"Authorization": f"Bearer {access_token}"})

            # Assert
            self.assertEqual(response1.status_code, 201)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(l1.reservations), 1)


class UpdateReservationTestCase(ReservationsBaseViewTestCase):
    def test_update_reservation_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u2.id)

        today = datetime.utcnow()
        days = timedelta(days=5)
        future_date = today.date() + days

        json_data1 = {
            "start_date": future_date,
            "duration": 5,
            "renter": u2.id
        }

        patch_data1 = {
            "start_date": future_date,
            "duration": 6,
        }

        with app.test_client() as client:
            post_response = client.post(f"/api/reservations/{l1.id}",
                                        headers={"Authorization": f"Bearer {access_token}"},
                                        data=json_data1)

            data = post_response.get_json()
            response1_id = data["reservation"]["id"]

            patch_response = client.patch(f"/api/reservations/{response1_id}",
                                          headers={"Authorization": f"Bearer {access_token}"},
                                          data=patch_data1)

            data = patch_response.get_json()

            # Assert
            days = data["reservation"]["duration"]

            self.assertEqual(days, '6 days, 0:00:00')

    def test_cancel_reservation_request_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u2.id)

        today = datetime.utcnow()
        days = timedelta(days=5)
        future_date = today.date() + days

        json_data1 = {
            "start_date": future_date,
            "duration": 5,
            "renter": u2.id
        }

        patch_data1 = {
            "cancellation_reason": "Something came up."
        }

        with app.test_client() as client:
            post_response = client.post(f"/api/reservations/{l1.id}",
                                        headers={"Authorization": f"Bearer {access_token}"},
                                        data=json_data1)

            data = post_response.get_json()
            response1_id = data["reservation"]["id"]

            patch_response = client.patch(f"/api/reservations/{response1_id}/cancel",
                                          headers={"Authorization": f"Bearer {access_token}"},
                                          data=patch_data1)

            data = patch_response.get_json()

            # Assert
            self.assertEqual(data["reservation"]["status"], "Cancelled")

    def test_accept_reservation_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        today = datetime.utcnow()
        days = timedelta(days=5)
        future_date = today.date() + days

        json_data1 = {
            "start_date": future_date,
            "duration": 5,
            "renter": u2.id
        }

        with app.test_client() as client:
            post_response = client.post(f"/api/reservations/{l1.id}",
                                        headers={"Authorization": f"Bearer {access_token}"},
                                        data=json_data1)

            data = post_response.get_json()
            response1_id = data["reservation"]["id"]

            patch_response = client.patch(f"/api/reservations/{response1_id}/accept",
                                          headers={"Authorization": f"Bearer {access_token}"})

            data = patch_response.get_json()

            # Assert
            self.assertEqual(data["reservation"]["status"], "Accepted")


class DeleteReservationTestCase(ReservationsBaseViewTestCase):
    def test_decline_reservation_happy(self):
        # Arrange
        u1 = db.session.get(User, self.u1_id)
        u2 = db.session.get(User, self.u2_id)
        l1 = db.session.get(Listing, self.l1_id)

        # Act
        access_token = create_access_token(identity=u1.id)

        today = datetime.utcnow()
        days = timedelta(days=5)
        future_date = today.date() + days

        json_data1 = {
            "start_date": future_date,
            "duration": 5,
            "renter": u2.id
        }

        with app.test_client() as client:
            post_response = client.post(f"/api/reservations/{l1.id}",
                                        headers={"Authorization": f"Bearer {access_token}"},
                                        data=json_data1)

            data = post_response.get_json()
            response1_id = data["reservation"]["id"]

            patch_response = client.patch(f"/api/reservations/{response1_id}/decline",
                                          headers={"Authorization": f"Bearer {access_token}"})

            data = patch_response.get_json()

            # Assert
            self.assertEqual(data["reservation"]["status"], "Declined")
