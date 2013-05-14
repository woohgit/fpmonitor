import string
from datetime import datetime, timedelta
from helpers import create_adam, create_eva, login_adam, create_cecil, login_cecil, logout, ADAM_PASSWORD, ADAM_USERNAME, EVA_USERNAME, EVA_PASSWORD
from fpmonitor.test_api.test_api import create_nodes
from fpmonitor.consts import *
from fpmonitor.models import Node, AlertingChain, AlertLog
import json
from mock import patch, Mock

from fpmonitor.mailer import send_alerting_mail, send_reboot_mail

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.conf import settings
from django.utils import timezone

__all__ = ['LoginTestCase', 'NodeTestCase', 'TestApiTestCase', 'WebSiteTestCase', 'AlertingChainTestCase', 'AlertLogTestCase']


class AlertLogTestCase(TestCase):

    def setUp(self):
        self.owner = create_adam()
        self.other_owner = create_eva()
        self.node_name = 'name_01'
        self.created_node = Node.create_node(self.owner, self.node_name)

    def test_create_alert_log(self):
        AlertLog.create_alert_log(self.created_node)
        self.assertEquals(len(AlertLog.objects.all()), 1)
        log = AlertLog.objects.get(node=self.created_node)
        self.assertEquals(log.reported_status, self.created_node.status)

    def test_alerted_recently_no_node(self):
        result = AlertLog.alerted_recently(self.created_node, self.created_node.status)
        self.assertFalse(result)

    def test_alerted_recently_node_old_alert_record(self):
        AlertLog.create_alert_log(self.created_node)
        self.assertEquals(len(AlertLog.objects.all()), 1)
        log = AlertLog.objects.get(node=self.created_node)
        log.event_date = timezone.now() - timedelta(hours=1)
        log.save()
        result = AlertLog.alerted_recently(self.created_node, self.created_node.status)
        self.assertFalse(result)

    def test_alerted_recently_node(self):
        AlertLog.create_alert_log(self.created_node)
        self.assertEquals(len(AlertLog.objects.all()), 1)
        result = AlertLog.alerted_recently(self.created_node, self.created_node.status)
        self.assertTrue(result)


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

    def test_receive_data_new_node(self):
        owner = create_adam()
        data = {}
        data['node_name'] = 'test'
        data['node_user_id'] = owner.id
        data['uptime'] = 1000
        data['loadavg'] = (1, 1, 1)
        data['system'] = 'System'
        data['kernel'] = 'Kernel'
        data['distribution'] = 'Distribution'
        data['memory_usage'] = 40
        post_data = json.dumps(data)
        self.client.post('/receive_data', {'data': post_data})
        node = Node.objects.get(name='test')
        self.assertEquals(node.name, 'test')
        self.assertEquals(node.owner, owner)
        self.assertEquals(node.os_type, 'System')
        self.assertEquals(node.kernel_version, 'Kernel')
        self.assertEquals(node.get_last_seen_in_minutes(), "0 second(s)")

    def test_receive_data_existing_node(self):
        owner = create_adam()
        created_node = Node.create_node(owner, 'test')
        data = {}
        data['node_name'] = 'test'
        data['node_user_id'] = owner.id
        data['loadavg'] = (1, 1, 1)
        data['system'] = 'System'
        data['kernel'] = 'Kernel'
        data['distribution'] = 'Distribution'
        data['memory_usage'] = 40
        data['uptime'] = 1005
        post_data = json.dumps(data)
        self.client.post('/receive_data', {'data': post_data})
        node = Node.objects.get(pk=created_node.id)
        self.assertEquals(node.name, 'test')
        self.assertEquals(node.owner, owner)
        self.assertEquals(node.os_type, 'System')
        self.assertEquals(node.uptime, 1005)
        self.assertEquals(node.kernel_version, 'Kernel')
        self.assertEquals(node.get_last_seen_in_minutes(), "0 second(s)")

    @patch('fpmonitor.views.send_reboot_mail')
    def test_receive_data_sends_rebooted_email(self, mock_mail):
        owner = create_adam()
        created_node = Node.create_node(owner, 'test')
        created_node.uptime = 10000
        created_node.save()
        data = {}
        data['node_name'] = 'test'
        data['node_user_id'] = owner.id
        data['loadavg'] = (1, 1, 1)
        data['system'] = 'System'
        data['kernel'] = 'Kernel'
        data['distribution'] = 'Distribution'
        data['memory_usage'] = 40
        data['uptime'] = 10
        post_data = json.dumps(data)
        response = self.client.post('/receive_data', {'data': post_data})
        node = Node.objects.get(pk=created_node.id)
        mock_mail.assert_called_once_with(created_node)


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

    def test_node_get_cls_status_text(self):
        result = Node.cls_get_status_text(STATUS_UNKNOWN)
        self.assertEquals(result, 'unknown')

        result = Node.cls_get_status_text(STATUS_OK)
        self.assertEquals(result, 'ok')

        result = Node.cls_get_status_text(STATUS_INFO)
        self.assertEquals(result, 'info')

        result = Node.cls_get_status_text(STATUS_WARNING)
        self.assertEquals(result, 'warning')

        result = Node.cls_get_status_text(STATUS_ERROR)
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
        self.assertEquals(result, 'important')

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
        now = timezone.now()
        last_sync = now - timedelta(seconds=10)
        self.created_node.last_sync = last_sync
        result = self.created_node.get_last_seen_in_minutes()
        self.assertEquals(result, "10 second(s)")

    def test_get_last_seen_in_minutes_should_return_the_diff_in_minutes(self):
        """get_last_seen_in_minutes should return diff in minutes

        """
        now = timezone.now()
        last_sync = now - timedelta(minutes=10)
        self.created_node.last_sync = last_sync
        result = self.created_node.get_last_seen_in_minutes()
        self.assertEquals(result, "10 minute(s)")

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

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_alert_status_load(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 1
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_called_once_with(self.created_node, STATUS_UNKNOWN)
        self.assertEquals(len(AlertLog.objects.all()), 1)

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_alert_status_seen(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now() - timedelta(minutes=3)
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_called_once_with(self.created_node, STATUS_UNKNOWN)
        self.assertEquals(len(AlertLog.objects.all()), 1)

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_alert_status_memory(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 85
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 85)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_called_once_with(self.created_node, STATUS_UNKNOWN)
        self.assertEquals(len(AlertLog.objects.all()), 1)

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_does_not_alert_status_load(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 1
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.maintenance_mode = True
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_does_not_alert_status_seen(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now() - timedelta(minutes=3)
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.maintenance_mode = True
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_does_not_alert_status_memory(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 85
        self.created_node.maintenance_mode = True
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 85)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_does_not_alert_same_status_status_load(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_INFO
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 1
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_does_not_alert_same_status_status_seen(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_INFO
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now() - timedelta(minutes=3)
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_does_not_alert_same_status_status_memory(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_INFO
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 85
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 85)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        node.status = STATUS_INFO
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_alert_status_load_already_reported(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_INFO
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 1
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.save()
        AlertLog.create_alert_log(self.created_node)
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_UNKNOWN)
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_alert_status_seen_already_reported(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_INFO
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now() - timedelta(minutes=3)
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 0
        self.created_node.save()
        AlertLog.create_alert_log(self.created_node)
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 40)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_UNKNOWN)
        mock_send_alerting_mail.assert_has_calls([])

    @patch('fpmonitor.models.send_alerting_mail')
    def test_check_alerting_level_alert_status_memory_already_reported(self, mock_send_alerting_mail):
        self.created_node.status = STATUS_INFO
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.memory_usage = 85
        self.created_node.save()
        AlertLog.create_alert_log(self.created_node)
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.save()
        result = self.created_node.check_alerting_level(STATUS_INFO, 1, 2, 85)
        self.assertTrue(result)
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_UNKNOWN)
        mock_send_alerting_mail.assert_has_calls([])

    def test_update_status_if_required(self):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = 0
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.save()
        self.created_node.update_status_if_required()
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_OK)

    def test_update_status_if_required_load(self):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = settings.ALERT_INFO_LOAD + 1
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.save()
        self.created_node.update_status_if_required()
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_INFO)

    def test_update_status_if_required_error(self):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = settings.ALERT_DANGER_LOAD
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.save()
        self.created_node.update_status_if_required()
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_ERROR)

    def test_update_status_if_required_warning(self):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = settings.ALERT_WARNING_LOAD
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.save()
        self.created_node.update_status_if_required()
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_WARNING)

    def test_update_status_if_required_info(self):
        self.created_node.status = STATUS_UNKNOWN
        self.created_node.uptime = 1000
        self.created_node.last_sync = timezone.now()
        self.created_node.loadavg_5 = settings.ALERT_INFO_LOAD
        self.created_node.loadavg_10 = 0
        self.created_node.loadavg_15 = 0
        self.created_node.save()
        self.created_node.update_status_if_required()
        node = Node.objects.get(pk=self.created_node.id)
        self.assertEquals(node.status, STATUS_INFO)

    def test_get_alerting_addresses_no_extra_emails(self):
        """
        get_alerting_addresses should return the owner.email

        """
        result = self.created_node.get_alerting_addresses()
        self.assertEquals(len(result), 1)
        self.assertTrue(result[0], self.owner.email)

    def test_get_alerting_addresses_with_extra_emails(self):
        test_mail_address = 'test_email@test.hu'
        alerting_email = AlertingChain.objects.create(node=self.created_node, email=test_mail_address)
        alerting_email.save()
        result = self.created_node.get_alerting_addresses()
        self.assertEquals(len(result), 1)
        self.assertTrue(result[0], test_mail_address)

    def test_get_alerting_addresses_unique(self):
        test_mail_address = 'test_email@test.hu'
        alerting_email = AlertingChain.objects.create(node=self.created_node, email=test_mail_address)
        alerting_email.save()
        alerting_email = AlertingChain.objects.create(node=self.created_node, email=self.owner.email)
        alerting_email.save()
        result = self.created_node.get_alerting_addresses()
        self.assertEquals(len(result), 2)

    @patch('fpmonitor.mailer.smtplib')
    def test_send_reboot_mail(self, mock_smtplib):
        mock_smtplib.SMTP = Mock()
        result = send_reboot_mail(self.created_node)
        self.assertTrue(result)
        mock_smtplib.SMTP.assert_called_once_with("127.0.0.1")

    @patch('fpmonitor.mailer.smtplib')
    def test_send_reboot_mail_on_exception(self, mock_smtplib):
        mock_smtplib.SMTP = Mock()
        mock_smtplib.SMTP.side_effect = Exception("Boom")
        result = send_reboot_mail(self.created_node)
        self.assertFalse(result)
        mock_smtplib.SMTP.assert_called_once_with("127.0.0.1")

    @patch('fpmonitor.mailer.smtplib')
    @patch('fpmonitor.mailer.string')
    def test_send_alerting_mail(self, mock_string, mock_smtplib):
        mock_smtplib.SMTP = Mock()
        mock_string.join = Mock()
        self.created_node.status = STATUS_WARNING
        self.created_node.save()
        result = send_alerting_mail(self.created_node, STATUS_INFO)
        self.assertTrue(result)
        mock_string.join.assert_called_once_with(('From: info@fpmonitor.com', "To: ['adam@adam.hu']", 'Subject: [monitoring] [warning] name_01 status', '', "Your node's [name_01] status has been changed from info to warning\n"), '\r\n')
        mock_smtplib.SMTP.assert_called_once_with("127.0.0.1")


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

    def test_api_test_mode_off(self):
        self.client.get('/test_api/test_mode_off')
        self.assertFalse(settings.TEST_MODE)

    def test_api_test_mode_on(self):
        self.client.get('/test_api/test_mode_off')
        self.assertFalse(settings.TEST_MODE)
        self.client.get('/test_api/test_mode_on')
        self.assertTrue(settings.TEST_MODE)

    def test_api_test_mode_on_fails_when_not_superadmin(self):
        self.client.get('/test_api/test_mode_off')
        self.assertFalse(settings.TEST_MODE)
        self.owner.is_superuser = False
        self.owner.save()
        self.client.get('/test_api/test_mode_on')
        self.assertFalse(settings.TEST_MODE)

    def test_view_node_details_redirects_when_not_owner(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (1, STATUS_OK))
        self.owner = create_cecil()
        login_cecil(self)
        response = self.client.get('/node/1')
        self.assertRedirects(response, '/index', status_code=302)

    def test_view_node_details_redirects_on_exception(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (1, STATUS_OK))
        response = self.client.get('/node/00')
        self.assertRedirects(response, '/index', status_code=302)

    def test_view_node_details_returns_200_when_owner(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (1, STATUS_OK))
        response = self.client.get('/node/1')
        self.assertEquals(response.status_code, 200)

    def test_delete_node_successful(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (1, STATUS_OK))
        n = Node.objects.all()[0]
        self.client.get('/delete_node/%s' % n.id)
        nodes = Node.objects.all()
        self.assertEquals(len(nodes), 0)

    def test_delete_node_unsuccessful(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (1, STATUS_OK))
        n = Node.objects.all()[0]
        self.owner = create_cecil()
        login_cecil(self)
        self.client.get('/delete_node/%s' % n.id)
        nodes = Node.objects.all()
        self.assertEquals(len(nodes), 1)

    def test_view_node_create_alerting_chain_succeeds(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (1, STATUS_OK))
        self.client.post('/node/1', {'address': 'newaddress@address'})
        # response = self.client.get('/node/1')
        objects = AlertingChain.objects.all()
        self.assertEquals(len(objects), 1)
        self.assertEquals(objects[0].email, 'newaddress@address')

    def test_view_node_create_alerting_chain_fails(self):
        self.client.get('/test_api/create_nodes/%s/%s' % (1, STATUS_OK))
        self.owner = create_cecil()
        login_cecil(self)
        self.client.post('/node/1', {'address': 'newaddress@address'})
        objects = AlertingChain.objects.all()
        self.assertEquals(len(objects), 0)


