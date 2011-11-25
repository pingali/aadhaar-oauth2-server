#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('myresource.apps.account.views',
    (r'^login/?$',                  'login'),
    (r'^logout/?$',                 'logout'),
    (r'^signup/?$',                 'signup'),
    (r'^clients/?$',                'clients'),
    (r'^download/(?P<client_id>\w+)/?$',  'download'),
    (r'^aadhaar/authenticate/?$',    'aadhaar_login'),
)
