from fpmonitor.models import Node

from django.core.management.base import NoArgsCommand
from django.conf import settings


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        nodes = Node.objects.filter(maintenance_mode=False)
        for node in nodes:
            node.update_status_if_required()
