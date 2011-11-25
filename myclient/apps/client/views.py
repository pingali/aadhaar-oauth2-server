#-*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings 
from django.template import RequestContext
from oauth2app.models import Client, AccessToken, Code, AccessRange, TimestampGenerator
from base64 import b64encode
from django.contrib.auth.decorators import login_required
from .models import OauthRequest 
from django.conf import settings
import simplejson as json
import requests
import traceback 
from urllib import urlencode 

"""
Interact with the client. 
"""
@login_required 
def client(request, client_id):
    """
    Show the client details, available codes and access tokens for a
    given client.     
    """
    # XXX The client should eventually be decoupled from the user
    # account information.

    print "In apps.client.views.client - entered" 
    client = Client.objects.get(key=client_id)
    template = {
        "client":client,
        "basic_auth":"Basic %s" % b64encode(client.key + ":" + client.secret),
        "codes":Code.objects.filter(client=client).select_related(),
        "access_tokens":AccessToken.objects.filter(client=client).select_related()}
    template["error_description"] = request.GET.get("error_description")
    return render_to_response(
        'client/client.html', 
        template, 
        RequestContext(request))

# Login not required. 
def request(request, req_id):
    """
    Receive an authorization code from the server. The request object
    is used to generate the URL.
    """
    
    # client => server : create account
    # server => client: client configuration 
    # client => server: authorize request 
    # server => client: respond with authorization code 

    # XXX Rationalize the URL. Right now it is client/request/aaa
    # it could easily be request/aaa or callback/aaa 
    print "In apps.client.views.request - entered" 

    # The oauthRequest object is the state object for the request. It
    # keeps track of what the user asked and is updated when new
    # information is received from the server. Lookup that object
    # first.
    req = OauthRequest.objects.get(key=req_id)
    print "Found request = ", vars(req)
    try: 
        
        # Find the code 
        code_key = request.GET.get('code')
        print "Received code = ", code_key
        
        #=> Check if the code exists.
        try: 
            code = Code.objects.get(key=code_key)
        except:
            code = None
            pass
        
        if code is not None: 
            # Giving token refresh request triggers a callback to this
            # looks like (based on the redirect_uri specified") 
            raise Exception("Duplicate code returned") 
        
        # XXX expire is set automatically. But eventually it must be
        # transmitted from the server. For some reason the server is
        # not sending the expiration information. 
        code = Code.objects.create(user=req.user, 
                                   client=req.client,
                                   redirect_uri=request.path, 
                                   key=code_key)
        # copy the scope information into the code from the initial
        # request. This information is not available in the callback
        # from the server
        code.scope.add(*req.scope.all())
        code.save() 

        print "saved code = ", vars(code) 
        print "code scope = ", code.scope 
        # XXX This is not being used. May be it can be removed. 
        req.completed = TimestampGenerator()() 
        req.code = code_key # we dont store code object because it
                            # will be deleted
        req.save()
        print "saved request = ", vars(req) 

    except:
        traceback.print_exc() 
        pass
    
    #client = Client.objects.all()[:1][0]
    client = req.client 

    # Add this to the code objects 
    template = {
        "client":client,
        "basic_auth":"Basic %s" % b64encode(client.key + ":" + client.secret),
        "codes":Code.objects.filter(client=client).select_related(),
        "access_tokens":AccessToken.objects.filter(client=client).select_related()}
    template["error_description"] = request.GET.get("error_description")
    return render_to_response(
        'client/client.html', 
        template, 
        RequestContext(request))


