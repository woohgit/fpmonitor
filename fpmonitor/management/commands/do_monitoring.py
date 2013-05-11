from datetime import timedelta
import json
import os
import urllib2

from fpmonitor.common import (get_distribution, get_memory_usage, get_release, get_system,
                              get_system_load, get_system_uptime_in_seconds)

from django.core.management.base import NoArgsCommand
from django.conf import settings


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        data = {}
        data['node_name'] = settings.NODE_NAME
        data['node_user_id'] = settings.NODE_USER_ID
        data['uptime'] = get_system_uptime_in_seconds()
        data['uptime'] = 1000
        data['loadavg'] = get_system_load()
        data['system'] = get_system()
        data['kernel'] = get_release()
        data['distribution'] = get_distribution()
        data['memory_usage'] = get_memory_usage()
        post_data = json.dumps(data)

        request = urllib2.Request("%s/receive_data" % (settings.SERVER_HOST, ), data='data=%s' % post_data)
        result = urllib2.urlopen(request).read()
        if "NOK" in result:
            print "Error: invalid credentials"
