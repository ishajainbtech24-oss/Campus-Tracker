import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app

class CampusTrackerTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    # ---------- HOME PAGE ----------
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print('✅ Home page loads correctly')

    # ---------- LOGIN PAGE ----------
    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        print('✅ Login page loads correctly')

    # ---------- REGISTER PAGE ----------
    def test_register_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        print('✅ Register page loads correctly')

    # ---------- DASHBOARD REQUIRES LOGIN ----------
    def test_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        print('✅ Dashboard redirects to login if not logged in')

    # ---------- SUBMIT REQUIRES LOGIN ----------
    def test_submit_redirects_if_not_logged_in(self):
        response = self.client.get('/submit')
        self.assertEqual(response.status_code, 302)
        print('✅ Submit page redirects to login if not logged in')

    # ---------- ADMIN REQUIRES LOGIN ----------
    def test_admin_redirects_if_not_logged_in(self):
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 302)
        print('✅ Admin page redirects to login if not logged in')

    # ---------- COUNTERS PAGE ----------
    def test_counters_page(self):
        response = self.client.get('/counters')
        self.assertEqual(response.status_code, 200)
        print('✅ Office counters page loads correctly')

    # ---------- INVALID LOGIN ----------
    def test_invalid_login(self):
        response = self.client.post('/login', data={
            'email': 'wrong@test.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        print('✅ Invalid login handled correctly')

    # ---------- 404 PAGE ----------
    def test_404_page(self):
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        print('✅ 404 page works correctly')

if __name__ == '__main__':
    unittest.main(verbosity=2)