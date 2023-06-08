"""File for test setup"""
from unittest import TestCase

from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums
from mnb_backend.user_images.models import UserImage
from mnb_backend.users.models import User
from mnb_backend import app

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """File for test setup"""

    def setUp(self):
        """
        Create test client, add sample data."""

        UserImage.query.delete()
        User.query.delete()

        hashed_password = (bcrypt
                           .generate_password_hash("password")
                           .decode('UTF-8')
                           )

        u1 = User(
            email="u1@email.com",
            password=hashed_password,
            firstname="testFirstname",
            lastname="testLastname",
            status=UserStatusEnums.ACTIVE,

            # image_url=None,
        )

        u2 = User(
            email="u2@email.com",
            password=hashed_password,
            firstname="testSecondname",
            lastname="testSecondLastname",
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