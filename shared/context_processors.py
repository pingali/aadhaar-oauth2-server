#!/usr/bin/env python 

from django.conf import settings

def myclient_context(request):
    mysite = settings.MYSITE
    mysite_role = settings.MYSITE_ROLE
    authorize_url = settings.AUTHORIZE_URL 
    access_token_url = settings.ACCESS_TOKEN_URL
    aadhaar_authorize_url = settings.AADHAAR_AUTHORIZE_URL 
    myhost = request.get_host() 
    resource_name = settings.RESOURCE_NAME
    resource_server = settings.RESOURCE_SERVER
    resource_client_key = settings.RESOURCE_CLIENT_KEY 
    resource_client_secret = settings.RESOURCE_CLIENT_SECRET
    template = {'mysite': mysite,
                'mysite_role': mysite_role,
                'myhost': myhost,
                'authorize_url': authorize_url,
                'access_token_url': access_token_url, 
                'aadhaar_authorize_url': aadhaar_authorize_url,
                'resource_server': resource_server,
                'resource_name': resource_name,
                'resource_client_key': resource_client_key, 
                'resource_client_secret': resource_client_secret}

    #print "mysite_context = ", template 
    return template 

def myresource_context(request):
    mysite = settings.MYSITE
    mysite_role = settings.MYSITE_ROLE
    authorize_url = settings.AUTHORIZE_URL 
    access_token_url = settings.ACCESS_TOKEN_URL
    aadhaar_authorize_url = settings.AADHAAR_AUTHORIZE_URL 
    myhost = request.get_host() 
    resource_server = settings.RESOURCE_SERVER
    template = {'mysite': mysite,
                'mysite_role': mysite_role,
                'myhost': myhost,
                'authorize_url': authorize_url,
                'access_token_url': access_token_url, 
                'aadhaar_authorize_url': aadhaar_authorize_url,
                'resource_server': resource_server}
    #print "myresource_context = ", template 
    return template 

