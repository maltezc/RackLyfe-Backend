"""Test case for user routes"""
# FLASK_DEBUG=test python3 -m unittest discover -s mnb_backend/users/tests -k class
# EXAMPLE: FLASK_DEBUG=test python3 -m unittest discover -s mnb_backend/users/tests -k UpdateSpecificUserTestCase

from unittest import TestCase

from flask_jwt_extended import create_access_token

from mnb_backend import app
from mnb_backend.users.models import User
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        """
        Create test client, add sample data."""
        User.query.delete()

        u1 = User.signup("u1@email.com", "password", "u1firstname", "u1firstname", UserStatusEnums.ACTIVE)
        u2 = User.signup("u2@email.com", "password", "u2firstname", "u2firstname", UserStatusEnums.ACTIVE)
        u3 = User.signup("u3@email.com", "password", "u3firstname", "u3firstname", UserStatusEnums.ACTIVE)
        u4 = User.signup("u4@email.com", "password", "u4firstname", "u4firstname", UserStatusEnums.ACTIVE)

        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
        self.u4_id = u4.id

        self.client = app.test_client()

    def tearDown(self):
        """
        Rollback any failed session transactions"""
        db.session.rollback()


class UserListShowTestCase(UserBaseViewTestCase):
    def test_list_users_returns_correct_json(self):
        with app.test_client() as client:
            response = client.get('/api/users/')
            data = response.get_json()

            self.assertIsInstance(data, dict)
            self.assertIn('users', data)
            self.assertIsInstance(data['users'], list)
            self.assertTrue(all(isinstance(user, dict) for user in data['users']))
            self.assertTrue(all(key in user for user in data['users'] for key in
                                ['id', 'status', 'email', 'firstname', 'lastname', 'is_admin', 'image_url',
                                 'preferred_trade_location', 'user_rating', 'user_image', 'address']))

    def test_list_users_returns_status_code_200(self):
        with app.test_client() as client:
            response = client.get('/api/users/')
            self.assertEqual(response.status_code, 200)

    def test_list_users_no_users_exist(self):
        with app.test_client() as client:
            db.session.query(User).delete()
            db.session.commit()

            response = client.get('/api/users/')
            data = response.get_json()

            self.assertIsInstance(data, dict)
            self.assertIn('users', data)
            self.assertIsInstance(data['users'], list)
            self.assertEqual(len(data['users']), 0)

    def test_list_users_large_number_of_users(self):
        with app.test_client() as client:
            db.session.query(User).delete()
            db.session.commit()

            for i in range(10):
                User.signup(f'user{i}@example.com', 'password', f'firstname{i}', f'lastname{i}', UserStatusEnums.ACTIVE)

            response = client.get('/api/users/')
            data = response.get_json()

            self.assertIsInstance(data, dict)
            self.assertIn('users', data)
            self.assertIsInstance(data['users'], list)
            self.assertEqual(len(data['users']), 10)


class ShowSpecificUserTestCase(UserBaseViewTestCase):

    def test_show_user_happy_path(self):
        """Tests that a valid user is successfully retrieved and serialized."""

        with app.test_client() as client:
            # Create a test user
            test_user = User.signup(
                email="test@test.com",
                password="password",
                firstname="Test",
                lastname="User",
                status=UserStatusEnums.ACTIVE
            )

            # Make request to show_user endpoint
            response = client.get(f"api/users/{test_user.id}")

            # Check that response is successful and contains expected fields
            self.assertEqual(response.status_code, 200)
            self.assertIn("user", response.json)
            self.assertIn("email", response.json["user"])
            self.assertIn("image_url", response.json["user"])
            self.assertIn("firstname", response.json["user"])
            self.assertIn("lastname", response.json["user"])
            self.assertIn("address", response.json["user"])
            # self.assertIn("owned_books", response.json["user"])
            # self.assertIn("reservations", response.json["user"])

    def test_show_user_edge_case_1(self):
        """Tests that a 404 error is returned when the user does not exist in the database."""

        with app.test_client() as client:
            # Make request to show_user endpoint with invalid user id
            response = client.get("/api/users/999")

            # Check that response is a 404 error
            self.assertEqual(response.status_code, 404)

    def test_show_user_edge_case_2(self):
        """Tests that a 404 error is returned when an invalid user_uid input is provided."""

        with app.test_client() as client:
            # Make request to show_user endpoint with invalid input
            response = client.get("/api/users/invalid_input")

            # Check that response is a 404 error
            self.assertEqual(response.status_code, 404)

    def test_show_user_behavior_1(self):
        """Tests that the returned JSON contains all expected fields."""

        with app.test_client() as client:
            # Create a test user
            test_user = User.signup(
                email="test@test.com",
                password="password",
                firstname="Test",
                lastname="User",
                status=UserStatusEnums.ACTIVE
            )

            # Make request to show_user endpoint
            response = client.get(f"/api/users/{test_user.id}")

            # Check that response contains all expected fields
            self.assertIn("user", response.json)
            self.assertIn("email", response.json["user"])
            self.assertIn("image_url", response.json["user"])
            self.assertIn("firstname", response.json["user"])
            self.assertIn("lastname", response.json["user"])
            self.assertIn("address", response.json["user"])
            # self.assertIn("owned_books", response.json["user"])
            # self.assertIn("reservations", response.json["user"])

    def test_show_user_behavior_2(self):
        """Tests that the serialized user object contains all expected fields."""

        with app.test_client() as client:
            # Create a test user
            test_user = User.signup(
                email="test@test.com",
                password="password",
                firstname="Test",
                lastname="User",
                status=UserStatusEnums.ACTIVE
            )

            # Make request to show_user endpoint
            response = client.get(f"/api/users/{test_user.id}")

            # Check that serialized user object contains all expected fields
            self.assertIn("id", response.json["user"])
            self.assertIn("status", response.json["user"])
            self.assertIn("email", response.json["user"])
            self.assertIn("firstname", response.json["user"])
            self.assertIn("lastname", response.json["user"])
            self.assertIn("is_admin", response.json["user"])
            self.assertIn("image_url", response.json["user"])
            self.assertIn("preferred_trade_location", response.json["user"])
            self.assertIn("user_rating", response.json["user"])
            self.assertIn("user_image", response.json["user"])
            self.assertIn("address", response.json["user"])

    def test_show_user_behavior_3(self):
        """Tests that the HTTP status code is correct (200 for successful response, 404 for error)."""

        with app.test_client() as client:
            # Create a test user
            test_user = User.signup(
                email="test@test.com",
                password="password",
                firstname="Test",
                lastname="User",
                status=UserStatusEnums.ACTIVE
            )

            # Make request to show_user endpoint with valid user id
            response = client.get(f"/api/users/{test_user.id}")

            # Check that response is a successful response (200)
            self.assertEqual(response.status_code, 200)

            # Make request to show_user endpoint with invalid user id
            response = client.get("/api/users/999")

            # Check that response is a 404 error
            self.assertEqual(response.status_code, 404)


