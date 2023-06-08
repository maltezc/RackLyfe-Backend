"""Test case for user routes"""
# FLASK_DEBUG=test python3 -m unittest discover -s mnb_backend/users/tests -k class
# EXAMPLE: FLASK_DEBUG=test python3 -m unittest discover -s mnb_backend/users/tests -k UpdateSpecificUserTestCase

import string

from flask_jwt_extended import create_access_token

# os.environ['FLASK_DEBUG'] = 'test'
from mnb_backend import app
from mnb_backend.database import db
from mnb_backend.enums import UserStatusEnums
from mnb_backend.users.models import User
from mnb_backend.users.tests.setup import UserBaseViewTestCase


class UserCreateTestCase(UserBaseViewTestCase):
    def test_create_user_returns_correct_json(self):
        with app.test_client() as client:
            response = client.post('/api/users/signup', data=dict(
                email='johndoe@email.com',
                password='password',
                firstname='TestA',
                lastname='UserA',
            ))

            data = response.get_json()

            self.assertIsInstance(data, dict)
            self.assertIn('user', data)
            self.assertIsInstance(data['user'], dict)
            self.assertTrue(all(key in data['user'] for key in
                                ['id', 'status', 'email', 'firstname', 'lastname', 'is_admin', 'image_url',
                                 'preferred_trade_location', 'user_rating', 'user_image', 'address']))

    def test_create_user_duplicate_email_returns_400(self):
        with app.test_client() as client:
            u1 = db.session.get(User, self.u1_id)

            response = client.post('/api/users/signup', data=dict(
                email=u1.email,
                password='password',
                firstname='TestA',
                lastname='UserA',
            ))

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], 'Email already taken')

    def test_create_user_returns_status_code_201(self):
        with app.test_client() as client:
            response = client.post('/api/users/signup', data=dict(
                email="JohnDoe@email.com",
                password='password',
                firstname='TestA',
                lastname='UserA',
            ))

            self.assertEqual(response.status_code, 201)


class UserCreateAdminTestCase(UserBaseViewTestCase):
    def test_create_admin_returns_correct_json(self):
        with app.test_client() as client:
            # create a test user
            admin1 = db.session.get(User, self.uAdmin_id)

            # log in as the test user
            access_token = create_access_token(identity=admin1.id)

            response = client.post('/api/users/signup_admin', headers={"Authorization": f"Bearer {access_token}"},
                                   data=dict(
                                       email="admin2@email.com",
                                       password='password',
                                       firstname='TestA',
                                       lastname='UserA',
                                   ))

            data = response.get_json()

            self.assertIsInstance(data, dict)
            self.assertIn('user', data)
            self.assertEqual(data['user']['is_admin'], True)
            self.assertIsInstance(data['user'], dict)
            self.assertTrue(all(key in data['user'] for key in
                                ['id', 'status', 'email', 'firstname', 'lastname', 'is_admin', 'image_url',
                                 'preferred_trade_location', 'user_rating', 'user_image', 'address']))

    def test_create_admin_returns_status_code_201(self):
        with app.test_client() as client:
            # create a test user
            admin1 = db.session.get(User, self.uAdmin_id)

            # log in as the test user
            access_token = create_access_token(identity=admin1.id)

            response = client.post('/api/users/signup_admin', headers={"Authorization": f"Bearer {access_token}"},
                                   data=dict(
                                       email="JohnDoeAdmin@email.com",
                                       password='password',
                                       firstname='TestA',
                                       lastname='UserA',
                                   ))

            data = response.get_json()

            self.assertEqual(response.status_code, 201)

    def test_create_admin_returns_status_code_401(self):
        with app.test_client() as client:
            # create a test user
            admin1 = db.session.get(User, self.u1_id)

            # log in as the test user
            access_token = create_access_token(identity=admin1.id)

            response = client.post('/api/users/signup_admin', headers={"Authorization": f"Bearer {access_token}"},
                                   data=dict(
                                       email="JohnDoeAdmin@email.com",
                                       password='password',
                                       firstname='TestA',
                                       lastname='UserA',
                                   ))

            data = response.get_json()

            self.assertEqual(response.status_code, 403)


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

            # for c in ascii_lowercase:

            for i in string.ascii_lowercase[:10]:
                # for i in range(10):
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
            response = client.patch(f'/api/users/{user.id}', json=data,
                                    headers={'Authorization': f'Bearer {access_token}'})

            # check that the response is an error message and the user information has not been updated
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json['error'], 'invalid firstname')


