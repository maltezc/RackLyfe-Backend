"""Setup for User tests"""
from unittest import TestCase
from unittest.mock import patch

from mnb_backend import app
from mnb_backend.addresses.models import Address, Location, City, State, ZipCode
from mnb_backend.addresses.states import states
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums, RackMountTypeEnum, RackActivityTypeEnum
from mnb_backend.listings.models import Listing
from mnb_backend.reservations.models import Reservation
from mnb_backend.users.models import User
from mnb_backend.test_setup_helpers import delete_all_tables


class ReservationsBaseViewTestCase(TestCase):

    def setUp(self):
        """
        Create test client, add sample data."""

        delete_all_tables(self)


        # Insert all states into the database
        for state_data in states:
            state = State(state_name=state_data['name'], state_abbreviation=state_data['abbreviation'])
            db.session.add(state)

        u1 = User.signup("ua@email.com", "password", "uafirstname", "uafirstname", "I am a test user",
                         UserStatusEnums.ACTIVE)
        u2 = User.signup("ub@email.com", "password", "ubfirstname", "ubfirstname", "I am a test user",
                         UserStatusEnums.ACTIVE)
        # u3 = User.signup("uc@email.com", "password", "ucfirstname", "ucfirstname", UserStatusEnums.ACTIVE)
        # u4 = User.signup("ud@email.com", "password", "udfirstname", "udfirstname", UserStatusEnums.ACTIVE)
        # admin1 = User.signup("uAdmin@email.com", "password", "Admin", "Admin", UserStatusEnums.ACTIVE, is_admin=True)

        # db.session.add(u1)
        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        # self.u3_id = u3.id
        # self.u4_id = u4.id
        # self.uAdmin_id = admin1.id

        # a1 = Address.create_address("1234 Main St", "Apt 1", "San Francisco", "CA", "94122")
        address1 = Address(street_address="164 Glenwood")
        address2 = Address(street_address="100 Finch Court")
        db.session.add_all([address1, address2])
        address1.user = u1
        address2.user = u2

        location1 = Location(point='POINT(-122.28195023589687 38.006370860286694)')
        location2 = Location(point='POINT(-122.25820007861707 37.99945603355348)')
        db.session.add_all([location1, location2])
        address1.location = location1
        address2.location = location2

        city1 = City(
            city_name="Hercules",
        )
        db.session.add(city1)

        address1.city = city1
        address2.city = city1

        city1.state = State.query.filter(State.state_abbreviation == "CA").first()

        zipcode1 = ZipCode(code=94547)
        db.session.add(zipcode1)
        address1.zipcode = zipcode1
        address2.zipcode = zipcode1
        db.session.commit()

        self.a1_id = address1.id
        self.a2_id = address2.id
        # owner, title, activity_type, mount_type, rate_price,

        primary_image_url = "https://books.google.com/books/publisher/content?id=5y6JEAAAQBAJ&pg=PP1&img=1&zoom=3&hl=en&bul=1&sig=ACfU3U0tX540c49AVK3fB3P75wrNGyzlNg&w=1280"
        title = "Large Cargo basket"
        rack_mount_type = RackMountTypeEnum.ROOF.value
        activity_type = RackActivityTypeEnum.CARGO.value
        rate_price = 2000,

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

        self.l1_id = listing1.id

        self.client = app.test_client()

    def tearDown(self):
        """
        Rollback any failed session transactions"""
        db.session.rollback()
