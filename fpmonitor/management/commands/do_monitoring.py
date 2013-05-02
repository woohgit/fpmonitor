from datetime import timedelta
import os
from fpmonitor.common import get_system_load, get_system_uptime_in_seconds

from django.core.management.base import NoArgsCommand
from django.conf import settings


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        request = {}
        request['uptime'] = get_system_uptime_in_seconds()
        request['loadavg'] = get_system_load()
        print request
