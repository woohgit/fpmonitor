from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'fpmonitor.views.home', name='home'),
    url(r'^index$', 'fpmonitor.views.index', name='index'),
    url(r'^login$', 'fpmonitor.views.user_login', name='login'),
    url(r'^logout$', 'fpmonitor.views.user_logout', name='logout'),
    url(r'^api/v1/node/maintenance_mode$', 'fpmonitor.views.api_node_maintenance', name='api_node_maintenance'),
)

urlpatterns += patterns(
    '',
    (r'^', include('fpmonitor.test_api.urls')),
)
