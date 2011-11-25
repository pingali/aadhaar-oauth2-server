#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('myclient.apps.account.views',
    (r'^login/?$',                  'login'),
    (r'^logout/?$',                 'logout'),
    (r'^signup/?$',                 'signup'),
    (r'^clients/?$',                'clients'),
    (r'^aadhaar/authenticate/?$',    'aadhaar_login'),
)
