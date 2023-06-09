"""Setup for User tests"""
from unittest import TestCase

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums
from mnb_backend.users.models import User


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        """
        Create test client, add sample data."""
        User.query.delete()

        u1 = User.signup("ua@email.com", "password", "uafirstname", "uafirstname", UserStatusEnums.ACTIVE)
        u2 = User.signup("ub@email.com", "password", "ubfirstname", "ubfirstname", UserStatusEnums.ACTIVE)
        u3 = User.signup("uc@email.com", "password", "ucfirstname", "ucfirstname", UserStatusEnums.ACTIVE)
        u4 = User.signup("ud@email.com", "password", "udfirstname", "udfirstname", UserStatusEnums.ACTIVE)
        admin1 = User.signup("uAdmin@email.com", "password", "Admin", "Admin", UserStatusEnums.ACTIVE, is_admin=True)

        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
        self.u4_id = u4.id
        self.uAdmin_id = admin1.id

        self.client = app.test_client()

    def tearDown(self):
        """
        Rollback any failed session transactions"""
        db.session.rollback()