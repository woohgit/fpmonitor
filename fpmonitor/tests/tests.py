from datetime import datetime, timedelta
from helpers import create_adam, create_eva, login_adam, ADAM_PASSWORD, ADAM_USERNAME, EVA_USERNAME, EVA_PASSWORD
import fpmonitor.api
from fpmonitor.test_api.test_api import create_nodes
from fpmonitor.consts import *
from fpmonitor.models import Node
from mock import patch, Mock

from django.contrib.auth.models import User
from django.db import IntegrityError
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
        create_eva()
        response = self.client.post('/login', {'username': EVA_USERNAME, 'password': EVA_PASSWORD})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Inactive")

    def test_login_fails_on_exception(self):
        response = self.client.post('/login', {'username': EVA_USERNAME})
        self.assertEquals(response.status_code, 402)

    def test_logout(self):
        response = self.client.get('/logout')
        self.assertRedirects(response, '/login', status_code=302)


class NodeTestCase(TestCase):
    def setUp(self):
        self.owner = create_adam()
        self.other_owner = create_eva()
        self.node_name = 'name_01'
        self.created_node = Node.create_node(self.owner, self.node_name)

    def test_create_node_raises_exception_when_name_and_owner_is_the_same(self):
        with self.assertRaises(IntegrityError):
            Node.create_node(self.owner, self.node_name)

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

    def test_node_get_status_text_unknown(self):
        self.created_node.status = STATUS_UNKNOWN
        result = self.created_node.get_status_text()
        self.assertEquals(result, 'unknown')

    def test_node_get_status_text_ok(self):
        self.created_node.status = STATUS_OK
        result = self.created_node.get_status_text()
        self.assertEquals(result, 'ok')

    def test_node_get_status_text_info(self):
        self.created_node.status = STATUS_INFO
        result = self.created_node.get_status_text()
        self.assertEquals(result, 'info')

    def test_node_get_status_text_warning(self):
        self.created_node.status = STATUS_WARNING
        result = self.created_node.get_status_text()
        self.assertEquals(result, 'warning')

    def test_node_get_status_text_error(self):
        self.created_node.status = STATUS_ERROR
        result = self.created_node.get_status_text()
        self.assertEquals(result, 'error')

    def test_node_get_status_class_unknown(self):
        self.created_node.status = STATUS_UNKNOWN
        result = self.created_node.get_status_class()
        self.assertEquals(result, '')

    def test_node_get_status_class_ok(self):
        self.created_node.status = STATUS_OK
        result = self.created_node.get_status_class()
        self.assertEquals(result, 'success')

    def test_node_get_status_class_info(self):
        self.created_node.status = STATUS_INFO
        result = self.created_node.get_status_class()
        self.assertEquals(result, 'info')

    def test_node_get_status_class_warning(self):
        self.created_node.status = STATUS_WARNING
        result = self.created_node.get_status_class()
        self.assertEquals(result, 'warning')

    def test_node_get_status_class_error(self):
        self.created_node.status = STATUS_ERROR
        result = self.created_node.get_status_class()
        self.assertEquals(result, 'danger')

    def test_delete_succeeds(self):
        """it should return true if the node exists and the owner matches with the node

        """
        request = Mock()
        request.user = self.owner
        result = Node.delete_node(self.created_node.id, request)
        self.assertTrue(result)
        nodes = Node.get_nodes(self.owner)
        self.assertEquals(len(nodes), 0)

    def test_get_last_seen_in_minutes_empty_last_sync(self):
        """get_last_seen_in_minutes should return N/A when no info about the last sync

        """
        result = self.created_node.get_last_seen_in_minutes()
        self.assertEquals(result, "N/A")

    def test_get_last_seen_in_minutes_should_return_0_minutes(self):
        """get_last_seen_in_minutes should return 0 in minutes

        """
        now = datetime.now()
        last_sync = now - timedelta(seconds=10)
        self.created_node.last_sync = last_sync
        result = self.created_node.get_last_seen_in_minutes()
        self.assertEquals(result, 0)

    def test_get_last_seen_in_minutes_should_return_the_diff_in_minutes(self):
        """get_last_seen_in_minutes should return diff in minutes

        """
        now = datetime.now()
        last_sync = now - timedelta(minutes=10)
        self.created_node.last_sync = last_sync
        result = self.created_node.get_last_seen_in_minutes()
        self.assertEquals(result, 10)

    def test_api_node_maintenance_login_required_302(self):
        response = self.client.post('/api/v1/node/maintenance_mode', {'id': '0'})
        self.assertEquals(response.status_code, 302)

    def test_api_node_maintenance_changes_maintenance(self):
        login_adam(self)
        response = self.client.post('/api/v1/node/maintenance_mode', {'id': self.created_node.id, 'mode': 'true'})
        node = Node.objects.get(pk=self.created_node.id)
        self.assertFalse(node.maintenance_mode)
        response = self.client.post('/api/v1/node/maintenance_mode', {'id': self.created_node.id, 'mode': 'false'})
        node = Node.objects.get(pk=self.created_node.id)
        self.assertTrue(node.maintenance_mode)

    def test_api_node_maintenance_does_notchange_maintenance_on_exception(self):
        login_adam(self)
        self.assertFalse(self.created_node.maintenance_mode)
        response = self.client.post('/api/v1/node/maintenance_mode', {'id': self.created_node.id})
        node = Node.objects.get(pk=self.created_node.id)
        self.assertFalse(node.maintenance_mode)

    @patch('fpmonitor.models.Node.get_uptime_string')
    def test_get_uptime_calls_get_uptime_string(self, mock_get_uptime_string):
        mock_get_uptime_string.return_value = "1 hour(s), 0 minute(s)"
        self.created_node.uptime = 3600
        self.created_node.save()
        result = self.created_node.get_uptime()
        mock_get_uptime_string.assert_called_once_with(self.created_node.uptime)

    def test_get_uptime_string(self):
        result = Node.get_uptime_string(0)
        self.assertEquals("0 second(s)", result)
        result = Node.get_uptime_string(60)
        self.assertEquals("1 minute(s)", result)
        result = Node.get_uptime_string(840)
        self.assertEquals("14 minute(s)", result)
        result = Node.get_uptime_string(3600)
        self.assertEquals("1 hour(s), 0 minute(s)", result)
        result = Node.get_uptime_string(86400)
        self.assertEquals("1 day(s), 0 hour(s)", result)
        result = Node.get_uptime_string(3459601)
        self.assertEquals("40 day(s), 1 hour(s)", result)


