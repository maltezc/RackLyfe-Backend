from unittest import TestCase

from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums
from mnb_backend.users.models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        """
        Create test client, add sample data."""

        User.query.delete()

        hashed_password = (bcrypt
                           .generate_password_hash("password")
                           .decode('UTF-8')
                           )

        u1 = User(
            email="uA@email.com",
            password=hashed_password,
            firstname="uAFirstname",
            lastname="uALastname",
            status=UserStatusEnums.ACTIVE,

            # image_url=None,
        )

        u2 = User(
            email="uB@email.com",
            password=hashed_password,
            firstname="uBFirstname",
            lastname="uBLastname",
            status=UserStatusEnums.ACTIVE,
            # image_url=None,
        )

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()
