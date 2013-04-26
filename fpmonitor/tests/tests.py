from helpers import create_adam, create_eva, login_adam, ADAM_PASSWORD, ADAM_USERNAME
import fpmonitor.api
from fpmonitor.models import Node
from mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

__all__ = ['LoginTestCase', 'NodeTestCase', 'WebSiteTestCase']


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


class NodeTestCase(TestCase):
    def setUp(self):
        self.owner = create_adam()
        self.other_owner = create_eva()
        self.node_name = 'name_01'
        self.created_node = Node.create_node(self.owner, self.node_name)

    def test_get_nodes_shuld_return_empty_when_no_nodes_under_owner(self):
        result = Node.get_nodes(self.other_owner)
        self.assertEquals(len(result), 0)

    def test_get_nodes_shuld_return_nodes_when_nodes_under_owner(self):
        result = Node.get_nodes(self.owner)
        self.assertEquals(len(result), 1)

    def test_node_owner(self):
        self.assertEquals(self.created_node.owner, self.owner)

    def test_node_name(self):
        self.assertEquals(self.created_node.name, self.node_name)

    def test_node_maintenance_mode(self):
        self.assertFalse(self.created_node.maintenance_mode)

    def test_node_registered_at(self):
        self.assertTrue(self.created_node.registered_at)