class TestApiTestCase(TestCase):

    def setUp(self):
        self.owner = create_adam()
        login_adam(self)
        self.nodes_to_create = 2
        settings.TEST_MODE = True

    def test_test_api_create_nodes_should_create_nodes(self):
        response = self.client.get('/test_api/create_nodes/%s/%s' % (self.nodes_to_create, STATUS_OK))
        self.assertEquals(response.status_code, 200)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), self.nodes_to_create)
        for node in nodes:
            self.assertEquals(node.status, STATUS_OK)

    def test_test_api_create_nodes_should_return_302_when_tests_are_disabled(self):
        settings.TEST_MODE = False
        response = self.client.get('/test_api/create_nodes/%s/%s' % (self.nodes_to_create, STATUS_UNKNOWN))
        self.assertRedirects(response, '/index', status_code=302)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    def test_test_api_clenaup_nodes_should_return_302_when_tests_are_disabled(self):
        settings.TEST_MODE = False
        response = self.client.get('/test_api/cleanup_nodes')
        self.assertRedirects(response, '/index', status_code=302)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    def test_test_api_create_nodes_should_create_nodes_with_specific_name(self):
        nodename = 'nodename12345'
        response = self.client.get('/test_api/create_nodes/%s/%s/%s' % (1, STATUS_OK, nodename))
        self.assertEquals(response.status_code, 200)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 1)
        self.assertEquals(nodes[0].name, nodename)

    def test_tets_api_cleanup_nodes_should_delete_all_nodes(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (self.nodes_to_create, STATUS_UNKNOWN))
        response = self.client.get('/test_api/cleanup_nodes')
        self.assertEquals(response.status_code, 200)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    @patch('fpmonitor.test_api.test_api.Node.create_node')
    def test_test_api_create_nodes_returns_500_on_exeption(self, mock_create_node):
        mock_create_node.side_effect = Exception("Boom")
        response = self.client.get('/test_api/create_nodes/%s/%s' % (self.nodes_to_create, STATUS_UNKNOWN))
        self.assertEquals(response.content, 'NOK')
        self.assertEquals(response.status_code, 500)
        nodes = Node.objects.filter(owner=self.owner)
        self.assertEquals(len(nodes), 0)

    @patch('fpmonitor.test_api.test_api.Node.objects.filter')
    def test_test_api_cleanup_nodes_returns_500_on_exeption(self, mock_objects_fiter):
        mock_objects_fiter.side_effect = Exception("Boom")
        self.client.get('/test_api/create_nodes/%s/%s' % (self.nodes_to_create, STATUS_UNKNOWN))
        response = self.client.get('/test_api/cleanup_nodes')
        self.assertEquals(response.content, 'NOK')
        self.assertEquals(response.status_code, 500)
