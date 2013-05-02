from datetime import timedelta
import os
from fpmonitor.common import (get_distribution, get_release, get_system,
                              get_system_load, get_system_uptime_in_seconds)

from django.core.management.base import NoArgsCommand
from django.conf import settings


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        request = {}
        request['uptime'] = get_system_uptime_in_seconds()
        request['loadavg'] = get_system_load()
        request['system'] = get_system()
        request['kernel'] = get_release()
        request['distribution'] = get_distribution()
        print request
