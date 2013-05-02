from django.conf.urls import patterns
from . import test_api

# Test API
urlpatterns = patterns(
    '',
    (r'^test_api/create_nodes/(?P<node_count>[0-9]+)/(?P<status>[0-9])$', test_api.create_nodes),
    (r'^test_api/create_nodes/(?P<node_count>[0-9]+)/(?P<status>[0-9])/(?P<name>[a-z0-9]+)$', test_api.create_nodes),
    (r'^test_api/cleanup_nodes$', test_api.cleanup_nodes),
    (r'^test_api/test_mode_off$', test_api.test_mode_off),
    (r'^test_api/test_mode_on$', test_api.test_mode_on),
)
