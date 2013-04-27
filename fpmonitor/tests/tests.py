from helpers import create_adam, create_eva, login_adam, ADAM_PASSWORD, ADAM_USERNAME, EVA_USERNAME, EVA_PASSWORD
import fpmonitor.api
from fpmonitor.test_api.test_api import create_nodes

from fpmonitor.models import Node
from mock import patch, Mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

__all__ = ['LoginTestCase', 'NodeTestCase', 'TestApiTestCase', 'WebSiteTestCase']


class WebSiteTestCase(TestCase):

    def test_default_page_redirects_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login', status_code=302)

    def test_login_required_return_302(self):
        response = self.client.post('/index', {'key': 'value'})
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
        self.assertContains(response, "Invalid")

    def test_login_unsuccessful_when_inactive(self):
        """unsuccessful login should reload the login page with 200 response code

        """
        create_eva()
        response = self.client.post('/login', {'username': EVA_USERNAME, 'password': EVA_PASSWORD})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Inactive")

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

    def test_delete_fails_if_node_not_exists(self):
        """it should return False when the node does not exists

        """
        request = Mock()
        request.user = self.owner
        result = Node.delete_node(5, request)
        self.assertFalse(result)

    def test_delete_succeeds(self):
        """it should return true if the node exists and the owner matches with the node

        """
        request = Mock()
        request.user = self.owner
        result = Node.delete_node(self.created_node.id, request)
        self.assertTrue(result)
        nodes = Node.get_nodes(self.owner)
        self.assertEquals(len(nodes), 0)


class TestApiTestCase(TestCase):

    def setUp(self):
        self.owner = create_adam()
        login_adam(self)
        self.nodes_to_create = 5
        settings.TEST_MODE = True

    def test_test_api_create_nodes_should_create_nodes(self):
        response = self.client.get('/test_api/create_nodes/%s/' % self.nodes_to_create)
        self.assertEquals(response.status_code, 200)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), self.nodes_to_create)

    def test_test_api_create_nodes_should_return_302_when_tests_are_disabled(self):
        settings.TEST_MODE = False
        response = self.client.get('/test_api/create_nodes/%s/' % self.nodes_to_create)
        self.assertRedirects(response, '/index', status_code=302)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    def test_test_api_clenaup_nodes_should_return_302_when_tests_are_disabled(self):
        settings.TEST_MODE = False
        response = self.client.get('/test_api/cleanup_nodes')
        self.assertRedirects(response, '/index', status_code=302)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    def test_tets_api_cleanup_nodes_should_delete_all_nodes(self):
        self.client.get('/test_api/create_nodes/%s/' % self.nodes_to_create)
        response = self.client.get('/test_api/cleanup_nodes')
        self.assertEquals(response.status_code, 200)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    @patch('fpmonitor.test_api.test_api.Node.create_node')
    def test_test_api_create_nodes_returns_500_on_exeption(self, mock_create_node):
        mock_create_node.side_effect = Exception("Boom")
        response = self.client.get('/test_api/create_nodes/%s/' % self.nodes_to_create)
        self.assertEquals(response.content, 'NOK')
        self.assertEquals(response.status_code, 500)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    @patch('fpmonitor.test_api.test_api.Node.objects.filter')
    def test_test_api_cleanup_nodes_returns_500_on_exeption(self, mock_objects_fiter):
        mock_objects_fiter.side_effect = Exception("Boom")
        self.client.get('/test_api/create_nodes/%s/' % self.nodes_to_create)
        response = self.client.get('/test_api/cleanup_nodes')
        self.assertEquals(response.content, 'NOK')
        self.assertEquals(response.status_code, 500)
