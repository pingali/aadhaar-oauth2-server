#-*- coding: utf-8 -*-

from oauth2app.authenticate import JSONAuthenticator, AuthenticationException
from oauth2app.models import AccessRange
from oauth2app.models import Client, AccessToken, Code
import traceback 

def date_joined(request):
    scope = AccessRange.objects.get(key="date_joined")
    authenticator = JSONAuthenticator(scope=scope)
    try:
        authenticator.validate(request)
    except AuthenticationException:
        return authenticator.error_response()
    
    response = authenticator.response({
            "date_joined":str(authenticator.user.date_joined)})
    print "response = ", response 
    return response 
    
    
def last_login(request):
    print "in last_login" 
    scope = AccessRange.objects.get(key="last_login")
    authenticator = JSONAuthenticator(scope=scope)
    try:
        authenticator.validate(request)
    except AuthenticationException:
        return authenticator.error_response()
    response = authenticator.response({
            "last_login":str(authenticator.user.last_login)})
    print "returning ", response
    return response

def email(request):
    print "in email" 
    authenticator = JSONAuthenticator()
    try:
        authenticator.validate(request)
    except AuthenticationException:
        return authenticator.error_response()
    response = authenticator.response({"email":authenticator.user.email})    
    print "returning ", response 
    return response
