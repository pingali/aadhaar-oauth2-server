#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('shared.apps.base.views',
    (r'^/?$',                      'homepage'),
)
