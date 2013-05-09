from django.utils import timezone
from fpmonitor.consts import *
from django.contrib.auth.models import User
from django.db import models, IntegrityError


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
                result = ((now - self.last_sync).seconds) / 60
        except Exception as e:
            result = e
        return result

    def check_alerting_level(self, status, threshold_load, threshold_seen):
        # TODO: wooh - here goes the logic!
        # ha a load nagyobb mint 5
        # ha a get_last_seen_in_minutes > 6
        if (int(float(self.loadavg_5)) >= threshold_load or int(float(self.loadavg_10)) >= threshold_load or int(float(self.loadavg_15)) >= threshold_load):
            self.status = status
            self.save()
            return True

        if (self.get_last_seen_in_minutes() >= threshold_seen):
            self.status = status
            self.save()
            return True

        return False

    def update_status_if_required(self):

        if self.check_alerting_level(STATUS_ERROR, ALERT_DANGER_LOAD, ALERT_DANGER_SEEN):
            return
        if self.check_alerting_level(STATUS_WARNING, ALERT_WARNING_LOAD, ALERT_WARNING_SEEN):
            return
        if self.check_alerting_level(STATUS_INFO, ALERT_INFO_LOAD, ALERT_INFO_SEEN):
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

        # use a bigger perspective. We're not interested in seconds as of now
        if days == 0:
            return "%d hour(s), %d minute(s)" % (hours, minutes)

        # use a more bigger perspective. We're not interested in minutes and seconds as of now
        return "%d day(s), %d hour(s)" % (days, hours)
