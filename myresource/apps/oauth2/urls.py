#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
        (r'^missing_redirect_uri/?$',   'myresource.apps.oauth2.views.missing_redirect_uri'),
        (r'^authorize/?$',              'myresource.apps.oauth2.views.authorize'),
        (r'^authorize/aadhaar/?$',              'myresource.apps.oauth2.views.authorize_aadhaar'),
        (r'^token/?$',                  'oauth2app.token.handler'),
)