class DeleteSpecificUserTestCase(UserBaseViewTestCase):

    #  Tests that a user can be deleted when authorized.
    def test_delete_user_happy_path(self):
        """Test that a user can be deleted when authorized"""

        # Create a user to be deleted
        user = User.signup('test@test.com', 'password', 'Test', 'User', UserStatusEnums.ACTIVE)
        db.session.add(user)
        db.session.commit()

        # Login as the user to be deleted
        access_token = create_access_token(identity=user.id)

        # Delete the user
        response = self.client.delete(f'/api/users/{user.id}', headers={'Authorization': f'Bearer {access_token}'})

        # Check that the user was deleted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, "User successfully deleted")

    #  Tests that an admin can delete any user.
    def test_delete_user_admin(self):
        """Test that an admin can delete any user"""

        # Create an admin user
        admin = User.signup('admin@test.com', 'password', 'Admin', 'User', UserStatusEnums.ACTIVE, is_admin=True)
        db.session.add(admin)
        db.session.commit()

        # Create a user to be deleted
        user = User.signup('test@test.com', 'password', 'Test', 'User', UserStatusEnums.ACTIVE)
        db.session.add(user)
        db.session.commit()

        # Login as the admin
        access_token = create_access_token(identity=admin.id)

        # Delete the user
        response = self.client.delete(f'/api/users/{user.id}', headers={'Authorization': f'Bearer {access_token}'})

        # Check that the user was deleted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, "User successfully deleted")

    #  Tests that an error message is returned when the user ID does not exist.
    def test_delete_user_nonexistent_id(self):
        """Test that an error message is returned when the user ID does not exist"""

        # Create an admin user
        admin = User.signup('admin@test.com', 'password', 'Admin', 'User', UserStatusEnums.ACTIVE, is_admin=True)
        db.session.add(admin)
        db.session.commit()

        # Login as the admin
        access_token = create_access_token(identity=admin.id)

        # Delete a nonexistent user
        response = self.client.delete('/api/users/999', headers={'Authorization': f'Bearer {access_token}'})

        # Check that an error message is returned
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "User not found"})

    #  Tests that an error message is returned when the user is not authorized to delete the user.
    def test_delete_user_unauthorized(self):
        """Test that an error message is returned when the user is not authorized to delete the user"""

        # Create a user to be deleted
        user = User.signup('test@test.com', 'password', 'Test', 'User', UserStatusEnums.ACTIVE)
        db.session.add(user)
        db.session.commit()

        # Create another user who is not authorized to delete the first user
        other_user = User.signup('other@test.com', 'password', 'Other', 'User', UserStatusEnums.ACTIVE)
        db.session.add(other_user)
        db.session.commit()

        # Login as the other user
        access_token = create_access_token(identity=other_user.id)

        # Try to delete the first user
        response = self.client.delete(f'/api/users/{user.id}', headers={'Authorization': f'Bearer {access_token}'})

        # Check that an error message is returned
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error": "not authorized"})

    #  Tests deleting a user when there are multiple users in the database.
    def test_delete_user_multiple_users(self):
        """Test deleting a user when there are multiple users in the database"""

        # Create an admin user
        admin = User.signup('admin@test.com', 'password', 'Admin', 'User', UserStatusEnums.ACTIVE, is_admin=True)
        db.session.add(admin)
        db.session.commit()

        # Create multiple users to be deleted
        user1 = User.signup('test1@test.com', 'password', 'Test', 'UserA', UserStatusEnums.ACTIVE)
        user2 = User.signup('test2@test.com', 'password', 'Test', 'UserB', UserStatusEnums.ACTIVE)
        db.session.add_all([user1, user2])
        db.session.commit()

        # Login as the admin
        access_token = create_access_token(identity=admin.id)

        # Delete the users
        response1 = self.client.delete(f'/api/users/{user1.id}', headers={'Authorization': f'Bearer {access_token}'})
        response2 = self.client.delete(f'/api/users/{user2.id}', headers={'Authorization': f'Bearer {access_token}'})

        # Check that the users were deleted
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.json, "User successfully deleted")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json, "User successfully deleted")


