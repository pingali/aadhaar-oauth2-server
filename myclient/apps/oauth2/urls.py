#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
        (r'^missing_redirect_uri/?$',   'myclient.apps.oauth2.views.missing_redirect_uri'),
        (r'^authorize/?$',              'myclient.apps.oauth2.views.authorize'),
        (r'^authorize/aadhaar/?$',              'myclient.apps.oauth2.views.authorize', {'aadhaar': True} ),
        (r'^token/?$',                  'oauth2app.token.handler'),
)