class AlertingChainTestCase(TestCase):

    def setUp(self):
        self.owner = create_adam()
        self.other_owner = create_eva()
        self.node_name = 'name_01'
        self.created_node = Node.create_node(self.owner, self.node_name)
        self.email = 'testemail@test.hu'

    def test_create_alerting_chain_successful(self):
        created = AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        self.assertTrue(created)
        result = AlertingChain.objects.all()
        self.assertEquals(len(result), 1)

    def test_create_alerting_chain_does_not_create_twice(self):
        AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        created = AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        self.assertFalse(created)
        result = AlertingChain.objects.all()
        self.assertEquals(len(result), 1)

    def test_delete_alerting_chain_successful(self):
        created = AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        self.assertTrue(created)
        chain = AlertingChain.objects.get(node=self.created_node, email=self.email)
        result = AlertingChain.delete_alerting_chain(self.created_node.owner, chain.id)
        self.assertTrue(result)
        chains = AlertingChain.objects.all()
        self.assertEquals(len(chains), 0)

    def test_delete_alerting_chain_fails(self):
        created = AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        self.assertTrue(created)
        chain = AlertingChain.objects.get(node=self.created_node, email=self.email)
        result = AlertingChain.delete_alerting_chain(self.other_owner, chain.id)
        self.assertFalse(result)
        chains = AlertingChain.objects.all()
        self.assertEquals(len(chains), 1)

    def test_delete_alerting_chain_fails_exception(self):
        created = AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        self.assertTrue(created)
        chain = AlertingChain.objects.get(node=self.created_node, email=self.email)
        result = AlertingChain.delete_alerting_chain('owner', chain.id)
        self.assertFalse(result)
        chains = AlertingChain.objects.all()
        self.assertEquals(len(chains), 1)

    def test_delete_address_succeessful(self):
        login_adam(self)
        AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        chain = AlertingChain.objects.get(node=self.created_node, email=self.email)
        response = self.client.get('/delete_address/%s' % chain.id)
        self.assertRedirects(response, '/index', status_code=302)
        chains = AlertingChain.objects.all()
        self.assertEquals(len(chains), 0)

    def test_delete_address_succeessful_with_meta(self):
        login_adam(self)
        AlertingChain.create_alerting_chain(node=self.created_node, email=self.email)
        chain = AlertingChain.objects.get(node=self.created_node, email=self.email)
        response = self.client.get('/delete_address/%s' % chain.id, HTTP_REFERER='http://testserver/node/1')
        self.assertRedirects(response, '/node/1', status_code=302)
        chains = AlertingChain.objects.all()
        self.assertEquals(len(chains), 0)
