#-*- coding: utf-8 -*-


from django.shortcuts import render_to_response
from django.template import RequestContext
from oauth2app.models import Client, AccessToken
import time 

def homepage(request):
    template = {}
    if request.user.is_authenticated():
        now = int(time.time())
        clients = Client.objects.filter() #user=request.user)
        access_tokens = AccessToken.objects.filter(#user=request.user, 
                                                   expire__gt=now)
        access_tokens = access_tokens.select_related()
        template["access_tokens"] = access_tokens
        template["clients"] = clients
    return render_to_response(
        'base/homepage.html', 
        template, 
        RequestContext(request))
