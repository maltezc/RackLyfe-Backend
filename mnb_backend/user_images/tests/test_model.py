# Generated by CodiumAI

from unittest import TestCase

from mnb_backend.enums import UserStatusEnums
from mnb_backend.user_images.tests.setup import UserModelTestCase
from mnb_backend.users.models import User
from mnb_backend.user_images.models import UserImage
from mnb_backend.database import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

"""
Code Analysis

Main functionalities:
The UserImage class is a model that represents the connection between a user and their profile image. It stores the user's ID, the image URL, and provides a method to serialize the object. It also has a relationship with the User class, allowing for easy access to the user's profile image.

Methods:
- serialize(): returns a dictionary representation of the object
- __repr__(): returns a string representation of the object for debugging purposes

Fields:
- id: integer, primary key
- user_id: integer, foreign key to the users table
- user: relationship to the User class, back_populates to the profile_image attribute
- image_url: text, the URL of the user's profile image
"""


class TestUserImage(UserModelTestCase):
    """Tests creating a UserImage object with valid inputs."""

    def test_create_user_image_valid_inputs(self):
        """Tests creating a UserImage object with valid inputs."""

        # Arrange
        u1 = db.session.get(User, self.u1_id)

        # Act
        user_image = UserImage(user_id=u1.id, image_url="https://example.com/image.jpg")
        db.session.add(user_image)
        db.session.commit()

        # Assert
        self.assertEqual(user_image.user_id, u1.id)
        self.assertEqual(user_image.image_url, "https://example.com/image.jpg")

    #  Tests serializing a UserImage object.
    def test_serialize_user_image(self):
        """Tests serializing a UserImage object."""

        # Arrange
        u1 = db.session.get(User, self.u1_id)

        user_image = UserImage(user_id=u1.id, image_url="https://example.com/image.jpg")
        db.session.add(user_image)
        db.session.commit()

        # Act
        serialized_user_image = user_image.serialize()

        # Assert
        self.assertEqual(serialized_user_image["id"], user_image.id)
        self.assertEqual(serialized_user_image["image_url"], "https://example.com/image.jpg")
        self.assertEqual(serialized_user_image["user_id"], u1.id)

    #  Tests deleting a UserImage object from the database.
    def test_delete_user_image(self):
        """Tests deleting a UserImage object from the database."""

        # Arrange
        # user = User(id=1, name="John")
        # db.session.add(user)
        # db.session.commit()
        u1 = db.session.get(User, self.u1_id)

        user_image = UserImage(user_id=u1.id, image_url="https://example.com/image.jpg")
        db.session.add(user_image)
        db.session.commit()

        # Act
        db.session.delete(user_image)
        db.session.commit()

        # Assert
        self.assertIsNone(db.session.get(UserImage, user_image.id))
