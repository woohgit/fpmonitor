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
)

urlpatterns += patterns(
    '',
    (r'^', include('fpmonitor.test_api.urls')),
)
