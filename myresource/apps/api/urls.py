#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('myresource.apps.api.views',
    (r'^date_joined/?$',           'date_joined'),
    (r'^last_login/?$',            'last_login'),
    (r'^email/?$',                 'email')
)
