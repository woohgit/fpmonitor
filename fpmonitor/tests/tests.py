from helpers import create_adam, login_adam, ADAM_PASSWORD, ADAM_USERNAME
import fpmonitor.api
from mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

__all__ = ['LoginTestCase', 'WebSiteTestCase']


class WebSiteTestCase(TestCase):

    def test_default_page_redirects_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login', status_code=302)

    def test_login_required_return_302(self):
        response = self.client.post('/secret_place', {'key': 'value'})
        self.assertEquals(response.status_code, 302)

    def test_default_page_redirects_if_loggedin(self):
        create_adam()
        login_adam(self)
        response = self.client.get('/')
        self.assertRedirects(response, '/index', status_code=302)


class LoginTestCase(TestCase):

    def setUp(self):
        create_adam()

    def test_login_successful(self):
        """successful login should redirect us to /index with 302 response code

        """
        response = self.client.post('/login', {'username': ADAM_USERNAME, 'password': ADAM_PASSWORD})
        self.assertRedirects(response, '/index', status_code=302)

    def test_login_unsuccessful(self):
        """unsuccessful login should reload the login page with 200 response code

        """
        response = self.client.post('/login', {'username': ADAM_USERNAME, 'password': 'whatever'})
        self.assertEquals(response.status_code, 200)

    def test_logout(self):
        response = self.client.get('/logout')
        self.assertRedirects(response, '/login', status_code=302)