class DeactivateSpecificUserTestCase(UserBaseViewTestCase):
    # Generated by CodiumAI

    def test_toggle_user_status_auth_success(self):
        # Happy path test
        with app.test_client() as client:
            # Create a user
            user = User.signup(
                email="test@test.com",
                password="password",
                firstname="John",
                lastname="Doe",
                status=UserStatusEnums.ACTIVE
            )
            db.session.add(user)
            db.session.commit()

            # Authenticate the user
            access_token = create_access_token(identity=user.id)

            # Toggle the user's status
            response = client.patch(f"/api/users/{user.id}/toggle_status",
                                    headers={"Authorization": f"Bearer {access_token}"})

            # Check that the response is successful and the user's status has been toggled
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["user"]["status"], "Inactive")

    #  Tests that a user cannot toggle another user's status when authenticated.
    def test_toggle_user_status_auth_fail(self):
        # Edge case test: user cannot toggle another user's status
        with app.test_client() as client:
            # Create two users
            user1 = User.signup(
                email="test1@test.com",
                password="password",
                firstname="John",
                lastname="Doe",
                status=UserStatusEnums.ACTIVE
            )
            user2 = User.signup(
                email="test2@test.com",
                password="password",
                firstname="Jane",
                lastname="Doe",
                status=UserStatusEnums.ACTIVE
            )
            db.session.add_all([user1, user2])
            db.session.commit()

            # Authenticate user1
            access_token = create_access_token(identity=user1.id)

            # Try to toggle user2's status
            response = client.patch(f"/api/users/{user2.id}/toggle_status",
                                    headers={"Authorization": f"Bearer {access_token}"})

            # Check that the response is unauthorized and the user's status has not been toggled
            self.assertEqual(response.status_code, 401)
            self.assertEqual(user2.status, UserStatusEnums.ACTIVE)

    #  Tests that an error message is returned when a user that does not exist in the database is provided.
    def test_toggle_user_status_user_not_exist(self):
        # Edge case test: error message returned when user does not exist
        with app.test_client() as client:
            # Authenticate a user
            access_token = create_access_token(identity=1)

            # Try to toggle a non-existent user's status
            response = client.patch("/api/users/999/toggle_status",
                                    headers={"Authorization": f"Bearer {access_token}"})

            # Check that the response is not found and no changes have been made to the database
            self.assertEqual(response.status_code, 404)
            self.assertEqual(User.query.filter_by(status=UserStatusEnums.INACTIVE).count(), 0)

    #  Tests that the database is updated correctly when a user's status is toggled.
    def test_toggle_user_status_database_changes(self):
        # General behavior test: database is updated correctly when user's status is toggled
        with app.test_client() as client:
            # Create a user
            user = User.signup(
                email="test@test.com",
                password="password",
                firstname="John",
                lastname="Doe",
                status=UserStatusEnums.ACTIVE
            )
            db.session.add(user)
            db.session.commit()

            # Authenticate the user
            access_token = create_access_token(identity=user.id)

            # Toggle the user's status
            response = client.patch(f"/api/users/{user.id}/toggle_status",
                                    headers={"Authorization": f"Bearer {access_token}"})

            # Check that the response is successful and the database has been updated correctly
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.filter_by(status=UserStatusEnums.INACTIVE).count(), 1)

    #  Tests that an error message is returned when a user is not authenticated.
    def test_toggle_user_status_not_authenticated(self):
        # Edge case test: error message returned when user is not authenticated
        with app.test_client() as client:
            # Create a user
            user = User.signup(
                email="test@test.com",
                password="password",
                firstname="John",
                lastname="Doe",
                status=UserStatusEnums.ACTIVE
            )
            db.session.add(user)
            db.session.commit()

            # Try to toggle the user's status without authentication
            response = client.patch(f"/api/users/{user.id}/toggle_status")

            # Check that the response is unauthorized and the user's status has not been changed
            self.assertEqual(response.status_code, 401)
            self.assertEqual(user.status, UserStatusEnums.ACTIVE)
