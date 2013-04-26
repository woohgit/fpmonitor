import logging
import os
import unittest

from coverage.control import coverage
from django.conf import settings
from django.db.models import get_app, get_apps
from django.test.simple import DjangoTestSuiteRunner, build_suite, build_test, get_tests, reorder_suite
from django.test.testcases import TestCase
import xmlrunner


def get_non_django_apps():
    apps = get_apps()
    ignored_apps = ['%s.models' % app for app in getattr(settings, 'TEST_IGNORE_APPS', [])]
    non_django_apps = [app for app in apps if not app.__name__.startswith('django.') and app.__name__ not in ignored_apps]
    return non_django_apps


class TestSuiteRunner(DjangoTestSuiteRunner):

    def __init__(self, verbosity=1, interactive=True, failfast=True, **kwargs):
        super(TestSuiteRunner, self).__init__(verbosity, interactive, failfast, **kwargs)
        if getattr(settings, 'TEST_WITH_COVERAGE', False):
            omit_list = [
                '%s/lib/*' % os.environ['VIRTUAL_ENV'],  # libraries
                '%s/src/*' % os.environ['VIRTUAL_ENV'],  # source libraries
                '*/tests*',  # all tests
            ]
            self.coverage = coverage(branch=True, omit=omit_list)
            self.coverage_format = getattr(settings, 'TEST_COVERAGE_FORMAT', 'xml')
        else:
            self.coverage = None

    def setup_test_environment(self, **kwargs):
        super(TestSuiteRunner, self).setup_test_environment(**kwargs)
        if not getattr(settings, 'TEST_ENABLE_LOGGING', False):
            logging.disable(logging.CRITICAL)
        if self.coverage:
            self.coverage.start()

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()

        if test_labels:
            for label in test_labels:
                if '.' in label:
                    try:
                        suite.addTest(build_test(label))
                    except ValueError:
                        # Try our own discovery mechanism (suited for the
                        # dynamic test loader).
                        suite.addTest(build_test_from_dynamic(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_non_django_apps():
                suite.addTest(build_suite(app))

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))

    def teardown_test_environment(self, **kwargs):
        super(TestSuiteRunner, self).teardown_test_environment(**kwargs)
        if self.coverage:
            self.coverage.stop()
            if self.coverage_format == 'xml':
                output_file = getattr(settings, 'TEST_COVERAGE_OUTPUT_XML',
                                      'reports/coverage.xml')
                self.coverage.xml_report(outfile=output_file)
            elif self.coverage_format == 'html':
                output_dir = getattr(settings, 'TEST_COVERAGE_OUTPUT_HTML',
                                     'reports/coverage/')
                self.coverage.html_report(directory=output_dir)


class DjangoXMLTestRunner(TestSuiteRunner):

    def run_suite(self, suite, **kwargs):
        verbose = getattr(settings, 'TEST_OUTPUT_VERBOSE', False)
        descriptions = getattr(settings, 'TEST_OUTPUT_DESCRIPTIONS', False)
        output = getattr(settings, 'TEST_OUTPUT_DIR', '.')
        return xmlrunner.XMLTestRunner(
            verbose=verbose,
            descriptions=descriptions,
            output=output).run(suite)
