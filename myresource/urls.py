from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    (r'^', include('shared.apps.base.urls')),
    (r'^account/', include('shared.apps.account.urls')),
    (r'^client/', include('myresource.apps.client.urls')),
    (r'^oauth2/', include('myresource.apps.oauth2.urls')),
    (r'^api/', include('myresource.apps.api.urls')),
)
