"""File for reservations model tests"""
from datetime import datetime, timedelta
from unittest.mock import patch

from flask_bcrypt import Bcrypt

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.listings.models import Listing
from mnb_backend.reservations.models import Reservation
from mnb_backend.reservations.tests.setup import ReservationsBaseViewTestCase
from mnb_backend.users.models import User

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


class CreateReservationTestCase(ReservationsBaseViewTestCase):

    @patch("mnb_backend.addresses.models.fuzz_coordinates")
    def test_create_new_reservation(self, mock_fuzz_coordinates):
        with app.app_context():
            u2 = db.session.get(User, self.u2_id)

            l1 = db.session.get(Listing, self.l1_id)

            mock_fuzz_coordinates.return_value = (-122.28195077277807, 38.006370801958916)

            start_date1 = datetime(2023, 5, 20, 12, 1)
            duration = timedelta(weeks=5)  # double check insomnia if this errors out.

            reservation1 = Reservation.create_new_reservation(start_date1, duration, l1, u2)

            serialized_reservation = reservation1.serialize()

            # mock_fuzz_coordinates.assert_called_once()

            self.assertEqual(len(l1.reservations), 1)
            self.assertEqual(serialized_reservation, {
                "id": reservation1.id,
                "reservation_date_created": reservation1.reservation_date_created,
                "start_date": reservation1.start_date,
                "end_date": reservation1.end_date,
                "status": reservation1.status.value,
                "duration": str(reservation1.duration),
                "total": reservation1.total,
                "cancellation_reason": reservation1.cancellation_reason,
                "listing_owner": l1.owner.serialize(),
                "listing_renter": reservation1.renter.serialize(),
                "listing_id": l1.id,
            })

    @patch("mnb_backend.addresses.models.fuzz_coordinates")
    def test_attempt_reservation_update_happy(self, mock_fuzz_coordinates):
        with app.app_context():
            u1 = db.session.get(User, self.u1_id)
            u2 = db.session.get(User, self.u2_id)
            l1 = db.session.get(Listing, self.l1_id)

            mock_fuzz_coordinates.return_value = (-122.28195077277807, 38.006370801958916)

            start_date1 = datetime(2023, 5, 20, 12, 1)
            duration = timedelta(weeks=6)  # double check insomnia if this errors out.

            reservation1 = Reservation.create_new_reservation(start_date1, duration, l1, u2)

            updated_start_date = datetime(2023, 7, 20, 12, 1)

            updated_reservation = Reservation.attempt_reservation_update(reservation1, updated_start_date, duration)

            serialized_reservation = updated_reservation.serialize()

            # mock_fuzz_coordinates.assert_called_once()

            self.assertEqual(len(l1.reservations), 1)
            self.assertEqual(reservation1.start_date, updated_start_date)
            self.assertEqual(serialized_reservation, {
                "id": reservation1.id,
                "reservation_date_created": reservation1.reservation_date_created,
                "start_date": reservation1.start_date,
                "end_date": reservation1.end_date,
                "status": reservation1.status.value,
                "duration": str(reservation1.duration),
                "total": reservation1.total,
                "cancellation_reason": reservation1.cancellation_reason,
                "listing_owner": l1.owner.serialize(),
                "listing_renter": reservation1.renter.serialize(),
                "listing_id": l1.id,
            })