class UpdateSpecificUserTestCase(UserBaseViewTestCase):

    def test_update_user_authenticated_and_authorized(self):
        with app.test_client() as client:
            # create a user
            user = User.signup(
                email='test@test.com',
                password='password',
                firstname='Test',
                lastname='User',
                status=UserStatusEnums.ACTIVE
            )
            db.session.commit()

            # authenticate the user
            access_token = create_access_token(identity=user.id)

            # update the user's information
            data = {
                'firstname': 'John',
                'lastname': 'Doe'
            }
            response = client.patch(f'/api/users/{user.id}', json=data,
                                    headers={'Authorization': f'Bearer {access_token}'})

            # check that the response is successful and the user information has been updated
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['user']['firstname'], 'John')
            self.assertEqual(response.json['user']['lastname'], 'Doe')

#     TODO: add tests for the update path route and continue with the rest

    def test_update_user_not_authenticated(self):
        with app.test_client() as client:
            # create a user
            user = User.signup(
                email='test@test.com',
                password='password',
                firstname='Test',
                lastname='User',
                status=UserStatusEnums.ACTIVE
            )
            db.session.commit()

            # attempt to update the user's information without authentication
            data = {
                'firstname': 'John',
                'lastname': 'Doe'
            }
            response = client.patch(f'/api/users/{user.id}', json=data)

            # check that the response is an error message and the user information has not been updated
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json['msg'], 'Missing Authorization Header')

    def test_update_user_not_authorized(self):
        with app.test_client() as client:
            # create two users
            user1 = User.signup(
                email='test1@test.com',
                password='password',
                firstname='Test',
                lastname='User',
                status=UserStatusEnums.ACTIVE
            )
            user2 = User.signup(
                email='test2@test.com',
                password='password',
                firstname='Test',
                lastname='User',
                status=UserStatusEnums.ACTIVE
            )
            db.session.commit()

            # authenticate user1
            access_token = create_access_token(identity=user1.id)

            # attempt to update user2's information
            data = {
                'firstname': 'John',
                'lastname': 'Doe'
            }
            response = client.patch(f'api/users/{user2.id}', json=data,
                                    headers={'Authorization': f'Bearer {access_token}'})

            # check that the response is an error message and the user information has not been updated
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json['error'], 'not authorized')

    def test_update_user_invalid_data(self):
        with app.test_client() as client:
            # create a user
            user = User.signup(
                email='test@test.com',
                password='password',
                firstname='Test',
                lastname='User',
                status=UserStatusEnums.ACTIVE
            )
            db.session.commit()

            # authenticate the user
            access_token = create_access_token(identity=user.id)

            # attempt to update the user's information with invalid data
            data = {
                'firstname': 1234,
                'lastname': 'Doe'
            }
            response = client.patch(f'/api/users/{user.id}', json=data, headers={'Authorization': f'Bearer {access_token}'})

            breakpoint()
            # check that the response is an error message and the user information has not been updated
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json['error'], 'Invalid data provided')