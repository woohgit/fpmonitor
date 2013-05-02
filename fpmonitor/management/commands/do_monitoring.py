from datetime import timedelta

from django.core.management.base import NoArgsCommand
from django.conf import settings


def get_uptime_seconds():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
