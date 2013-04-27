from django.conf.urls import patterns
from . import test_api

# Test API
urlpatterns = patterns(
    '',
    (r'^test_api/create_nodes/(?P<node_count>[0-9]+)/$', test_api.create_nodes),
    (r'^test_api/cleanup_nodes$', test_api.cleanup_nodes),
)
