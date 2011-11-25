from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    (r'^', include('myclient.apps.base.urls')),
    (r'^account/', include('shared.apps.account.urls')),
    (r'^client/', include('myclient.apps.client.urls')),
    (r'^oauth2/', include('myclient.apps.oauth2.urls')),
    (r'^api/', include('myclient.apps.api.urls')),
)