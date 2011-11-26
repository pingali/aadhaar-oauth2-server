#-*- coding: utf-8 -*-
"""
Interact with the client. 
"""
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse 
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
import logging 

#=================================================================
# Prevent sql commands from being printed out for this section...
from django.conf import settings
from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper

if settings.DEBUG:
    BaseDatabaseWrapper.make_debug_cursor = lambda self, cursor: CursorWrapper(cursor, self)
#==================================================================

log = logging.getLogger("myclient.apps.client.views") 

@login_required 
def client(request, client_id):
    """
    Show the client details, available codes and access tokens for a
    given client.     
    """
    # XXX The client should eventually be decoupled from the user
    # account information.

    log.debug("In apps.client.views.client - entered")
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
    log.debug("In apps.client.views.request - entered")
    if request.META.has_key('HTTP_REFERRER'):
        log.debug("Referrer = %s " % (request.META['HTTP_REFERRER']))

    try: 

        # The oauthRequest object is the state object for the request. It
        # keeps track of what the user asked and is updated when new
        # information is received from the server. Lookup that object
        # first.
        req = OauthRequest.objects.get(key=req_id)
        log.debug("Found request = %s " % vars(req))
        
        # Find the code 
        code_key = request.GET.get('code')
        log.debug("Received code = %s " % code_key)
        
        # => Check where the code has been used. Code object has been 
        # deleted. So it cant be used. This is a hack to make things
        # work with oauth2app 
        if ((req.code == code_key) and (req.completed != 0)): 
            log.error("Duplicate callback. Should not come here") 
            raise Exception("Code already used") 
        
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

        log.debug("saved code = %s " % vars(code))
        log.debug("code scope = %s " % code.scope)
        # XXX This is not being used. May be it can be removed. 
        req.completed = TimestampGenerator()() 
        req.code = code_key # we dont store code object because it
                            # will be deleted
        req.save()
        log.debug("saved request = %s " % vars(req))

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


# Helper functions
def get_auth(auth_type='basic'): 
    if auth_type != "basic": 
        raise Exception("Unknown authentication type asked for")
                        
    client_key = settings.RESOURCE_CLIENT_KEY
    client_secret = settings.RESOURCE_CLIENT_SECRET
    log.debug("Client_key = %s " % client_key)
    log.debug("Client secret= %s" % client_secret)
    basic_auth = "Basic %s" % b64encode(client_key + ":" + client_secret)
    log.debug("computed authorization = %s " % basic_auth)
    return basic_auth 

