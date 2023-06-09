"""User model tests."""
from sqlalchemy.exc import IntegrityError

# run these tests like:
#
# FLASK_ENV=test python3 -m unittest discover -v


from mnb_backend import app
from mnb_backend.auth.tests.setup import UserModelTestCase
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums
from mnb_backend.errors import EmailAlreadyExistsError
from mnb_backend.users.models import User


# instantiate Bcrypt to create hashed passwords for test data


class UserAuthAndSignupTestCase(UserModelTestCase):
    def test_user_model(self):
        u1 = db.session.get(User, self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.sent_messages), 0)
        self.assertEqual(len(u1.received_messages), 0)

    def test_valid_signup(self):
        u3 = User.signup("uC@email.com", "password", "uCfirstname", "uClastname", UserStatusEnums.ACTIVE)

        # self.assertEqual(u3.username, "u3")
        self.assertEqual(u3.email, "uC@email.com")
        self.assertNotEqual(u3.password, "password")
        self.assertEqual(u3.firstname, "uCfirstname")
        self.assertEqual(u3.lastname, "uClastname")
        self.assertEqual(u3.status, UserStatusEnums.ACTIVE)
        # Bcrypt strings should start with $2b$
        self.assertTrue(u3.password.startswith("$2b$"))

    def test_signup_duplicate_email(self):
        # Create the first user
        user1 = User.signup('test@test.com', 'password', 'Test', 'User', UserStatusEnums.ACTIVE)

        # Attempt to create a second user with the same email
        with self.assertRaises(EmailAlreadyExistsError):
            User.signup('test@test.com', 'password2', 'TestB', 'UserB', UserStatusEnums.ACTIVE)

            # Ensure that only one user was added to the database
            users = User.query.all()
            self.assertEqual(len(users), 1)

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

    def test_serialize_user_object_missing_related_objects(self): # TODO: REMOVE THIS TEST. ITS REDUNDANT
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

    # TODO: MOVE BELOW TESTS TO AUTHENTICATION FOLDER
    # #################### Authentication Tests

    def test_valid_authentication(self):
        u1 = db.session.get(User, self.u1_id)

        u = User.authenticate("uA@email.com", "password")
        self.assertEqual(u, u1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("bad-username", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate("uA@email.com", "bad-password"))
