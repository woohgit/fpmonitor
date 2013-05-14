from django.utils import timezone
from fpmonitor.consts import *
from fpmonitor.mailer import send_alerting_mail
from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.conf import settings


class Node(models.Model):

    owner = models.ForeignKey(User, blank=False)
    registered_at = models.DateTimeField(null=True, blank=True, default=timezone.now())
    last_sync = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=250, blank=False)
    os_type = models.CharField(max_length=250)
    os_version = models.CharField(max_length=250)
    kernel_version = models.CharField(max_length=250)
    maintenance_mode = models.BooleanField(default=False)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    uptime = models.PositiveIntegerField(default=0)
    loadavg_5 = models.CharField(max_length=64, blank=True, null=True)
    loadavg_10 = models.CharField(max_length=64, blank=True, null=True)
    loadavg_15 = models.CharField(max_length=64, blank=True, null=True)
    memory_usage = models.PositiveIntegerField(default=0)

    @classmethod
    def get_nodes(cls, owner):
        return Node.objects.filter(owner=owner)

    @classmethod
    def create_node(cls, owner, name, status=STATUS_UNKNOWN):
        n = Node.objects.filter(owner=owner, name=name)
        if n:
            raise IntegrityError('This node name is taken')
        node = Node.objects.create(owner=owner, name=name, os_type='Linux', os_version='Ubuntu', status=status)
        return node

    @classmethod
    def delete_node(cls, pk, request):
        try:
            node = Node.objects.get(pk=pk, owner=request.user)
            node.delete()
            return True
        except:
            return False

    @classmethod
    def cls_get_status_text(cls, status):
        if status == STATUS_OK:
            return 'ok'
        elif status == STATUS_UNKNOWN:
            return 'unknown'
        elif status == STATUS_INFO:
            return 'info'
        elif status == STATUS_WARNING:
            return 'warning'
        else:
            return 'error'

    def get_status_text(self):
        if self.status == STATUS_OK:
            return 'ok'
        elif self.status == STATUS_UNKNOWN:
            return 'unknown'
        elif self.status == STATUS_INFO:
            return 'info'
        elif self.status == STATUS_WARNING:
            return 'warning'
        else:
            return 'error'

    def get_alerting_addresses(self):
        emails = []
        alert_addresses = AlertingChain.objects.filter(node=self)
        if not alert_addresses:
            emails.append(self.owner)
        else:
            for email in alert_addresses:
                emails.append(email)
        return emails

    def get_status_class(self):
        if self.status == STATUS_OK:
            return 'success'
        elif self.status == STATUS_UNKNOWN:
            return ''
        elif self.status == STATUS_INFO:
            return 'info'
        elif self.status == STATUS_WARNING:
            return 'warning'
        else:
            return 'important'

    def get_last_seen_in_minutes(self):
        now = timezone.now()
        try:
            if self.last_sync is None:
                result = 'N/A'
            else:
                result = self.get_uptime_string((now - self.last_sync).seconds)
        except Exception as e:
            result = e
        return result

    def check_alerting_level(self, status, threshold_load, threshold_seen, threshold_memory):
        if (int(float(self.loadavg_5)) >= threshold_load or int(float(self.loadavg_10)) >= threshold_load or int(float(self.loadavg_15)) >= threshold_load):
            if self.status != status and not self.maintenance_mode and not AlertLog.alerted_recently(self, status):
                send_alerting_mail(self, self.status)
                self.status = status
                self.save()
                AlertLog.create_alert_log(self)
            return True

        if ((timezone.now() - self.last_sync).seconds / 60) >= threshold_seen:
            if self.status != status and not self.maintenance_mode and not AlertLog.alerted_recently(self, status):
                send_alerting_mail(self, self.status)
                self.status = status
                self.save()
                AlertLog.create_alert_log(self)
            return True

        if self.memory_usage >= threshold_memory:
            if self.status != status and not self.maintenance_mode and not AlertLog.alerted_recently(self, status):
                send_alerting_mail(self, self.status)
                self.status = status
                self.save()
                AlertLog.create_alert_log(self)
            return True

        return False

    def update_status_if_required(self):

        if self.check_alerting_level(STATUS_ERROR, settings.ALERT_DANGER_LOAD, settings.ALERT_DANGER_SEEN, settings.ALERT_DANGER_MEMORY):
            return
        if self.check_alerting_level(STATUS_WARNING, settings.ALERT_WARNING_LOAD, settings.ALERT_WARNING_SEEN, settings.ALERT_WARNING_MEMORY):
            return
        if self.check_alerting_level(STATUS_INFO, settings.ALERT_INFO_LOAD, settings.ALERT_INFO_SEEN, settings.ALERT_INFO_MEMORY):
            return

        self.status = STATUS_OK
        self.save()

    def get_uptime(self):
        return self.get_uptime_string(self.uptime)

    @classmethod
    def get_uptime_string(cls, seconds):
        days = seconds / 86400
        seconds -= 86400 * days

        hours = seconds / 3600
        seconds -= 3600 * hours

        minutes = seconds / 60
        seconds -= 60 * minutes

        if days == 0 and hours == 0 and minutes == 0:
            return "%d second(s)" % (seconds)

        if days == 0 and hours == 0:
            return "%d minute(s)" % (minutes)

        if days == 0:
            return "%d hour(s), %d minute(s)" % (hours, minutes)

        # use a more bigger perspective. We're not interested in minutes and seconds as of now
        return "%d day(s), %d hour(s)" % (days, hours)


class AlertingChain(models.Model):

    node = models.ForeignKey(Node, blank=False)
    email = models.CharField(max_length=64, blank=True, null=True)

    def get_email(self):
        return self.email.replace('@', '_')

    @classmethod
    def create_alerting_chain(cls, node, email):
        addresses = AlertingChain.objects.filter(node=node, email=email)
        if addresses:
            return False
        else:
            chain = AlertingChain.objects.create(node=node, email=email)
            chain.save()
            return True

    @classmethod
    def delete_alerting_chain(cls, owner, id):
        try:
            chain = AlertingChain.objects.get(pk=id)
            if chain.node.owner == owner:
                chain.delete()
                return True
            else:
                return False
        except:
            return False


class AlertLog(models.Model):
    node = models.ForeignKey(Node, blank=False)
    event_date = models.DateTimeField(null=True, blank=True, default=timezone.now())
    reported_status = models.PositiveIntegerField(choices=STATUS_CHOICES)

    def get_status_text(self):
        return self.node.cls_get_status_text(self.reported_status)

    @classmethod
    def alerted_recently(cls, node, status):
        now = timezone.now()
        alerts = AlertLog.objects.filter(node=node, reported_status=status).order_by('-event_date')
        if alerts:
            alert = alerts[0]
            if (now - alert.event_date).seconds / 60 > settings.ALERT_QUIET_PERIOD_MINUTES:
                return False
            else:
                return True
        else:
            return False