@login_required 
@csrf_exempt
def request_token(request): 
    """
    Handle the request from the user to obtain an access token for a
    given code.
    """ 
    log.debug("Trying to obtain a token")
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
        log.debug("Client object = %s " % vars(client))
        log.debug("Code object = %s " % vars(code))
        
        # set the standard parameters 
        params['client_id'] = settings.RESOURCE_CLIENT_KEY         
        params['grant_type'] = 'authorization_code'                 
        params['redirect_uri'] = \
            "http://%s/client/request/%s" % (request.get_host(), req.key)

        # XXX set the scope. Not sure if this the best way. 
        log.debug("type req.scope.all() = %s " % type(req.scope.all()))
        all_keys = [s.key for s in req.scope.all()]
        log.debug("all_scopes = %s " % all_keys)
        if len(all_keys) > 0: 
            params['scope'] = all_keys[0] # XXX should be a join(",") instead?
        else:
            params['scope'] = ""

        log.debug("Sending data = %s " % params)
        
        # Obtain the authentication 
        basic_auth = get_auth() 
        headers = { 'Authorization': basic_auth } 
        log.debug("headers = %s " % headers)

        # Constructing the call 
        url = settings.ACCESS_TOKEN_URL + "/?" + urlencode(params)
        log.debug("url = %s " % url)

        # There is nothing in the body. There is only a post - which
        # for some reason seems to turn into a GET at the other end. 
        r = requests.post(url, data="", headers=headers)
        log.debug("received headers = %s " % r.headers)
        if r.headers['content-type'] != 'application/json':
            log.error("Received error from server %s" % r.content)
            raise Exception("Possible error in request to the server")
        
        #=> Now store the token for future access purposes 
        grant_data = json.loads(r.content)
        log.debug("grant data = %s " % grant_data)
        
        content = grant_data 
        if not grant_data.has_key('error'): 
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
            access_ranges = list(AccessRange.objects.filter(key__in=[grant_data['scope']]))
            access_token.scope = access_ranges
            # alternative to the above
            # access_token.scope.add(*req.scope.all())
            access_token.save() 
        
            # Update the state 
            req.refresh_token = grant_data['refresh_token'] 
            req.token = grant_data['access_token'] 
            req.save() 
            log.debug("access token = %s " % vars(access_token))
        
            # Clean up 
            code.delete() 
            log.debug("Deleted code") 

        # wrap if necessary...
        try: 
            callback=request.GET.get('callback')
            json_data = "%s(%s);" % (callback, json.dumps(content))
        except: 
            json_data = json.dumps(content)

        # => Send the response back 
        log.debug("Response = %s " % json_data) 
        response = HttpResponse(json_data, 
                                content_type="application/json")
        return response         
    except:
        traceback.print_exc() 
        pass
    


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
    
    log.debug("in refresh_token")

    if request.method != "GET": 
        return HttpResponseRedirect("/")
    
    # Obtain and lookup a refresh token 
    refresh_token_key = request.GET.get('refresh_token')
    try: 
        token = AccessToken.objects.get(refresh_token=refresh_token_key) 
        req = OauthRequest.objects.get(refresh_token=refresh_token_key) 
        client = req.client
    
        # Start constructing the request that must be sent to the resource
        # server.
        params = {} 
        params['client_id'] = settings.RESOURCE_CLIENT_KEY         
        params['grant_type'] = 'refresh_token'
        params['refresh_token'] = token.refresh_token 
        
        # Dont need to specify the redirect_uri as we dont need a call
        # back from the server. Just the json response is enough.
        params['redirect_uri'] = \
            "http://%s/client/request/%s" % (request.get_host(), req.key)
        
        # => set the scope of the refresh. Not sure why scope is required
        # again because it has been specific while obtaining the
        # authorization. The scope cant be any different. 
        log.debug("type req.scope.all() = %s " % type(req.scope.all()))
        all_keys = [s.key for s in req.scope.all()]
        log.debug("all_scopes = %s " % all_keys)
        if len(all_keys) > 0: 
            params['scope'] = all_keys[0]
        else:
            params['scope'] = ""
        
        # => params to ready 
        log.debug("params = %s " % params)
    
        # Obtain the authentication 
        basic_auth = get_auth() 
        headers = { 'Authorization': basic_auth } 
        log.debug("headers = %s " %  headers)
        
        # Constructing the call 
        url = settings.ACCESS_TOKEN_URL + "/?" + urlencode(params)
        log.debug("url = %s " % url)
        
        # Call the server 
        r = requests.post(url, data="", headers=headers)
        log.debug("received headers = %s " % r.headers)
        if r.headers['content-type'] != 'application/json':
            # Should probably delete the token 
            log.error("Received error from server %s" % r.content)
            raise Exception("Possible error in request to the server")
        
        # => Now store the token for future access purposes 
        grant_data = json.loads(r.content)
        log.debug("grant data = %s " % grant_data)
    
        if grant_data.has_key('error'):
            # Dont change anything
            content = grant_data 
        else: 
            # => Update the token state 
            token.token = grant_data['access_token']
            token.refresh_token = grant_data['refresh_token']
            now =  TimestampGenerator()()
            token.expire =now + int(grant_data['expire_in'])
            token.save() 
            
            # Update the request state 
            req.token = grant_data['access_token']
            req.refresh_token = grant_data['refresh_token']
            req.save() 
            
            # response 
            content = {'refresh_token': req.refresh_token, 'token': req.token}
            
        # wrap if necessary...
        try: 
            callback=request.GET.get('callback')
            json_data = "%s(%s);" % (callback, json.dumps(content))
        except: 
            json_data = json.dumps(content)

        # XXX May be this should be the response instead
        #next = "/client/%s" % client.key
        #log.debug("Redirecting to %s " % next)
        #return HttpResponseRedirect(next)
            
        # => Send the response back 
        log.debug("Response = %s " % json_data) 
        response = HttpResponse(json_data, 
                                content_type="application/json")
        return response 
    
    except: 
        traceback.print_exc() 
        raise Exception("Invalid refresh token") 

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
    
    log.debug("request parameters = %s " % request.GET)
    
    # Figure out if this request is aadhaar 
    try: 
        aadhaar = False
        aadhaar_str = request.GET.get('aadhaar')
        if aadhaar_str == "True":
            aadhaar = True
    except:
        pass
    
    log.debug("aadhaar = %s %s " % (aadhaar, type(aadhaar)))

    # Some dummy client. It does not matter. 
    # XXX change this if you need to support multiple clients. 
    client = Client.objects.all()[:1][0]
    if client == None: 
        raise Exception("Could not find a suitable client") 

    user = request.user 
    scope_key = request.GET.get('scope')
    log.debug("scope key = %s %s " % (scope_key, type(scope_key)))
    if ((scope_key is not None) and (scope_key != "None")):
        access_ranges = list(AccessRange.objects.filter(key__in=[scope_key]))
    else:
        access_ranges = []

    log.debug("access_ranges = %s " % access_ranges)
    log.debug([r.key for r in access_ranges])
    response_type = 'code'
    
    # Now create the request. 
    req = OauthRequest.objects.create(client=client,
                                      user=user, 
                                      #aadhaar=aadhaar,
                                      response_type=response_type)
    req.scope = access_ranges
    req.save() 
    
    log.debug("created request object %s with key %s " % (req, req.key))

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
    log.debug("Updated parameters = %s " % params)
    log.debug("Redirecting to %s " % next)
    return HttpResponseRedirect(next) 
