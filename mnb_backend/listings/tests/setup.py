"""Setup for User tests"""
from unittest import TestCase

from mnb_backend import app
from mnb_backend.addresses.models import Address, Location, City, State, ZipCode
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums
from mnb_backend.listings.models import Listing
from mnb_backend.users.models import User


class ListingBaseViewTestCase(TestCase):
    def setUp(self):
        """
        Create test client, add sample data."""

        # This order is important
        Listing.query.delete()
        Location.query.delete()
        Address.query.delete()  # This should come before ZipCode
        ZipCode.query.delete()
        City.query.delete()
        User.query.delete()

        db.session.commit()  # Commit after deletion


        # ZipCode.query.delete()
        # City.query.delete()
        # Location.query.delete()
        # Listing.query.delete()
        # Address.query.delete()
        # User.query.delete() # TODO: FAILING HERE. CHECK CASCADE DELETE IN MODELS. NOT SURE WHAT ELSE TO CHECK.

        u1 = User.signup("ua@email.com", "password", "uafirstname", "uafirstname", UserStatusEnums.ACTIVE)
        # u2 = User.signup("ub@email.com", "password", "ubfirstname", "ubfirstname", UserStatusEnums.ACTIVE)
        # u3 = User.signup("uc@email.com", "password", "ucfirstname", "ucfirstname", UserStatusEnums.ACTIVE)
        # u4 = User.signup("ud@email.com", "password", "udfirstname", "udfirstname", UserStatusEnums.ACTIVE)
        # admin1 = User.signup("uAdmin@email.com", "password", "Admin", "Admin", UserStatusEnums.ACTIVE, is_admin=True)

        db.session.add(u1)
        # db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        self.u1_id = u1.id
        # self.u2_id = u2.id
        # self.u3_id = u3.id
        # self.u4_id = u4.id
        # self.uAdmin_id = admin1.id

        # a1 = Address.create_address("1234 Main St", "Apt 1", "San Francisco", "CA", "94122")
        address1 = Address(street_address="164 Glenwood")
        db.session.add(address1)
        address1.user = u1

        location1 = Location(point='POINT(-122.28195023589687 38.006370860286694)')
        db.session.add(location1)
        address1.location = location1

        city1 = City(
            city_name="Hercules",
        )
        db.session.add(city1)

        address1.city = city1

        city1.state = State.query.filter(State.state_abbreviation == "CA").first()

        zipcode1 = ZipCode(code=94547)
        db.session.add(zipcode1)
        address1.zipcode = zipcode1
        db.session.commit()

        self.a1_id = address1.id

        self.client = app.test_client()

    def tearDown(self):
        """
        Rollback any failed session transactions"""
        db.session.rollback()