import os

import django
from django_configglue.schema import schemas
from configglue.schema import *

from config.schema import SettingsSchema

DjangoSchema = schemas.get(django.get_version())


class FpMonitorSchema(DjangoSchema, SettingsSchema):
    virtualenv_dir = StringOption(fatal=True)

    class testing(Section):
        test_coverage_format = StringOption(default='html')
        test_enable_logging = BoolOption(default=False)
        test_ignore_apps = ListOption(item=StringOption(), default=['django_configglue', 'compressor', 'django_extensions'])
        test_output_descriptions = BoolOption(default=False)
        test_output_dir = StringOption()
        test_output_verbose = BoolOption(default=False)
        test_with_coverage = BoolOption(default=False)
        tets_mode = BoolOption(default=False)
