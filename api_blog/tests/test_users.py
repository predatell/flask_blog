import unittest
import json
from ..app import create_app
from ..models import db


class UsersTest(unittest.TestCase):
    """Users Test Case"""

    def setUp(self):
        """Test Setup"""
        self.app = create_app("test")
        self.client = self.app.test_client
        self.user_data = {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test_test'
        }
        self.headers = {'Content-Type': 'application/json'}

        # with self.app.app_context():
        #     # create all tables
        #     db.create_all()

    def test_user_create(self):
        """Test: create user with valid credentials"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        data = json.loads(response.data)
        self.assertTrue(data.get('jwt_token'))
        self.assertEqual(response.status_code, 201)

    def test_user_create_with_existing_email(self):
        """Test: create user with existing email"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        user_data = {
            'username': 'test2',
            'email': 'test@test.com',
            'password': 'test_test'
        }
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(user_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('error'))

    def test_user_create_with_existing_username(self):
        """Test: create user with existing username"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        user_data = {
            'username': 'test',
            'email': 'another@test.com',
            'password': 'test_test'
        }
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(user_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('error'))

    def test_user_create_with_no_data(self):
        """Test create user with no data"""
        user = {}
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(user))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(data.get('error'))

    def test_user_create_with_no_password(self):
        """Test create user with no password"""
        user = {
            'username': 'test',
            'email': 'test@test.com',
        }
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(user))
        data = json.loads(response.data)
        print(data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('error', {}).get('password'))

    def test_user_create_with_no_email(self):
        """Test create user with no email"""
        user = {
            'username': 'test',
            'password': 'test23424',
        }
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(user))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('error', {}).get('email'))

    def test_user_login(self):
        """ User Login Tests """
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        response = self.client().post('/users/login', headers=self.headers, data=json.dumps(self.user_data))
        data = json.loads(response.data)
        self.assertTrue(data.get('jwt_token'))
        self.assertEqual(response.status_code, 200)

    def test_user_login_with_invalid_password(self):
        """ User Login Tests with invalid credentials """
        user1 = {
            'password': 'test',
            'email': 'test@test.com',
        }
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        response = self.client().post('/users/login', headers=self.headers, data=json.dumps(user1))
        data = json.loads(response.data)
        self.assertFalse(data.get('jwt_token'))
        self.assertEqual(data.get('error'), 'Invalid credentials')
        self.assertEqual(response.status_code, 400)

    def test_user_login_with_invalid_email(self):
        """User Login Tests with invalid credentials"""
        user1 = {
            'password': 'test12',
            'email': 'test@test.com',
        }
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        response = self.client().post('/users/login', headers=self.headers, data=json.dumps(user1))
        data = json.loads(response.data)
        self.assertFalse(data.get('jwt_token'))
        self.assertEqual(data.get('error'), 'Invalid credentials')
        self.assertEqual(response.status_code, 400)

    def test_user_get_me(self):
        """Test" Get info about my user"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        api_token = json.loads(response.data).get('jwt_token')
        response = self.client().get('/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('email'), 'test@test.com')
        self.assertEqual(data.get('username'), 'test')

    def test_user_get_not_existing(self):
        """Test" Get not existing user"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        api_token = json.loads(response.data).get('jwt_token')
        response = self.client().get('/users/5', headers={'Content-Type': 'application/json', 'api-token': api_token})
        self.assertEqual(response.status_code, 404)

    def test_user_get_all(self):
        """Test" Get the list of users"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        api_token = json.loads(response.data).get('jwt_token')
        response = self.client().get('/users/', headers={'Content-Type': 'application/json', 'api-token': api_token})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get('data')), 1)

    def tearDown(self):
        """
        Tear Down
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
