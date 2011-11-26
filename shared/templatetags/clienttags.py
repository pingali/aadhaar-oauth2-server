from django import template
from django.utils.timesince import timesince
from datetime import datetime
import time 

register = template.Library()

def timedelta(value_timestamp, arg=None):
    if not value_timestamp:
        return ''
    value = datetime.utcfromtimestamp(value_timestamp)
    if arg:
        cmp = datetime.utcfromtimestamp(arg)
    else:
        cmp = datetime.utcnow()
    if value > cmp:
        msg = "in %s" % timesince(cmp,value)
    else:
        msg = "%s ago" % timesince(value,cmp)
    return msg 
    
register.filter('timedelta',timedelta)