@login_required 
@csrf_exempt
def request_token(request): 
    """
    Handle the request from the user to obtain an access token for a
    given code.
    """ 
    print "Trying to obtain a token" 

    
    if request.method != "GET": 
        return HttpResponseRedirect("/")
    
    try:
        
        params = {} 

        # extract the user-specified code 
        params['code'] = request.GET.get('code')
        
        # Obtain the state objects 
        code = Code.objects.get(key=params['code'])
        req = OauthRequest.objects.get(code=params['code'])
        client = req.client 
        #client = Client.objects.all()[:1][0] 
        print "Client object = ", vars(client) 
        print "Code object = ", vars(code) 
        
        # set the standard parameters 
        params['client_id'] = settings.RESOURCE_CLIENT_KEY         
        params['grant_type'] = 'authorization_code'         
        
        # Ignore the redirect_uri because we dont need a call back. The 
        # json response is enough. 
        #params['redirect_uri'] = settings.CLIENT_SITE + code.redirect_uri
        
        # XXX set the scope. Not sure if this the best way. 
        print "type req.scope.all() = ", type(req.scope.all())
        all_keys = [s.key for s in req.scope.all()]
        print "all_scopes = ", all_keys
        if len(all_keys) > 0: 
            params['scope'] = all_keys[0] # XXX should be a join(",") instead?
        else:
            params['scope'] = ""

        print "Sending data = ", params         
        
        client_key = settings.RESOURCE_CLIENT_KEY
        client_secret = settings.RESOURCE_CLIENT_SECRET
        print "Client_key = ", client_key
        print "Client secret=", client_secret 
        basic_auth = "Basic %s" % b64encode(client_key + ":" + client_secret)
        print "computed authorization = ", basic_auth
        
        # Constructing the call 
        url = settings.ACCESS_TOKEN_URL + "/?" + urlencode(params)
        headers = { 'Authorization': basic_auth } 

        print "url = ", url 
        print "headers = ", headers 

        # There is nothing in the body. There is only a post - which
        # for some reason seems to turn into a GET at the other end. 
        r = requests.post(url, data="", headers=headers)
        print "received headers = ", r.headers 
        if r.headers['content-type'] != 'application/json':
            raise Exception("Possible error in request to the server")
        
        #=> Now store the token for future access purposes 
        grant_data = json.loads(r.content)
        print "grant data = ", grant_data
        
        # Create an access token.  There is no place, it seems for a
        # token_type (bearer etc.)
        access_token = \
            AccessToken.objects.create(user=request.user, 
                                       client=client, 
                                       token=grant_data['access_token'],
                                       refresh_token=grant_data['refresh_token'],
                                       # token_type=gr['token_type'],
                                       # scope=grant_data['scope']
                                       )
        # Should be this [grant_data['scope']]? 
        access_ranges = list(AccessRange.objects.filter(key__in=grant_data['scope']))
        access_token.scope = access_ranges
        access_token.save() 
        
        # Update the state 
        req.refresh_token = grant_data['refresh_token'] 
        req.token = grant_data['access_token'] 
        req.save() 
        print "access token = ", vars(access_token) 
        
        # Clean up 
        code.delete() 
        
    except:
        traceback.print_exc() 
        pass
    
    # redirect 
    HttpResponseRedirect(settings.CLIENT_SITE + "/client/%s" % client.key)

# Helper functions
def get_auth(auth_type='basic'): 
    if auth_type != "basic": 
        raise Exception("Unknown authentication type asked for")
                        
    client_key = settings.RESOURCE_CLIENT_KEY
    client_secret = settings.RESOURCE_CLIENT_SECRET
    print "Client_key = ", client_key
    print "Client secret=", client_secret 
    basic_auth = "Basic %s" % b64encode(client_key + ":" + client_secret)
    print "computed authorization = ", basic_auth
    return basic_auth 

