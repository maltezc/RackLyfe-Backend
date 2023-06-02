"""User model tests."""

# run these tests like:
#
# FLASK_ENV=test python3 -m unittest discover -v


import os

from mnb_backend.enums import UserStatusEnums

from sqlalchemy.exc import IntegrityError
from mnb_backend import app

from unittest import TestCase
from flask_bcrypt import Bcrypt

from mnb_backend.database import db
from mnb_backend.users.models import User

# instantiate Bcrypt to create hashed passwords for test data
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
            firstname="u2Firstname",
            lastname="u2Lastname",
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

    def test_user_model(self):
        u1 = db.session.get(User, self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.sent_messages), 0)
        self.assertEqual(len(u1.received_messages), 0)

    def test_valid_signup(self):
        u3 = User.signup("u3@email.com", "password", "u3firstname", "u3lastname", UserStatusEnums.ACTIVE)

        # self.assertEqual(u3.username, "u3")
        self.assertEqual(u3.email, "u3@email.com")
        self.assertNotEqual(u3.password, "password")
        self.assertEqual(u3.firstname, "u3firstname")
        self.assertEqual(u3.lastname, "u3lastname")
        self.assertEqual(u3.status, UserStatusEnums.ACTIVE)
        # Bcrypt strings should start with $2b$
        self.assertTrue(u3.password.startswith("$2b$"))

    def test_invalid_signup(self):
        # Assert that user signup raises an integrity error when we make a user
        # with the same email

        with self.assertRaises(IntegrityError):
            User.signup("u1@email.com", "password", "u1FirstName", "u1lastname", UserStatusEnums.ACTIVE)
            db.session.commit()

    def test_serialize_user_object(self):
        """Test serializing a user object to JSON format"""

        # Arrange
        email = "testuser@example.com"
        password = "password123"
        firstname = "Test"
        lastname = "User"
        status = UserStatusEnums.ACTIVE

        user = User.signup(email, password, firstname, lastname, status)

        # Act
        serialized_user = user.serialize()

        # Assert
        expected_output = {
            "id": user.id,
            "status": status.value,
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "is_admin": False,
            "image_url": None,
            "preferred_trade_location": None,
            "user_rating": 5.0,
            "user_image": None,
            "address": None
        }
        self.assertEqual(serialized_user, expected_output)

    def test_serialize_user_object_missing_related_objects(self):
        """Test serializing a user object with missing related objects"""

        # Arrange
        email = "testuser@example.com"
        password = "password123"
        firstname = "Test"
        lastname = "User"
        status = UserStatusEnums.ACTIVE

        user = User.signup(email, password, firstname, lastname, status)

        # Act
        serialized_user = user.serialize()

        # Assert
        self.assertIsNone(serialized_user["address"])
        self.assertIsNone(serialized_user["user_image"])

    # #################### Authentication Tests

    def test_valid_authentication(self):
        u1 = db.session.get(User, self.u1_id)

        u = User.authenticate("u1@email.com", "password")
        self.assertEqual(u, u1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("bad-username", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate("u1@email.com", "bad-password"))
