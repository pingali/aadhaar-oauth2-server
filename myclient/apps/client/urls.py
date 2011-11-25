#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('myclient.apps.client.views',
    (r'^forward/?$',            'forward'),
    (r'^request/(?P<req_id>\w+)/?$',    'request'),
    (r'^request_token$',              'request_token'),
    (r'^refresh_token$',              'refresh_token'),
    (r'^(?P<client_id>\w+)/?$', 'client'),
)# Create your views here.
