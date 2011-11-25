#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('myclient.apps.api.views',
    (r'^date_joined/?$',           'date_joined'),
    (r'^last_login/?$',            'last_login'),
    (r'^email/?$',                 'email'),
    (r'^remote/date_joined/?$',    'remote', {'target_method': 'date_joined'}),
    (r'^remote/last_login/?$',     'remote', {'target_method': 'last_login'}),
    (r'^remote/email/?$',          'remote', {'target_method': 'email'}),
)
