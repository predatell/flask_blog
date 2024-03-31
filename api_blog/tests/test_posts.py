import unittest
import json
from ..app import create_app
from ..models import db


class PostsTest(unittest.TestCase):
    """Posts Test Case"""

    def setUp(self):
        self.app = create_app("test")
        self.client = self.app.test_client
        self.user_data = {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test_test'
        }
        self.post_data = {
            'title': 'My first post',
            'content': 'This is my first post',
        }
        self.comment_data = {
            'content': 'My comment',
            'post_id': 1,
        }
        self.headers = {'Content-Type': 'application/json'}

        # with self.app.app_context():
        #     db.create_all()

    def test_blog_create_without_credentials(self):
        """Test: create post without credentials"""
        response = self.client().post('/posts/', headers=self.headers, data=json.dumps(self.post_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('error'))
        self.assertEqual(data.get('error'), "Authentication token is not available, please login")

    def test_blog_create(self):
        """Test: create post"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        api_token = json.loads(response.data).get('jwt_token')
        headers = {'Content-Type': 'application/json', 'api-token': api_token}
        response = self.client().post('/posts/', headers=headers, data=json.dumps(self.post_data))
        self.assertEqual(response.status_code, 201)
        return api_token

    def test_blog_create_without_content(self):
        """Test: create post without content"""
        response = self.client().post('/users/', headers=self.headers, data=json.dumps(self.user_data))
        self.assertEqual(response.status_code, 201)
        api_token = json.loads(response.data).get('jwt_token')
        headers = {'Content-Type': 'application/json', 'api-token': api_token}
        post_data = {
            'title': 'My second post',
        }
        response = self.client().post('/posts/', headers=headers, data=json.dumps(post_data))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(data.get('error'))
        self.assertTrue(data.get('error').get("content"))

    def test_blog_one(self):
        """Test: get one post"""
        self.test_blog_create()
        response = self.client().get('/posts/1', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('title'), 'My first post')

    def test_blog_patch(self):
        """Test: update blog post"""
        api_token = self.test_blog_create()
        response = self.client().get('/posts/1', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('title'), 'My first post')

        # Check without token
        new_title = 'Changed title'
        post_data = {'title': new_title}
        response = self.client().patch('/posts/1', headers=self.headers, data=json.dumps(post_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('error'))

        # Check with token
        headers = {'Content-Type': 'application/json', 'api-token': api_token}
        response = self.client().patch('/posts/1', headers=headers, data=json.dumps(post_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('title'), new_title)

    def test_blog_list(self):
        """Test: get the list of posts"""
        self.test_blog_create()
        response = self.client().get('/posts/', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get("data")), 1)

    def test_blog_list_paginate(self):
        """Test: get the list of posts"""
        api_token = self.test_blog_create()
        # Create new item
        headers = {'Content-Type': 'application/json', 'api-token': api_token}
        response = self.client().post('/posts/', headers=headers, data=json.dumps(self.post_data))
        self.assertEqual(response.status_code, 201)

        # Check the count of items
        response = self.client().get('/posts/', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get("data")), 2)

        # Check pagination
        response = self.client().get('/posts/?per_page=1', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get("data")), 1)
        self.assertTrue(data.get('next'))

    def test_comment_create(self):
        """Test: create comment for post"""
        api_token = self.test_blog_create()
        headers = {'Content-Type': 'application/json', 'api-token': api_token}
        response = self.client().post('/comments/', headers=headers, data=json.dumps(self.comment_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data.get('content'), 'My comment')
        return api_token

    def test_comment_create_without_credentials(self):
        """Test: create comment for post without credentials"""
        self.test_blog_create()
        response = self.client().post('/comments/', headers=self.headers, data=json.dumps(self.comment_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data.get('error'), "Authentication token is not available, please login")

    def test_comment_list(self):
        """Test: get the list of comments"""
        self.test_comment_create()
        response = self.client().get('/comments/', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get("data")), 1)

    def test_blog_comments_list(self):
        """Test: get the list of comments for one post"""
        self.test_comment_create()
        response = self.client().get('/post-comments/1', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get("data")), 1)

    def test_comment_delete(self):
        """Test: delete the comment"""
        api_token = self.test_comment_create()
        # Check for without token
        response = self.client().delete('/comments/1', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(data.get('error'))

        # Check for with token
        headers = {'Content-Type': 'application/json', 'api-token': api_token}
        response = self.client().delete('/comments/1', headers=headers)
        self.assertEqual(response.status_code, 204)

        # Check the count of comments
        response = self.client().get('/comments/', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get("data")), 0)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