@login_required 
@csrf_exempt
def refresh_token(request): 
    """
    Handle a request from the user for refreshing a token. 
    """
    # <form method="post" action="http://localhost:8000/oauth2/token" 
    #                class="authenticate">
    # <input type="hidden" name="grant_type" value="refresh_token" />
    # <input type="hidden" name="refresh_token" value="38d6122e30" />
    # <input type="hidden" name="client_id" value="d53d90894c157ab" />
    # <input type="hidden" name="scope" value="" />
    # <input type="submit" value="38d6122e30"/>
    # </form>

    if request.method != "GET": 
        return HttpResponseRedirect("/")
    
    # Obtain and lookup a refresh token 
    refresh_token_key = request.GET.get('refresh_token')
    try: 
        token = AccessToken.objects.get(refresh_token=refresh_token_key) 
        req = OauthRequest.objects.get(refresh_token=refresh_token_key) 
        client = req.client
    except: 
        traceback.print_exc() 
        raise Exception("Invalid refresh token") 
    
    # Start constructing the request that must be sent to the resource
    # server.
    params = {} 
    params['client_id'] = settings.RESOURCE_CLIENT_KEY         
    params['grant_type'] = 'refresh_token'
    params['refresh_token'] = token.refresh_token 
    
    # Dont need to specify the redirect_uri as we dont need a call
    # back from the server. Just the json response is enough.
    #params['redirect_uri'] = \
    #    "http://%s/client/request/%s" % (request.get_host(), req.key)

    print "type req.scope.all() = ", type(req.scope.all())
    #=> set the scope of the refresh. Not sure why scope is required
    # again because it has been specific while obtaining the
    # authorization. The scope cant be any different. 
    all_keys = [s.key for s in req.scope.all()]
    print "all_scopes = ", all_keys
    if len(all_keys) > 0: 
        params['scope'] = all_keys[0]
    else:
        params['scope'] = ""
        
    print "params = ", params 
    
    # Obtain the authentication 
    basic_auth = get_auth() 
    headers = { 'Authorization': basic_auth } 
    print "headers = ", headers 
    
    # Constructing the call 
    url = settings.ACCESS_TOKEN_URL + "/?" + urlencode(params)
    print "url = ", url 

    # Call the server 
    r = requests.post(url, data="", headers=headers)
    print "received headers = ", r.headers 
    if r.headers['content-type'] != 'application/json':
        raise Exception("Possible error in request to the server")
        
    # => Now store the token for future access purposes 
    grant_data = json.loads(r.content)
    print "grant data = ", grant_data
    
    # => Update the token state 
    token.token = grant_data['access_token']
    token.refresh_token = grant_data['refresh_token']
    token.save() 
    
    # Update the request state 
    req.token = grant_data['access_token']
    req.refresh_token = grant_data['refresh_token']
    req.save() 

    return HttpResponseRedirect("/client/%s" % client.key)
    

@login_required 
def forward(request): 
    """
    Request authorization from the resource server. First create a
    OauthRequest object to store local state and use when the callback
    is obtained. 
    """
    
    # The request from the user is coming in the form a get. It must
    # specify whether aadhaar must be used for authorization. 
    
    # XXX change /client/forward to something else. may be request_code 
    if request.method != "GET": 
        return HttpResponseRedirect(nexturl)

    print "request parameters = ", request.GET 
    
    # Figure out if this request is aadhaar 
    try: 
        aadhaar = False
        aadhaar_str = request.GET.get('aadhaar')
        if aadhaar_str == "True":
            aadhaar = True
    except:
        pass
    
    print "aadhaar = ", aadhaar, type(aadhaar) 

    # Some dummy client. It does not matter. 
    # XXX change this if you need to support multiple clients. 
    client = Client.objects.all()[:1][0]
    if client == None: 
        raise Exception("Could not find a suitable client") 

    user = request.user 
    scope_key = request.GET.get('scope')
    print "scope key = ", scope_key, type(scope_key) 
    if ((scope_key is not None) and (scope_key != "None")):
        access_ranges = list(AccessRange.objects.filter(key__in=[scope_key]))
    else:
        access_ranges = []
    response_type = 'code'
    
    # Now create the request. 
    req = OauthRequest.objects.create(client=client,
                                      user=user, 
                                      #aadhaar=aadhaar,
                                      response_type=response_type)

    req.scope = access_ranges
    req.save() 
    print "created request object ", req, "with key ", req.key 

    # Construct the request 
    #params = request.GET.copy()
    params = {} 
    params['response_type'] = response_type
    params['client_id'] = settings.RESOURCE_CLIENT_KEY 
    if scope_key is not None: 
        params['scope'] = scope_key 
    params['redirect_uri'] = "http://%s/client/request/%s" % (request.get_host(), req.key)
    
    # Construct the url 
    url = urlencode(params)
    if aadhaar: 
        next = "%s?%s" % (settings.AADHAAR_AUTHORIZE_URL, url)
    else:
        next = "%s?%s" % (settings.AUTHORIZE_URL, url)
    print "Updated parameters = ", params 
    print "Redirecting to ", next 

    print "redirecting the request to ", next 
    return HttpResponseRedirect(next) 
