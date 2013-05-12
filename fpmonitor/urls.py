from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'fpmonitor.views.home', name='home'),
    url(r'^index$', 'fpmonitor.views.index', name='index'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'password_change.html', 'post_change_redirect': '/index'}),
    url(r'^login$', 'fpmonitor.views.user_login', name='login'),
    url(r'^logout$', 'fpmonitor.views.user_logout', name='logout'),
    url(r'^api/v1/node/maintenance_mode$', 'fpmonitor.views.api_node_maintenance', name='api_node_maintenance'),
    url(r'^receive_data$', 'fpmonitor.views.receive_data', name='receive_data'),
)

urlpatterns += patterns(
    '',
    (r'^', include('fpmonitor.test_api.urls')),
)
