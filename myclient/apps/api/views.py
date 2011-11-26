#-*- coding: utf-8 -*-


from oauth2app.authenticate import JSONAuthenticator, AuthenticationException
from oauth2app.models import AccessRange
import requests
from django.http import HttpResponseRedirect, HttpResponse

def remote(request, target_method):
    print "remote api call for %s" % target_method
    
    # copy the authorization header
    auth = request.META['HTTP_AUTHORIZATION']
    headers = { 'Authorization': auth }
    
    # construct the url 
    url = "http://localhost:8000/api/%s" % target_method
    r = requests.get(url, data="", headers=headers)
    print r.headers 
    
    # Check the header
    if r.headers['content-type'] != 'application/json':
        raise Exception("Possible error in request to the server")

    # Generate the response.
    try: 
        callback=request.GET.get('callback')
        json_data = "%s(%s);" % (callback, r.content)
    except: 
        json_data = r.content 
        pass 

    print "Responding with ", json_data
    response = HttpResponse(json_data, 
                            content_type="application/json")
    return response 

def remote_date_joined(request):
    raise Exception("nothing here")

def remote_email(request):
    raise Exception("nothing here")

def date_joined(request):
    scope = AccessRange.objects.get(key="date_joined")
    authenticator = JSONAuthenticator(scope=scope)
    try:
        authenticator.validate(request)
    except AuthenticationException:
        return authenticator.error_response()
    return authenticator.response({
        "date_joined":str(authenticator.user.date_joined)})
    
    
def last_login(request):
    scope = AccessRange.objects.get(key="last_login")
    authenticator = JSONAuthenticator(scope=scope)
    try:
        authenticator.validate(request)
    except AuthenticationException:
        return authenticator.error_response()
    data = {"date_joined":str(request.user.date_joined)}
    return authenticator.response({
        "last_login":str(authenticator.user.last_login)})


def email(request):
    authenticator = JSONAuthenticator()
    try:
        authenticator.validate(request)
    except AuthenticationException:
        return authenticator.error_response()
    return authenticator.response({"email":authenticator.user.email})    
