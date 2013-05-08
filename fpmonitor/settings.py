from os.path import abspath, dirname
from django_configglue.utils import update_settings
from fpmonitor.schema import FpMonitorSchema
from config.config import init_settings
import warnings


INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.sites', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.admin', 'django.contrib.databrowse', 'compressor', 'fpmonitor']

init_settings('fpmonitor', FpMonitorSchema, abspath(dirname(__file__)))

from config.config import settings

update_settings(settings, __name__)

warnings.filterwarnings('error', r"DateTimeField received a naive datetime", RuntimeWarning, r'django\.db\.models\.fields')
