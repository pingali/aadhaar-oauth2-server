#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('myclient.apps.base.views',
    (r'^/?$',                      'homepage'),
)
