import unittest
from app import app

class TestApp(unittest.TestCase):
    
    def test_home_page(self):
        tester = app.test_client(self)
        response = tester.get('/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_login_page(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username='user', password='pass'), follow_redirects=True)
        self.assertIn(b'Welcome', response.data)

if __name__ == '__main__':
    unittest.main()