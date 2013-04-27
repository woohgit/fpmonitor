from datetime import datetime
from fpmonitor.consts import *
from django.contrib.auth.models import User
from django.db import models


class Node(models.Model):

    owner = models.ForeignKey(User, blank=False)
    registered_at = models.DateTimeField(null=True, blank=True, default=datetime.now())
    last_sync = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=250, blank=False)
    os_type = models.CharField(max_length=250)
    os_version = models.CharField(max_length=250)
    kernel_version = models.CharField(max_length=250)
    maintenance_mode = models.BooleanField(default=False)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=STATUS_UNKNOWN)

    @classmethod
    def get_nodes(cls, owner):
        return Node.objects.filter(owner=owner)

    @classmethod
    def create_node(cls, owner, name):
        node = Node.objects.create(owner=owner, name=name, os_type='Linux', os_version='Ubuntu')
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
