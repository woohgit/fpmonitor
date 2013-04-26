import copy
import os
import sys

from configglue.parser import SchemaConfigParser

settings = None


class ConfigSection(object):
    def __init__(self, config_parser, section_name):
        super(ConfigSection, self).__init__()
        self.parser = config_parser
        self.section_name = section_name

    def __getitem__(self, option_name):
        return self.parser.get(section=self.section_name, option=option_name)


class ConfigParser(SchemaConfigParser):
    def __getitem__(self, section):
        return ConfigSection(config_parser=self, section_name=section)

    @property
    def shared_secret(self):
        return str(self['__main__']['shared_secret'])

    @property
    def project_dir(self):
        return str(self['__main__']['project_dir'])

    def get_state(self):
        return copy.deepcopy(self._sections)

    def set_state(self, state):
        self._sections = state


def config_files(project_dir, project_name):
    files = ['etc/config.cfg']

    for file in files:
        # if the path is not absolute, append to the project_dir
        if not os.path.isabs(file):
            file = os.path.join(project_dir, file)
        yield file


def init_settings(name, schema, project_dir):

    parser = ConfigParser(schema())
    parser.set('__main__', 'project_dir', project_dir)

    parser.read(config_files(project_dir, name))
    parser.parse_all()

    is_valid, reasons = parser.is_valid(report=True)

    if not is_valid:
        sys.stderr.write("WARNING: Schema validation errors:\n")
        for reason in reasons[0:100]:
            sys.stderr.write("    {0}\n".format(reason))
        sys.stderr.write("\n\n\n")

    global settings
    settings = parser


def debug(message):
    sys.stderr.write("{0}\n".format(message))


config_module = os.environ.get('DJANGO_SETTINGS_MODULE', None) or 'settings'
if config_module == 'None':
    debug("[settings] Skip: config_module == 'None'")
else:
    if 'settings' in sys.modules:
        debug("[settings] Skip: 'settings' already loaded")
    else:
        if config_module not in sys.modules:
            debug("[settings] Importing '{0}".format(config_module))
            __import__(config_module, fromlist=[], level=0)
