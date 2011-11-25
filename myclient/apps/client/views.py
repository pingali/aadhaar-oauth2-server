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

@login_required 
def client(request, client_id):
    
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

# this receives the post from the oauth2 server 
def request(request, req_id):
    
    print "In apps.client.views.request - entered" 
    req = OauthRequest.objects.get(key=req_id)
    print "Found request = ", vars(req)
    try: 
        # XXX This URL should embed localstate information
        # to be able to extract all relevant information. 
        # The form should first post to the local server 
        # which stores the request and redirects it to the 
        # remote server. 
        code_key = request.GET.get('code')
        print "Received code = ", code_key
        
        #=> Check if it exists 
        try: 
            code = Code.objects.get(key=code_key)
        except:
            code = None
            pass
        
        if code is not None: 
            # Giving token refresh request triggers a callback to this
            # looks like (based on the redirect_uri specified") 
            raise Exception("Duplicate code returned") 
        
        # expire is set automatically 
        code = Code.objects.create(user=req.user, 
                                   client=req.client,
                                   redirect_uri=request.path, 
                                   key=code_key)
        print "code's scope = ", code.scope.all()
        print "req's scope = ", req.scope.all()
        code.scope.add(*req.scope.all())
        code.save() 
        print "saved code = ", vars(code) 
        print "code scope = ", code.scope 
        req.completed = TimestampGenerator()() 
        req.code = code_key # we dont store code object because it
                            # will be deleted
        req.save()
        print "saved request = ", vars(req) 

    except:
        traceback.print_exc() 
        pass
    
    client = Client.objects.all()[:1][0]

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

    print "Trying to obtain a token" 

    client = Client.objects.all()[:1][0] 
    print "Client = ", vars(client) 
    
    if request.method != "GET": 
        return HttpResponseRedirect("/")
    
    try:

        params = {} 
        params['code'] = request.GET.get('code')
        
        # Obtain the state objects
        code = Code.objects.get(key=params['code'])
        req = OauthRequest.objects.get(code=params['code'])

        params['client_id'] = settings.RESOURCE_CLIENT_KEY         
        params['grant_type'] = 'authorization_code'         
        #params['redirect_uri'] = settings.CLIENT_SITE + code.redirect_uri
        
        # set the scope 
        print "type req.scope.all() = ", type(req.scope.all())
        all_keys = [s.key for s in req.scope.all()]
        print "all_scopes = ", all_keys
        if len(all_keys) > 0: 
            params['scope'] = all_keys[0]
        else:
            params['scope'] = ""

        print "Found code = ", vars(code) 
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

        # Call 
        r = requests.post(url, data="", headers=headers)
        print "received headers = ", r.headers 
        if r.headers['content-type'] != 'application/json':
            raise Exception("Possible error in request to the server")
        
        #=> Now store the token for future access purposes 
        grant_data = json.loads(r.content)
        print "grant data = ", grant_data
        
        access_token = \
            AccessToken.objects.create(user=request.user, 
                                       client=client, 
                                       refresh_token=grant_data['refresh_token'],
                                       # token_type=gr['token_type'],
                                       # scope=grant_data['scope'],
                                       token=grant_data['access_token'])
        access_ranges = list(AccessRange.objects.filter(key__in=grant_data['scope']))
        access_token.scope = access_ranges
        access_token.save() 
        
        req.refresh_token = grant_data['refresh_token'] 
        req.token = grant_data['access_token'] 
        req.save() 
        print "access token = ", vars(access_token) 
        
        # Dont delete the 
        #code.delete() 
        
    except:
        traceback.print_exc() 
        pass
    
    # redirect 
    HttpResponseRedirect(settings.CLIENT_SITE + "/client/%s" % client.key)

@login_required 
@csrf_exempt
def refresh_token(request): 

	#<form method="post" action="http://localhost:8000/oauth2/token" class="authenticate">
        #<input type="hidden" name="grant_type" value="refresh_token" />
        #<input type="hidden" name="refresh_token" value="38d6122e30" />
        #<input type="hidden" name="client_id" value="d53d90894c157ab" />
        #<input type="hidden" name="scope" value="" />
        #<input type="submit" value="38d6122e30"/>
        #</form>

    if request.method != "GET": 
        return HttpResponseRedirect("/")
    
    refresh_token_key = request.GET.get('refresh_token')
    try: 
        token = AccessToken.objects.get(refresh_token=refresh_token_key) 
        req = OauthRequest.objects.get(refresh_token=refresh_token_key) 
    except: 
        traceback.print_exc() 
        raise Exception("Invalid refresh token") 

    params = {} 
    params['client_id'] = settings.RESOURCE_CLIENT_KEY         
    params['grant_type'] = 'refresh_token'
    params['refresh_token'] = token.refresh_token 
    #params['redirect_uri'] = \
    #    "http://%s/client/request/%s" % (request.get_host(), req.key)

    print "type req.scope.all() = ", type(req.scope.all())
    all_keys = [s.key for s in req.scope.all()]
    print "all_scopes = ", all_keys
    if len(all_keys) > 0: 
        params['scope'] = all_keys[0]
    else:
        params['scope'] = ""
        
    print "params = ", params 

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

    # Call 
    r = requests.post(url, data="", headers=headers)
    print "received headers = ", r.headers 
    if r.headers['content-type'] != 'application/json':
        raise Exception("Possible error in request to the server")
        
    # => Now store the token for future access purposes 
    grant_data = json.loads(r.content)
    print "grant data = ", grant_data
    
    token.token = grant_data['access_token']
    token.refresh_token = grant_data['refresh_token']
    token.save() 

    req.token = grant_data['access_token']
    req.refresh_token = grant_data['refresh_token']
    req.save() 
    
    
    

@login_required 
def forward(request): 
    
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

    # Some dummy client. It doesnt matter. 
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

    #params = request.GET.copy()
    params = {} 
    params['response_type'] = 'code'
    params['client_id'] = settings.RESOURCE_CLIENT_KEY 
    
    if scope_key is not None: 
        params['scope'] = scope_key 

    req = OauthRequest.objects.create(client=client,
                                      user=user, 
                                      #aadhaar=aadhaar,
                                      response_type=params['response_type'])

    req.scope = access_ranges
    req.save() 
    print "created request object ", req, "with key ", req.key 

    # Now key is available. So update the URL
    params['redirect_uri'] = "http://%s/client/request/%s" % (request.get_host(), req.key)
    url = urlencode(params)
    print "Updated parameters = ", params 
    
    if aadhaar: 
        print "aadhaar enabled link" 
        next = "%s?%s" % (settings.AADHAAR_AUTHORIZE_URL, url)
    else:
        print "normal link" 
        next = "%s?%s" % (settings.AUTHORIZE_URL, url)

    print "redirecting the request to ", next 
    return HttpResponseRedirect(next) 
